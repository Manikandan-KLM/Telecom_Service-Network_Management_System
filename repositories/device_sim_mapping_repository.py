from sqlalchemy.orm import Session

from models.device_sim_mapping_model import (
    DeviceSIMMapping
)


class DeviceSIMMappingRepository:

    @staticmethod
    def get_active_by_device(
        db: Session,
        device_id: int
    ) -> DeviceSIMMapping | None:

        return (
            db.query(DeviceSIMMapping)
            .filter(
                DeviceSIMMapping.device_id == device_id,
                DeviceSIMMapping.is_active == True
            )
            .first()
        )

    @staticmethod
    def get_active_by_sim(
        db: Session,
        sim_id: int
    ) -> DeviceSIMMapping | None:

        return (
            db.query(DeviceSIMMapping)
            .filter(
                DeviceSIMMapping.sim_id == sim_id,
                DeviceSIMMapping.is_active == True
            )
            .first()
        )

    @staticmethod
    def get_by_id(
        db: Session,
        mapping_id: int
    ) -> DeviceSIMMapping | None:

        return (
            db.query(DeviceSIMMapping)
            .filter(
                DeviceSIMMapping.id == mapping_id
            )
            .first()
        )

    @staticmethod
    def create(
        db: Session,
        mapping: DeviceSIMMapping
    ) -> DeviceSIMMapping:

        db.add(mapping)
        db.commit()
        db.refresh(mapping)

        return mapping

    @staticmethod
    def update(
        db: Session,
        mapping: DeviceSIMMapping
    ) -> DeviceSIMMapping:

        db.commit()
        db.refresh(mapping)

        return mapping

    @staticmethod
    def get_by_device(
        db: Session,
        device_id: int
    ):

        return (
            db.query(DeviceSIMMapping)
            .filter(
                DeviceSIMMapping.device_id == device_id
            )
            .order_by(
                DeviceSIMMapping.assigned_at.desc()
            )
            .all()
        )