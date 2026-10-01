from sqlalchemy import or_
from sqlalchemy.orm import Session

from models.device_model import Device


class DeviceRepository:

    @staticmethod
    def get_by_id(
        db: Session,
        device_id: int
    ) -> Device | None:

        return (
            db.query(Device)
            .filter(Device.id == device_id)
            .first()
        )

    @staticmethod
    def get_by_imei(
        db: Session,
        imei: str
    ) -> Device | None:

        return (
            db.query(Device)
            .filter(Device.imei == imei)
            .first()
        )

    @staticmethod
    def create(
        db: Session,
        device: Device
    ) -> Device:

        db.add(device)
        db.commit()
        db.refresh(device)

        return device

    @staticmethod
    def update(
        db: Session,
        device: Device
    ) -> Device:

        db.commit()
        db.refresh(device)

        return device

    @staticmethod
    def search(
        db: Session,
        search: str | None = None,
        manufacturer: str | None = None,
        device_type: str | None = None,
        device_status: str | None = None,
        customer_id: int | None = None
    ):

        query = db.query(Device)

        if search:

            search_value = f"%{search}%"

            query = query.filter(
                or_(
                    Device.imei.ilike(search_value),
                    Device.device_model.ilike(search_value),
                    Device.manufacturer.ilike(search_value)
                )
            )

        if manufacturer:
            query = query.filter(
                Device.manufacturer == manufacturer
            )

        if device_type:
            query = query.filter(
                Device.device_type == device_type
            )

        if device_status:
            query = query.filter(
                Device.status == device_status
            )

        if customer_id:
            query = query.filter(
                Device.customer_id == customer_id
            )

        return (
            query
            .order_by(Device.id.desc())
            .all()
        )