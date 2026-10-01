from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.service_plan_model import ServicePlan

from repositories.service_plan_repository import (
    ServicePlanRepository
)


class ServicePlanService:

    ALLOWED_PLAN_TYPES = {
        "Prepaid",
        "Postpaid",
        "Data",
        "Voice",
        "SMS"
    }

    @staticmethod
    def validate_plan_type(
        plan_type: str
    ):

        if plan_type not in (
            ServicePlanService.ALLOWED_PLAN_TYPES
        ):

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Invalid plan type. "
                    "Allowed values: "
                    "Prepaid, Postpaid, Data, Voice, SMS"
                )
            )

    @staticmethod
    def create_plan(
        db: Session,
        plan_code: str,
        plan_name: str,
        plan_type: str,
        data_limit: float,
        voice_limit: int,
        sms_limit: int,
        validity_days: int,
        price: float,
        description: str | None
    ):

        ServicePlanService.validate_plan_type(
            plan_type
        )

        existing_plan = (
            ServicePlanRepository.get_by_code(
                db,
                plan_code
            )
        )

        if existing_plan:

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Plan code already exists"
            )

        plan = ServicePlan(
            plan_code=plan_code.upper(),
            plan_name=plan_name,
            plan_type=plan_type,
            data_limit=data_limit,
            voice_limit=voice_limit,
            sms_limit=sms_limit,
            validity_days=validity_days,
            price=price,
            description=description,
            is_active=True
        )

        return ServicePlanRepository.create(
            db,
            plan
        )

    @staticmethod
    def get_plan(
        db: Session,
        plan_id: int
    ):

        plan = ServicePlanRepository.get_by_id(
            db,
            plan_id
        )

        if not plan:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service plan not found"
            )

        return plan

    @staticmethod
    def update_plan(
        db: Session,
        plan_id: int,
        plan_name: str | None,
        data_limit: float | None,
        voice_limit: int | None,
        sms_limit: int | None,
        validity_days: int | None,
        price: float | None,
        description: str | None
    ):

        plan = ServicePlanService.get_plan(
            db,
            plan_id
        )

        if plan_name is not None:
            plan.plan_name = plan_name

        if data_limit is not None:
            plan.data_limit = data_limit

        if voice_limit is not None:
            plan.voice_limit = voice_limit

        if sms_limit is not None:
            plan.sms_limit = sms_limit

        if validity_days is not None:
            plan.validity_days = validity_days

        if price is not None:
            plan.price = price

        if description is not None:
            plan.description = description

        return ServicePlanRepository.update(
            db,
            plan
        )

    @staticmethod
    def update_status(
        db: Session,
        plan_id: int,
        is_active: bool
    ):

        plan = ServicePlanService.get_plan(
            db,
            plan_id
        )

        plan.is_active = is_active

        return ServicePlanRepository.update(
            db,
            plan
        )

    @staticmethod
    def search_plans(
        db: Session,
        search: str | None = None,
        plan_type: str | None = None,
        is_active: bool | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        min_validity: int | None = None
    ):

        if plan_type:

            ServicePlanService.validate_plan_type(
                plan_type
            )

        return ServicePlanRepository.search(
            db=db,
            search=search,
            plan_type=plan_type,
            is_active=is_active,
            min_price=min_price,
            max_price=max_price,
            min_validity=min_validity
        )

    @staticmethod
    def compare_plans(
        db: Session,
        plan_ids: list[int]
    ):

        if len(plan_ids) < 2:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least 2 plans are required"
            )

        if len(plan_ids) > 5:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You can compare maximum 5 plans"
            )

        plans = (
            ServicePlanRepository.get_multiple_by_ids(
                db,
                plan_ids
            )
        )

        if len(plans) != len(set(plan_ids)):

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="One or more plans not found"
            )

        return plans