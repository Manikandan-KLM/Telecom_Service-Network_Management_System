from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy.orm import Session

from models.usage_model import UsageRecord

from repositories.usage_repository import (
    UsageRepository
)

from repositories.subscription_repository import (
    SubscriptionRepository
)

from repositories.service_plan_repository import (
    ServicePlanRepository
)


class UsageService:

    ALLOWED_USAGE_TYPES = {
        "Data",
        "Voice",
        "SMS"
    }

    @staticmethod
    def get_subscription(
        db: Session,
        subscription_id: int
    ):

        subscription = (
            SubscriptionRepository.get_by_id(
                db,
                subscription_id
            )
        )

        if not subscription:
            raise HTTPException(
                status_code=404,
                detail="Subscription not found"
            )

        return subscription

    @staticmethod
    def get_plan(
        db: Session,
        plan_id: int
    ):

        plan = (
            ServicePlanRepository.get_by_id(
                db,
                plan_id
            )
        )

        if not plan:
            raise HTTPException(
                status_code=404,
                detail="Service plan not found"
            )

        return plan

    @staticmethod
    def validate_usage_type(
        usage_type: str
    ):

        if usage_type not in UsageService.ALLOWED_USAGE_TYPES:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Invalid usage type. "
                    "Allowed values: Data, Voice, SMS"
                )
            )

    @staticmethod
    def validate_usage_amount(
        usage_type: str,
        usage_amount: float,
        plan
    ):

        if usage_amount <= 0:

            raise HTTPException(
                status_code=400,
                detail="Usage amount must be greater than zero"
            )

        if usage_type == "Data":

            quota = plan.data_limit

        elif usage_type == "Voice":

            quota = plan.voice_limit

        else:

            quota = plan.sms_limit

        if quota <= 0:

            raise HTTPException(
                status_code=400,
                detail=f"{usage_type} quota is not available in this plan"
            )

    @staticmethod
    def create_usage(
        db: Session,
        subscription_id: int,
        usage_type: str,
        usage_amount: float,
        usage_date: datetime | None
    ):

        subscription = UsageService.get_subscription(
            db,
            subscription_id
        )

        if subscription.status != "Active":

            raise HTTPException(
                status_code=400,
                detail="Usage can only be recorded for an Active subscription"
            )

        plan = UsageService.get_plan(
            db,
            subscription.plan_id
        )

        UsageService.validate_usage_type(
            usage_type
        )

        UsageService.validate_usage_amount(
            usage_type,
            usage_amount,
            plan
        )

        if usage_date is None:
            usage_date = datetime.now(timezone.utc)

        if usage_date < subscription.start_date:

            raise HTTPException(
                status_code=400,
                detail="Usage date cannot be before subscription start date"
            )

        if usage_date > subscription.end_date:

            raise HTTPException(
                status_code=400,
                detail="Usage date cannot be after subscription end date"
            )

        usage = UsageRecord(
            customer_id=subscription.customer_id,
            sim_id=subscription.sim_id,
            subscription_id=subscription.id,
            usage_type=usage_type,
            usage_amount=usage_amount,
            usage_date=usage_date
        )

        return UsageRepository.create(
            db,
            usage
        )

    @staticmethod
    def get_subscription_usage(
        db: Session,
        subscription_id: int
    ):

        UsageService.get_subscription(
            db,
            subscription_id
        )

        return UsageRepository.get_by_subscription(
            db,
            subscription_id
        )

    @staticmethod
    def get_sim_usage(
        db: Session,
        sim_id: int
    ):

        return UsageRepository.get_by_sim(
            db,
            sim_id
        )

    @staticmethod
    def get_customer_usage(
        db: Session,
        customer_id: int
    ):

        return UsageRepository.get_by_customer(
            db,
            customer_id
        )


    @staticmethod
    def get_usage_summary(
        db: Session,
        subscription_id: int
    ):

        subscription = UsageService.get_subscription(
            db,
            subscription_id
        )

        plan = UsageService.get_plan(
            db,
            subscription.plan_id
        )

        usage_records = (
            UsageRepository.get_by_subscription(
                db,
                subscription_id
            )
        )

        data_used = 0.0
        voice_used = 0.0
        sms_used = 0.0

        for usage in usage_records:

            if usage.usage_type == "Data":
                data_used += usage.usage_amount

            elif usage.usage_type == "Voice":
                voice_used += usage.usage_amount

            elif usage.usage_type == "SMS":
                sms_used += usage.usage_amount

        data_quota = plan.data_limit
        voice_quota = float(plan.voice_limit)
        sms_quota = float(plan.sms_limit)

        data_remaining = max(
            data_quota - data_used,
            0
        )

        voice_remaining = max(
            voice_quota - voice_used,
            0
        )

        sms_remaining = max(
            sms_quota - sms_used,
            0
        )

        data_percentage = (
            (data_used / data_quota) * 100
            if data_quota > 0
            else 0
        )

        voice_percentage = (
            (voice_used / voice_quota) * 100
            if voice_quota > 0
            else 0
        )

        sms_percentage = (
            (sms_used / sms_quota) * 100
            if sms_quota > 0
            else 0
        )

        return {
            "customer_id": subscription.customer_id,
            "sim_id": subscription.sim_id,
            "subscription_id": subscription.id,

            "data_used": data_used,
            "voice_used": voice_used,
            "sms_used": sms_used,

            "data_quota": data_quota,
            "voice_quota": voice_quota,
            "sms_quota": sms_quota,

            "data_percentage": round(
                data_percentage,
                2
            ),

            "voice_percentage": round(
                voice_percentage,
                2
            ),

            "sms_percentage": round(
                sms_percentage,
                2
            ),

            "data_remaining": data_remaining,
            "voice_remaining": voice_remaining,
            "sms_remaining": sms_remaining
        }



    @staticmethod
    def get_daily_usage(
        db: Session,
        subscription_id: int,
        date_value
    ):

        from datetime import datetime, timedelta, timezone

        start_date = datetime(
            date_value.year,
            date_value.month,
            date_value.day,
            tzinfo=timezone.utc
        )

        end_date = start_date + timedelta(days=1)

        return UsageRepository.get_between_dates(
            db=db,
            subscription_id=subscription_id,
            start_date=start_date,
            end_date=end_date
        )



        
    @staticmethod
    def get_monthly_usage(
        db: Session,
        subscription_id: int,
        year: int,
        month: int
    ):

        from datetime import datetime, timezone

        if month < 1 or month > 12:

            raise HTTPException(
                status_code=400,
                detail="Month must be between 1 and 12"
            )

        start_date = datetime(
            year,
            month,
            1,
            tzinfo=timezone.utc
        )

        if month == 12:

            end_date = datetime(
                year + 1,
                1,
                1,
                tzinfo=timezone.utc
            )

        else:

            end_date = datetime(
                year,
                month + 1,
                1,
                tzinfo=timezone.utc
            )

        return UsageRepository.get_between_dates(
            db=db,
            subscription_id=subscription_id,
            start_date=start_date,
            end_date=end_date
        )