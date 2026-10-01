from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy.orm import Session

from models.network_equipment_model import (
    NetworkEquipment
)

from repositories.network_equipment_repository import (
    NetworkEquipmentRepository
)

from repositories.network_tower_repository import (
    NetworkTowerRepository
)


class NetworkEquipmentService:

    ALLOWED_TYPES = {
        "Router",
        "Switch",
        "Base Station",
        "Network Device"
    }

    ALLOWED_HEALTH_STATUS = {
        "Healthy",
        "Warning",
        "Critical"
    }

    ALLOWED_NETWORK_STATUS = {
        "Online",
        "Offline",
        "Maintenance"
    }

    @staticmethod
    def validate_equipment_type(
        equipment_type: str
    ):

        if equipment_type not in (
            NetworkEquipmentService.ALLOWED_TYPES
        ):

            raise HTTPException(
                status_code=400,
                detail=(
                    "Invalid equipment type. "
                    "Allowed values: Router, Switch, "
                    "Base Station, Network Device"
                )
            )

    @staticmethod
    def validate_health_status(
        health_status: str
    ):

        if health_status not in (
            NetworkEquipmentService
            .ALLOWED_HEALTH_STATUS
        ):

            raise HTTPException(
                status_code=400,
                detail=(
                    "Invalid health status. "
                    "Allowed values: Healthy, "
                    "Warning, Critical"
                )
            )

    @staticmethod
    def validate_network_status(
        network_status: str
    ):

        if network_status not in (
            NetworkEquipmentService
            .ALLOWED_NETWORK_STATUS
        ):

            raise HTTPException(
                status_code=400,
                detail=(
                    "Invalid network status. "
                    "Allowed values: Online, "
                    "Offline, Maintenance"
                )
            )

    @staticmethod
    def calculate_health(
        cpu_usage: float,
        memory_usage: float
    ):

        if (
            cpu_usage >= 90
            or memory_usage >= 90
        ):
            return "Critical"

        if (
            cpu_usage >= 70
            or memory_usage >= 70
        ):
            return "Warning"

        return "Healthy"

    @staticmethod
    def validate_tower(
        db: Session,
        tower_id: int | None
    ):

        if tower_id is None:
            return None

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

        if tower.status == "Decommissioned":

            raise HTTPException(
                status_code=400,
                detail=(
                    "Equipment cannot be installed "
                    "on a decommissioned tower"
                )
            )

        return tower

    @staticmethod
    def create_equipment(
        db: Session,
        equipment_code: str,
        equipment_name: str,
        equipment_type: str,
        manufacturer: str,
        model_number: str,
        tower_id: int | None,
        installation_date,
        maintenance_schedule: str | None,
        notes: str | None
    ):

        NetworkEquipmentService.validate_equipment_type(
            equipment_type
        )

        existing = (
            NetworkEquipmentRepository.get_by_code(
                db,
                equipment_code
            )
        )

        if existing:

            raise HTTPException(
                status_code=409,
                detail="Equipment code already exists"
            )

        NetworkEquipmentService.validate_tower(
            db,
            tower_id
        )

        now = datetime.now(timezone.utc)

        equipment = NetworkEquipment(
            equipment_code=equipment_code.upper(),
            equipment_name=equipment_name,
            equipment_type=equipment_type,
            manufacturer=manufacturer,
            model_number=model_number,
            tower_id=tower_id,
            installation_date=installation_date,
            maintenance_schedule=maintenance_schedule,
            health_status="Healthy",
            cpu_usage=0,
            memory_usage=0,
            network_status="Online",
            last_heartbeat=now,
            downtime_minutes=0,
            notes=notes
        )

        return NetworkEquipmentRepository.create(
            db,
            equipment
        )

    @staticmethod
    def get_equipment(
        db: Session,
        equipment_id: int
    ):

        equipment = (
            NetworkEquipmentRepository.get_by_id(
                db,
                equipment_id
            )
        )

        if not equipment:

            raise HTTPException(
                status_code=404,
                detail="Network equipment not found"
            )

        return equipment

    @staticmethod
    def update_equipment(
        db: Session,
        equipment_id: int,
        data
    ):

        equipment = NetworkEquipmentService.get_equipment(
            db,
            equipment_id
        )

        if data.equipment_name is not None:

            equipment.equipment_name = (
                data.equipment_name
            )

        if data.manufacturer is not None:

            equipment.manufacturer = (
                data.manufacturer
            )

        if data.model_number is not None:

            equipment.model_number = (
                data.model_number
            )

        if data.tower_id is not None:

            NetworkEquipmentService.validate_tower(
                db,
                data.tower_id
            )

            equipment.tower_id = data.tower_id

        if data.installation_date is not None:

            equipment.installation_date = (
                data.installation_date
            )

        if data.maintenance_schedule is not None:

            equipment.maintenance_schedule = (
                data.maintenance_schedule
            )

        if data.notes is not None:

            equipment.notes = data.notes

        return NetworkEquipmentRepository.update(
            db,
            equipment
        )

    @staticmethod
    def update_metrics(
        db: Session,
        equipment_id: int,
        cpu_usage: float,
        memory_usage: float,
        network_status: str,
        last_heartbeat
    ):

        equipment = NetworkEquipmentService.get_equipment(
            db,
            equipment_id
        )

        NetworkEquipmentService.validate_network_status(
            network_status
        )

        equipment.cpu_usage = cpu_usage
        equipment.memory_usage = memory_usage
        equipment.network_status = network_status

        if last_heartbeat is None:

            last_heartbeat = datetime.now(
                timezone.utc
            )

        equipment.last_heartbeat = last_heartbeat

        equipment.health_status = (
            NetworkEquipmentService.calculate_health(
                cpu_usage,
                memory_usage
            )
        )

        return NetworkEquipmentRepository.update(
            db,
            equipment
        )

    @staticmethod
    def update_health(
        db: Session,
        equipment_id: int,
        health_status: str
    ):

        NetworkEquipmentService.validate_health_status(
            health_status
        )

        equipment = NetworkEquipmentService.get_equipment(
            db,
            equipment_id
        )

        equipment.health_status = health_status

        return NetworkEquipmentRepository.update(
            db,
            equipment
        )

    @staticmethod
    def calculate_downtime(
        db: Session,
        equipment_id: int
    ):

        equipment = NetworkEquipmentService.get_equipment(
            db,
            equipment_id
        )

        if not equipment.last_heartbeat:

            return {
                "equipment_id": equipment.id,
                "network_status": equipment.network_status,
                "last_heartbeat": None,
                "downtime_minutes": 0
            }

        now = datetime.now(timezone.utc)

        last_heartbeat = equipment.last_heartbeat

        if last_heartbeat.tzinfo is None:

            last_heartbeat = last_heartbeat.replace(
                tzinfo=timezone.utc
            )

        downtime = (
            now - last_heartbeat
        ).total_seconds() / 60

        if equipment.network_status == "Online":

            downtime = 0

        return {
            "equipment_id": equipment.id,
            "equipment_code": equipment.equipment_code,
            "network_status": equipment.network_status,
            "last_heartbeat": equipment.last_heartbeat,
            "downtime_minutes": round(
                max(downtime, 0),
                2
            )
        }

    @staticmethod
    def search_equipment(
        db: Session,
        search: str | None = None,
        equipment_type: str | None = None,
        health_status: str | None = None,
        network_status: str | None = None,
        tower_id: int | None = None
    ):

        if equipment_type:

            NetworkEquipmentService.validate_equipment_type(
                equipment_type
            )

        if health_status:

            NetworkEquipmentService.validate_health_status(
                health_status
            )

        if network_status:

            NetworkEquipmentService.validate_network_status(
                network_status
            )

        return NetworkEquipmentRepository.search(
            db=db,
            search=search,
            equipment_type=equipment_type,
            health_status=health_status,
            network_status=network_status,
            tower_id=tower_id
        )