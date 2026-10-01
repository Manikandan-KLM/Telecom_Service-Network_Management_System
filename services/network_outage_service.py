from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy.orm import Session

from models.network_outage_model import NetworkOutage

from repositories.network_outage_repository import (
    NetworkOutageRepository
)

from repositories.outage_tower_repository import (
    OutageTowerRepository
)

from repositories.outage_customer_repository import (
    OutageCustomerRepository
)

from repositories.tower_customer_mapping_repository import (
    TowerCustomerMappingRepository
)

from repositories.network_tower_repository import (
    NetworkTowerRepository
)


class NetworkOutageService:

    OUTAGE_TYPES = {
        "Power Failure",
        "Equipment Failure",
        "Network Failure",
        "Fiber Cut",
        "Hardware Failure",
        "Software Failure",
        "Maintenance",
        "Other"
    }

    SEVERITIES = {
        "Low",
        "Medium",
        "High",
        "Critical"
    }

    STATUSES = {
        "Open",
        "Investigating",
        "Resolved",
        "Closed"
    }

    @staticmethod
    def validate_outage_type(
        outage_type: str
    ):

        if outage_type not in NetworkOutageService.OUTAGE_TYPES:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Invalid outage type. "
                    f"Allowed: {', '.join(NetworkOutageService.OUTAGE_TYPES)}"
                )
            )

    @staticmethod
    def validate_severity(
        severity: str
    ):

        if severity not in NetworkOutageService.SEVERITIES:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Invalid severity. "
                    f"Allowed: {', '.join(NetworkOutageService.SEVERITIES)}"
                )
            )

    @staticmethod
    def validate_status(
        status: str
    ):

        if status not in NetworkOutageService.STATUSES:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Invalid status. "
                    f"Allowed: {', '.join(NetworkOutageService.STATUSES)}"
                )
            )

    @staticmethod
    def validate_towers(
        db: Session,
        tower_ids: list[int]
    ):

        for tower_id in tower_ids:

            tower = NetworkTowerRepository.get_by_id(
                db,
                tower_id
            )

            if not tower:
                raise HTTPException(
                    status_code=404,
                    detail=f"Tower {tower_id} not found"
                )

    @staticmethod
    def create_outage(
        db: Session,
        outage_code: str,
        outage_type: str,
        severity: str,
        description: str | None,
        start_time: datetime,
        expected_resolution: datetime | None,
        tower_ids: list[int],
        created_by: int
    ):

        NetworkOutageService.validate_outage_type(
            outage_type
        )

        NetworkOutageService.validate_severity(
            severity
        )

        if not tower_ids:
            raise HTTPException(
                status_code=400,
                detail="At least one affected tower is required"
            )

        tower_ids = list(set(tower_ids))

        NetworkOutageService.validate_towers(
            db,
            tower_ids
        )

        existing = NetworkOutageRepository.get_by_code(
            db,
            outage_code.upper()
        )

        if existing:
            raise HTTPException(
                status_code=409,
                detail="Outage code already exists"
            )

        if (
            expected_resolution
            and expected_resolution < start_time
        ):
            raise HTTPException(
                status_code=400,
                detail=(
                    "Expected resolution cannot be "
                    "before start time"
                )
            )

        outage = NetworkOutage(
            outage_code=outage_code.upper(),
            outage_type=outage_type,
            severity=severity,
            description=description,
            start_time=start_time,
            expected_resolution=expected_resolution,
            status="Open",
            created_by=created_by
        )

        db.add(outage)
        db.flush()

        # -----------------------------------------
        # Save affected towers
        # -----------------------------------------

        for tower_id in tower_ids:

            OutageTowerRepository.create(
                db,
                outage.id,
                tower_id
            )

        # -----------------------------------------
        # Automatically find affected customers
        # -----------------------------------------

        customer_ids = (
            TowerCustomerMappingRepository
            .get_customer_ids_by_towers(
                db,
                tower_ids
            )
        )

        # -----------------------------------------
        # Save affected customers
        # -----------------------------------------

        for customer_id in customer_ids:

            OutageCustomerRepository.create(
                db,
                outage.id,
                customer_id
            )

        db.commit()
        db.refresh(outage)

        return outage

    @staticmethod
    def update_outage(
        db: Session,
        outage_id: int,
        outage_type: str | None = None,
        severity: str | None = None,
        description: str | None = None,
        expected_resolution: datetime | None = None,
        actual_resolution: datetime | None = None,
        status: str | None = None
    ):

        outage = NetworkOutageRepository.get_by_id(
            db,
            outage_id
        )

        if not outage:
            raise HTTPException(
                status_code=404,
                detail="Outage not found"
            )

        if outage_type:

            NetworkOutageService.validate_outage_type(
                outage_type
            )

            outage.outage_type = outage_type

        if severity:

            NetworkOutageService.validate_severity(
                severity
            )

            outage.severity = severity

        if status:

            NetworkOutageService.validate_status(
                status
            )

            outage.status = status

        if description is not None:
            outage.description = description

        if expected_resolution:

            if expected_resolution < outage.start_time:

                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Expected resolution cannot be "
                        "before start time"
                    )
                )

            outage.expected_resolution = expected_resolution

        if actual_resolution:

            if actual_resolution < outage.start_time:

                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Actual resolution cannot be "
                        "before start time"
                    )
                )

            outage.actual_resolution = actual_resolution

            if not status:
                outage.status = "Resolved"

        return NetworkOutageRepository.update(
            db,
            outage
        )

    @staticmethod
    def get_affected_data(
        db: Session,
        outage_id: int
    ):

        outage = NetworkOutageRepository.get_by_id(
            db,
            outage_id
        )

        if not outage:
            raise HTTPException(
                status_code=404,
                detail="Outage not found"
            )

        tower_ids = OutageTowerRepository.get_tower_ids(
            db,
            outage_id
        )

        customer_ids = (
            OutageCustomerRepository.get_customer_ids(
                db,
                outage_id
            )
        )

        return {
            "outage_id": outage.id,
            "outage_code": outage.outage_code,
            "affected_tower_ids": tower_ids,
            "affected_customer_ids": customer_ids,
            "affected_tower_count": len(tower_ids),
            "affected_customer_count": len(customer_ids)
        }

    @staticmethod
    def get_outage(
        db: Session,
        outage_id: int
    ):

        outage = NetworkOutageRepository.get_by_id(
            db,
            outage_id
        )

        if not outage:
            raise HTTPException(
                status_code=404,
                detail="Outage not found"
            )

        return outage

    @staticmethod
    def get_all_outages(
        db: Session,
        severity: str | None = None,
        status: str | None = None,
        outage_type: str | None = None
    ):

        return NetworkOutageRepository.get_all(
            db,
            severity=severity,
            status=status,
            outage_type=outage_type
        )