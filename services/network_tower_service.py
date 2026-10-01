from fastapi import HTTPException
from sqlalchemy.orm import Session

from models.network_tower_model import NetworkTower

from repositories.network_tower_repository import (
    NetworkTowerRepository
)


class NetworkTowerService:

    ALLOWED_TOWER_TYPES = {
        "Macro",
        "Micro",
        "Small Cell",
        "Indoor",
        "Outdoor"
    }

    ALLOWED_STATUSES = {
        "Active",
        "Maintenance",
        "Offline",
        "Decommissioned"
    }

    @staticmethod
    def validate_tower_type(
        tower_type: str
    ):

        if tower_type not in (
            NetworkTowerService.ALLOWED_TOWER_TYPES
        ):

            raise HTTPException(
                status_code=400,
                detail=(
                    "Invalid tower type. "
                    "Allowed values: "
                    "Macro, Micro, Small Cell, "
                    "Indoor, Outdoor"
                )
            )

    @staticmethod
    def validate_status(
        status: str
    ):

        if status not in (
            NetworkTowerService.ALLOWED_STATUSES
        ):

            raise HTTPException(
                status_code=400,
                detail=(
                    "Invalid tower status. "
                    "Allowed values: "
                    "Active, Maintenance, "
                    "Offline, Decommissioned"
                )
            )

    @staticmethod
    def create_tower(
        db: Session,
        tower_number: str,
        tower_name: str,
        tower_type: str,
        latitude: float,
        longitude: float,
        coverage_area: float,
        capacity: int
    ):

        NetworkTowerService.validate_tower_type(
            tower_type
        )

        existing_tower = (
            NetworkTowerRepository.get_by_number(
                db,
                tower_number
            )
        )

        if existing_tower:

            raise HTTPException(
                status_code=409,
                detail="Tower number already exists"
            )

        tower = NetworkTower(
            tower_number=tower_number.upper(),
            tower_name=tower_name,
            tower_type=tower_type,
            latitude=latitude,
            longitude=longitude,
            coverage_area=coverage_area,
            capacity=capacity,
            status="Active",
            is_active=True
        )

        return NetworkTowerRepository.create(
            db,
            tower
        )

    @staticmethod
    def get_tower(
        db: Session,
        tower_id: int
    ):

        tower = (
            NetworkTowerRepository.get_by_id(
                db,
                tower_id
            )
        )

        if not tower:

            raise HTTPException(
                status_code=404,
                detail="Network tower not found"
            )

        return tower

    @staticmethod
    def update_tower(
        db: Session,
        tower_id: int,
        data
    ):

        tower = NetworkTowerService.get_tower(
            db,
            tower_id
        )

        if data.tower_type is not None:

            NetworkTowerService.validate_tower_type(
                data.tower_type
            )

            tower.tower_type = data.tower_type

        if data.tower_name is not None:
            tower.tower_name = data.tower_name

        if data.latitude is not None:
            tower.latitude = data.latitude

        if data.longitude is not None:
            tower.longitude = data.longitude

        if data.coverage_area is not None:
            tower.coverage_area = data.coverage_area

        if data.capacity is not None:
            tower.capacity = data.capacity

        return NetworkTowerRepository.update(
            db,
            tower
        )

    @staticmethod
    def update_status(
        db: Session,
        tower_id: int,
        new_status: str
    ):

        NetworkTowerService.validate_status(
            new_status
        )

        tower = NetworkTowerService.get_tower(
            db,
            tower_id
        )

        tower.status = new_status

        if new_status == "Active":

            tower.is_active = True

        elif new_status == "Decommissioned":

            tower.is_active = False

        else:

            tower.is_active = True

        return NetworkTowerRepository.update(
            db,
            tower
        )

    @staticmethod
    def delete_tower(
        db: Session,
        tower_id: int
    ):

        tower = NetworkTowerService.get_tower(
            db,
            tower_id
        )

        if tower.status != "Decommissioned":

            raise HTTPException(
                status_code=400,
                detail=(
                    "Only a Decommissioned tower "
                    "can be removed"
                )
            )

        tower.is_active = False

        return NetworkTowerRepository.update(
            db,
            tower
        )

    @staticmethod
    def search_towers(
        db: Session,
        search: str | None = None,
        tower_type: str | None = None,
        tower_status: str | None = None
    ):

        if tower_type:

            NetworkTowerService.validate_tower_type(
                tower_type
            )

        if tower_status:

            NetworkTowerService.validate_status(
                tower_status
            )

        return NetworkTowerRepository.search(
            db=db,
            search=search,
            tower_type=tower_type,
            tower_status=tower_status
        )