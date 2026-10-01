from sqlalchemy import or_
from sqlalchemy.orm import Session

from models.network_equipment_model import (
    NetworkEquipment
)


class NetworkEquipmentRepository:

    @staticmethod
    def get_by_id(
        db: Session,
        equipment_id: int
    ) -> NetworkEquipment | None:

        return (
            db.query(NetworkEquipment)
            .filter(
                NetworkEquipment.id == equipment_id
            )
            .first()
        )

    @staticmethod
    def get_by_code(
        db: Session,
        equipment_code: str
    ) -> NetworkEquipment | None:

        return (
            db.query(NetworkEquipment)
            .filter(
                NetworkEquipment.equipment_code
                == equipment_code
            )
            .first()
        )

    @staticmethod
    def create(
        db: Session,
        equipment: NetworkEquipment
    ) -> NetworkEquipment:

        db.add(equipment)
        db.commit()
        db.refresh(equipment)

        return equipment

    @staticmethod
    def update(
        db: Session,
        equipment: NetworkEquipment
    ) -> NetworkEquipment:

        db.commit()
        db.refresh(equipment)

        return equipment

    @staticmethod
    def search(
        db: Session,
        search: str | None = None,
        equipment_type: str | None = None,
        health_status: str | None = None,
        network_status: str | None = None,
        tower_id: int | None = None
    ):

        query = db.query(NetworkEquipment)

        if search:

            search_value = f"%{search}%"

            query = query.filter(
                or_(
                    NetworkEquipment.equipment_code.ilike(
                        search_value
                    ),
                    NetworkEquipment.equipment_name.ilike(
                        search_value
                    ),
                    NetworkEquipment.manufacturer.ilike(
                        search_value
                    ),
                    NetworkEquipment.model_number.ilike(
                        search_value
                    )
                )
            )

        if equipment_type:

            query = query.filter(
                NetworkEquipment.equipment_type
                == equipment_type
            )

        if health_status:

            query = query.filter(
                NetworkEquipment.health_status
                == health_status
            )

        if network_status:

            query = query.filter(
                NetworkEquipment.network_status
                == network_status
            )

        if tower_id is not None:

            query = query.filter(
                NetworkEquipment.tower_id
                == tower_id
            )

        return (
            query
            .order_by(NetworkEquipment.id.desc())
            .all()
        )