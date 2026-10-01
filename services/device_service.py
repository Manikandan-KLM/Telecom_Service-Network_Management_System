from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.device_model import Device
from models.device_sim_mapping_model import (
    DeviceSIMMapping
)

from repositories.device_repository import (
    DeviceRepository
)

from repositories.device_sim_mapping_repository import (
    DeviceSIMMappingRepository
)

from repositories.customer_repository import (
    CustomerRepository
)

from repositories.sim_card_repository import (
    SIMCardRepository
)


class DeviceService:

    ALLOWED_DEVICE_TYPES = {
        "Smartphone",
        "Tablet",
        "Feature Phone",
        "Router",
        "Modem",
        "IoT Device"
    }

    ALLOWED_STATUSES = {
        "Available",
        "Active",
        "Inactive",
        "Lost",
        "Blocked",
        "Damaged"
    }

    # --------------------------------------------------
    # VALIDATE DEVICE TYPE
    # --------------------------------------------------

    @staticmethod
    def validate_device_type(
        device_type: str
    ):

        if device_type not in DeviceService.ALLOWED_DEVICE_TYPES:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Invalid device type. "
                    "Allowed values: "
                    "Smartphone, Tablet, Feature Phone, "
                    "Router, Modem, IoT Device"
                )
            )

    # --------------------------------------------------
    # VALIDATE DEVICE STATUS
    # --------------------------------------------------

    @staticmethod
    def validate_status(
        device_status: str
    ):

        if device_status not in DeviceService.ALLOWED_STATUSES:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Invalid device status. "
                    "Allowed values: "
                    "Available, Active, Inactive, "
                    "Lost, Blocked, Damaged"
                )
            )

    # --------------------------------------------------
    # VALIDATE CUSTOMER
    # --------------------------------------------------

    @staticmethod
    def validate_customer(
        db: Session,
        customer_id: int | None
    ):

        if customer_id is None:
            return None

        customer = CustomerRepository.get_by_id(
            db,
            customer_id
        )

        if not customer:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )

        if not customer.is_active:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Customer account is inactive"
            )

        return customer

    # --------------------------------------------------
    # VALIDATE SIM
    # --------------------------------------------------

    @staticmethod
    def validate_sim(
        db: Session,
        sim_id: int
    ):

        sim = SIMCardRepository.get_by_id(
            db,
            sim_id
        )

        if not sim:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="SIM card not found"
            )

        if sim.status != "Active":

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Only an Active SIM can be "
                    "assigned to a device"
                )
            )

        if not sim.customer_id:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "SIM must be mapped to a customer "
                    "before device assignment"
                )
            )

        return sim

    # --------------------------------------------------
    # CREATE DEVICE
    # --------------------------------------------------

    @staticmethod
    def create_device(
        db: Session,
        imei: str,
        device_model: str,
        manufacturer: str,
        device_type: str,
        customer_id: int | None
    ):

        DeviceService.validate_device_type(
            device_type
        )

        # Duplicate IMEI prevention
        existing_device = DeviceRepository.get_by_imei(
            db,
            imei
        )

        if existing_device:

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="IMEI already registered"
            )

        # Customer validation
        DeviceService.validate_customer(
            db,
            customer_id
        )

        device = Device(
            imei=imei,
            device_model=device_model,
            manufacturer=manufacturer,
            device_type=device_type,
            status="Available",
            customer_id=customer_id,
            is_active=True
        )

        return DeviceRepository.create(
            db,
            device
        )

    # --------------------------------------------------
    # GET DEVICE
    # --------------------------------------------------

    @staticmethod
    def get_device(
        db: Session,
        device_id: int
    ):

        device = DeviceRepository.get_by_id(
            db,
            device_id
        )

        if not device:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Device not found"
            )

        return device

    # --------------------------------------------------
    # UPDATE DEVICE
    # --------------------------------------------------

    @staticmethod
    def update_device(
        db: Session,
        device_id: int,
        device_model: str | None,
        manufacturer: str | None,
        device_type: str | None,
        customer_id: int | None
    ):

        device = DeviceService.get_device(
            db,
            device_id
        )

        if device_model is not None:
            device.device_model = device_model

        if manufacturer is not None:
            device.manufacturer = manufacturer

        if device_type is not None:

            DeviceService.validate_device_type(
                device_type
            )

            device.device_type = device_type

        if customer_id is not None:

            DeviceService.validate_customer(
                db,
                customer_id
            )

            device.customer_id = customer_id

        return DeviceRepository.update(
            db,
            device
        )

    # --------------------------------------------------
    # CHANGE DEVICE STATUS
    # --------------------------------------------------

    @staticmethod
    def update_status(
        db: Session,
        device_id: int,
        new_status: str
    ):

        DeviceService.validate_status(
            new_status
        )

        device = DeviceService.get_device(
            db,
            device_id
        )

        if new_status == "Active":

            if not device.customer_id:

                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        "Device must be mapped to a "
                        "customer before activation"
                    )
                )

        device.status = new_status

        device.is_active = (
            new_status == "Active"
        )

        return DeviceRepository.update(
            db,
            device
        )

    # --------------------------------------------------
    # SEARCH DEVICES
    # --------------------------------------------------

    @staticmethod
    def search_devices(
        db: Session,
        search: str | None = None,
        manufacturer: str | None = None,
        device_type: str | None = None,
        device_status: str | None = None,
        customer_id: int | None = None
    ):

        if device_type:

            DeviceService.validate_device_type(
                device_type
            )

        if device_status:

            DeviceService.validate_status(
                device_status
            )

        return DeviceRepository.search(
            db=db,
            search=search,
            manufacturer=manufacturer,
            device_type=device_type,
            device_status=device_status,
            customer_id=customer_id
        )

    # --------------------------------------------------
    # ASSIGN SIM TO DEVICE
    # --------------------------------------------------

    @staticmethod
    def assign_sim(
        db: Session,
        device_id: int,
        sim_id: int
    ):

        device = DeviceService.get_device(
            db,
            device_id
        )

        if not device.is_active:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Inactive device cannot receive "
                    "a SIM assignment"
                )
            )

        # Validate SIM
        sim = DeviceService.validate_sim(
            db,
            sim_id
        )

        # Customer consistency
        if (
            device.customer_id
            and device.customer_id != sim.customer_id
        ):

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "SIM belongs to a different customer"
                )
            )

        # Prevent multiple active mappings
        active_device_mapping = (
            DeviceSIMMappingRepository
            .get_active_by_device(
                db,
                device_id
            )
        )

        if active_device_mapping:

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "Device already has an active SIM"
                )
            )

        # Prevent SIM assigned to another device
        active_sim_mapping = (
            DeviceSIMMappingRepository
            .get_active_by_sim(
                db,
                sim_id
            )
        )

        if active_sim_mapping:

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "SIM is already assigned "
                    "to another device"
                )
            )

        # If device has no customer, inherit SIM customer
        if not device.customer_id:

            device.customer_id = sim.customer_id

        mapping = DeviceSIMMapping(
            device_id=device.id,
            sim_id=sim.id,
            is_active=True
        )

        db.add(device)
        db.add(mapping)

        db.commit()

        db.refresh(device)
        db.refresh(mapping)

        return mapping

    # --------------------------------------------------
    # UNASSIGN SIM
    # --------------------------------------------------

    @staticmethod
    def unassign_sim(
        db: Session,
        device_id: int
    ):

        mapping = (
            DeviceSIMMappingRepository
            .get_active_by_device(
                db,
                device_id
            )
        )

        if not mapping:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    "No active SIM mapping found"
                )
            )

        mapping.is_active = False
        mapping.unassigned_at = datetime.now(
            timezone.utc
        )

        db.commit()
        db.refresh(mapping)

        return mapping

    # --------------------------------------------------
    # GET DEVICE SIM HISTORY
    # --------------------------------------------------

    @staticmethod
    def get_sim_history(
        db: Session,
        device_id: int
    ):

        DeviceService.get_device(
            db,
            device_id
        )

        return (
            DeviceSIMMappingRepository
            .get_by_device(
                db,
                device_id
            )
        )