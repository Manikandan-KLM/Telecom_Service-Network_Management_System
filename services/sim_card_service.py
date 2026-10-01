from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.sim_card_model import SIMCard
from models.sim_replacement_history_model import (
    SIMReplacementHistory
)

from repositories.sim_card_repository import (
    SIMCardRepository
)

from repositories.sim_replacement_repository import (
    SIMReplacementRepository
)

from repositories.customer_repository import (
    CustomerRepository
)

from repositories.service_plan_repository import (
    ServicePlanRepository
)


class SIMCardService:

    ALLOWED_SIM_TYPES = {
        "Physical",
        "eSIM"
    }

    ALLOWED_STATUSES = {
        "Available",
        "Active",
        "Suspended",
        "Lost",
        "Blocked",
        "Deactivated"
    }

    @staticmethod
    def validate_sim_type(sim_type: str):

        if sim_type not in SIMCardService.ALLOWED_SIM_TYPES:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Invalid SIM type. "
                    "Allowed values: Physical, eSIM"
                )
            )

    @staticmethod
    def validate_status(sim_status: str):

        if sim_status not in SIMCardService.ALLOWED_STATUSES:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Invalid SIM status. "
                    "Allowed values: "
                    "Available, Active, Suspended, "
                    "Lost, Blocked, Deactivated"
                )
            )

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

    @staticmethod
    def validate_plan(
        db: Session,
        plan_id: int | None
    ):

        if plan_id is None:
            return None

        plan = ServicePlanRepository.get_by_id(
            db,
            plan_id
        )

        if not plan:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service plan not found"
            )

        if not plan.is_active:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Service plan is inactive"
            )

        return plan

    @staticmethod
    def create_sim(
        db: Session,
        sim_number: str,
        sim_type: str,
        customer_id: int | None,
        plan_id: int | None
    ):

        SIMCardService.validate_sim_type(
            sim_type
        )

        existing_sim = SIMCardRepository.get_by_sim_number(
            db,
            sim_number
        )

        if existing_sim:

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="SIM number already exists"
            )

        SIMCardService.validate_customer(
            db,
            customer_id
        )

        SIMCardService.validate_plan(
            db,
            plan_id
        )

        sim = SIMCard(
            sim_number=sim_number,
            sim_type=sim_type,
            status="Available",
            activation_date=None,
            customer_id=customer_id,
            plan_id=plan_id
        )

        return SIMCardRepository.create(
            db,
            sim
        )

    @staticmethod
    def get_sim(
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

        return sim

    @staticmethod
    def update_sim(
        db: Session,
        sim_id: int,
        sim_type: str | None,
        customer_id: int | None,
        plan_id: int | None
    ):

        sim = SIMCardService.get_sim(
            db,
            sim_id
        )

        if sim_type is not None:

            SIMCardService.validate_sim_type(
                sim_type
            )

            sim.sim_type = sim_type

        if customer_id is not None:

            SIMCardService.validate_customer(
                db,
                customer_id
            )

            sim.customer_id = customer_id

        if plan_id is not None:

            SIMCardService.validate_plan(
                db,
                plan_id
            )

            sim.plan_id = plan_id

        return SIMCardRepository.update(
            db,
            sim
        )

    @staticmethod
    def update_status(
        db: Session,
        sim_id: int,
        new_status: str
    ):

        SIMCardService.validate_status(
            new_status
        )

        sim = SIMCardService.get_sim(
            db,
            sim_id
        )

        if new_status == "Active":

            if not sim.customer_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        "SIM must be mapped to a customer "
                        "before activation"
                    )
                )

            if not sim.plan_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        "SIM must be mapped to a service plan "
                        "before activation"
                    )
                )

            sim.activation_date = datetime.now(
                timezone.utc
            )

        sim.status = new_status

        return SIMCardRepository.update(
            db,
            sim
        )

    @staticmethod
    def search_sims(
        db: Session,
        search: str | None = None,
        sim_type: str | None = None,
        status: str | None = None,
        customer_id: int | None = None,
        plan_id: int | None = None
    ):

        if sim_type:

            SIMCardService.validate_sim_type(
                sim_type
            )

        if status:

            SIMCardService.validate_status(
                status
            )

        return SIMCardRepository.search(
            db=db,
            search=search,
            sim_type=sim_type,
            status=status,
            customer_id=customer_id,
            plan_id=plan_id
        )

    @staticmethod
    def replace_sim(
        db: Session,
        old_sim_id: int,
        new_sim_id: int,
        reason: str,
        remarks: str | None,
        replaced_by: int
    ):

        if old_sim_id == new_sim_id:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Old and new SIM cannot be the same"
            )

        old_sim = SIMCardService.get_sim(
            db,
            old_sim_id
        )

        new_sim = SIMCardService.get_sim(
            db,
            new_sim_id
        )

        if old_sim.status not in {
            "Active",
            "Lost",
            "Blocked",
            "Suspended"
        }:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "SIM cannot be replaced in its "
                    "current status"
                )
            )

        if new_sim.status != "Available":

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "New SIM must have Available status"
                )
            )

        if not old_sim.customer_id:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Old SIM is not mapped to a customer"
                )
            )

        new_sim.customer_id = old_sim.customer_id
        new_sim.plan_id = old_sim.plan_id
        new_sim.status = "Active"
        new_sim.activation_date = datetime.now(
            timezone.utc
        )

        old_sim.status = "Deactivated"

        history = SIMReplacementHistory(
            old_sim_id=old_sim.id,
            new_sim_id=new_sim.id,
            customer_id=old_sim.customer_id,
            reason=reason,
            remarks=remarks,
            replaced_by=replaced_by
        )

        db.add(old_sim)
        db.add(new_sim)
        db.add(history)

        db.commit()

        db.refresh(old_sim)
        db.refresh(new_sim)
        db.refresh(history)

        return new_sim

    @staticmethod
    def get_replacement_history(
        db: Session,
        customer_id: int | None = None,
        sim_id: int | None = None
    ):

        if customer_id:

            return SIMReplacementRepository.get_by_customer_id(
                db,
                customer_id
            )

        if sim_id:

            return SIMReplacementRepository.get_by_sim_id(
                db,
                sim_id
            )

        return []