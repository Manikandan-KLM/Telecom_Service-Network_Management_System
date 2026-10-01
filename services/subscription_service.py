from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.subscription_model import Subscription
from models.subscription_history_model import (
    SubscriptionHistory
)

from repositories.subscription_repository import (
    SubscriptionRepository
)

from repositories.subscription_history_repository import (
    SubscriptionHistoryRepository
)

from repositories.customer_repository import (
    CustomerRepository
)

from repositories.service_plan_repository import (
    ServicePlanRepository
)

from repositories.sim_card_repository import (
    SIMCardRepository
)


class SubscriptionService:

    ALLOWED_STATUSES = {
        "Active",
        "Suspended",
        "Cancelled",
        "Expired"
    }

    # ==================================================
    # VALIDATE CUSTOMER
    # ==================================================

    @staticmethod
    def validate_customer(
        db: Session,
        customer_id: int
    ):

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

    # ==================================================
    # VALIDATE SIM
    # ==================================================

    @staticmethod
    def validate_sim(
        db: Session,
        sim_id: int,
        customer_id: int
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

        if sim.customer_id != customer_id:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "SIM does not belong to the customer"
                )
            )

        if sim.status != "Active":

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Only an Active SIM can have "
                    "a subscription"
                )
            )

        return sim

    # ==================================================
    # VALIDATE PLAN
    # ==================================================

    @staticmethod
    def validate_plan(
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

        if not plan.is_active:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Service plan is inactive"
            )

        return plan

    # ==================================================
    # ADD HISTORY
    # ==================================================

    @staticmethod
    def add_history(
        db: Session,
        subscription_id: int,
        old_plan_id: int | None,
        new_plan_id: int | None,
        old_status: str | None,
        new_status: str | None,
        action: str,
        description: str,
        changed_by: int
    ):

        history = SubscriptionHistory(
            subscription_id=subscription_id,
            old_plan_id=old_plan_id,
            new_plan_id=new_plan_id,
            old_status=old_status,
            new_status=new_status,
            action=action,
            description=description,
            changed_by=changed_by
        )

        db.add(history)

    # ==================================================
    # CREATE SUBSCRIPTION
    # ==================================================

    @staticmethod
    def create_subscription(
        db: Session,
        customer_id: int,
        sim_id: int,
        plan_id: int,
        changed_by: int
    ):

        SubscriptionService.validate_customer(
            db,
            customer_id
        )

        SubscriptionService.validate_sim(
            db,
            sim_id,
            customer_id
        )

        plan = SubscriptionService.validate_plan(
            db,
            plan_id
        )

        # One active subscription per SIM
        existing_subscription = (
            SubscriptionRepository.get_active_by_sim(
                db,
                sim_id
            )
        )

        if existing_subscription:

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "SIM already has an active subscription"
                )
            )

        start_date = datetime.now(timezone.utc)

        end_date = (
            start_date
            + timedelta(days=plan.validity_days)
        )

        subscription = Subscription(
            customer_id=customer_id,
            sim_id=sim_id,
            plan_id=plan_id,
            start_date=start_date,
            end_date=end_date,
            status="Active"
        )

        db.add(subscription)
        db.flush()

        SubscriptionService.add_history(
            db=db,
            subscription_id=subscription.id,
            old_plan_id=None,
            new_plan_id=plan_id,
            old_status=None,
            new_status="Active",
            action="Created",
            description=(
                f"Subscription created with "
                f"plan {plan.plan_name}"
            ),
            changed_by=changed_by
        )

        db.commit()
        db.refresh(subscription)

        return subscription

    # ==================================================
    # GET SUBSCRIPTION
    # ==================================================

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
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subscription not found"
            )

        return subscription

    # ==================================================
    # PLAN UPGRADE
    # ==================================================

    @staticmethod
    def upgrade_plan(
        db: Session,
        subscription_id: int,
        new_plan_id: int,
        changed_by: int
    ):

        subscription = SubscriptionService.get_subscription(
            db,
            subscription_id
        )

        if subscription.status != "Active":

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Only an Active subscription "
                    "can be upgraded"
                )
            )

        old_plan = SubscriptionService.validate_plan(
            db,
            subscription.plan_id
        )

        new_plan = SubscriptionService.validate_plan(
            db,
            new_plan_id
        )

        if new_plan.id == old_plan.id:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New plan is same as current plan"
            )

        if new_plan.price <= old_plan.price:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Upgrade plan must have a higher price "
                    "than current plan"
                )
            )

        old_plan_id = subscription.plan_id

        subscription.plan_id = new_plan.id

        SubscriptionService.add_history(
            db=db,
            subscription_id=subscription.id,
            old_plan_id=old_plan_id,
            new_plan_id=new_plan.id,
            old_status="Active",
            new_status="Active",
            action="Plan Upgrade",
            description=(
                f"Plan upgraded from "
                f"{old_plan.plan_name} to "
                f"{new_plan.plan_name}"
            ),
            changed_by=changed_by
        )

        db.commit()
        db.refresh(subscription)

        return subscription

    # ==================================================
    # PLAN DOWNGRADE
    # ==================================================

    @staticmethod
    def downgrade_plan(
        db: Session,
        subscription_id: int,
        new_plan_id: int,
        changed_by: int
    ):

        subscription = SubscriptionService.get_subscription(
            db,
            subscription_id
        )

        if subscription.status != "Active":

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Only an Active subscription "
                    "can be downgraded"
                )
            )

        old_plan = SubscriptionService.validate_plan(
            db,
            subscription.plan_id
        )

        new_plan = SubscriptionService.validate_plan(
            db,
            new_plan_id
        )

        if new_plan.id == old_plan.id:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New plan is same as current plan"
            )

        if new_plan.price >= old_plan.price:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Downgrade plan must have a lower price "
                    "than current plan"
                )
            )

        old_plan_id = subscription.plan_id

        subscription.plan_id = new_plan.id

        SubscriptionService.add_history(
            db=db,
            subscription_id=subscription.id,
            old_plan_id=old_plan_id,
            new_plan_id=new_plan.id,
            old_status="Active",
            new_status="Active",
            action="Plan Downgrade",
            description=(
                f"Plan downgraded from "
                f"{old_plan.plan_name} to "
                f"{new_plan.plan_name}"
            ),
            changed_by=changed_by
        )

        db.commit()
        db.refresh(subscription)

        return subscription

    # ==================================================
    # RENEW SUBSCRIPTION
    # ==================================================

    @staticmethod
    def renew_subscription(
        db: Session,
        subscription_id: int,
        changed_by: int
    ):

        subscription = SubscriptionService.get_subscription(
            db,
            subscription_id
        )

        if subscription.status != "Active":

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Only an Active subscription "
                    "can be renewed"
                )
            )

        plan = SubscriptionService.validate_plan(
            db,
            subscription.plan_id
        )

        old_end_date = subscription.end_date

        current_time = datetime.now(timezone.utc)

        if subscription.end_date > current_time:

            new_start_date = subscription.end_date

        else:

            new_start_date = current_time

        subscription.end_date = (
            new_start_date
            + timedelta(days=plan.validity_days)
        )

        SubscriptionService.add_history(
            db=db,
            subscription_id=subscription.id,
            old_plan_id=subscription.plan_id,
            new_plan_id=subscription.plan_id,
            old_status="Active",
            new_status="Active",
            action="Renewed",
            description=(
                f"Subscription renewed. "
                f"Previous end date: {old_end_date}"
            ),
            changed_by=changed_by
        )

        db.commit()
        db.refresh(subscription)

        return subscription

    # ==================================================
    # SUSPEND
    # ==================================================

    @staticmethod
    def suspend_subscription(
        db: Session,
        subscription_id: int,
        changed_by: int
    ):

        subscription = SubscriptionService.get_subscription(
            db,
            subscription_id
        )

        if subscription.status != "Active":

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Only an Active subscription "
                    "can be suspended"
                )
            )

        old_status = subscription.status

        subscription.status = "Suspended"

        SubscriptionService.add_history(
            db=db,
            subscription_id=subscription.id,
            old_plan_id=subscription.plan_id,
            new_plan_id=subscription.plan_id,
            old_status=old_status,
            new_status="Suspended",
            action="Suspended",
            description="Subscription suspended",
            changed_by=changed_by
        )

        db.commit()
        db.refresh(subscription)

        return subscription

    # ==================================================
    # REACTIVATE
    # ==================================================

    @staticmethod
    def reactivate_subscription(
        db: Session,
        subscription_id: int,
        changed_by: int
    ):

        subscription = SubscriptionService.get_subscription(
            db,
            subscription_id
        )

        if subscription.status != "Suspended":

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Only a Suspended subscription "
                    "can be reactivated"
                )
            )

        old_status = subscription.status

        subscription.status = "Active"

        SubscriptionService.add_history(
            db=db,
            subscription_id=subscription.id,
            old_plan_id=subscription.plan_id,
            new_plan_id=subscription.plan_id,
            old_status=old_status,
            new_status="Active",
            action="Reactivated",
            description="Subscription reactivated",
            changed_by=changed_by
        )

        db.commit()
        db.refresh(subscription)

        return subscription

    # ==================================================
    # CANCEL
    # ==================================================

    @staticmethod
    def cancel_subscription(
        db: Session,
        subscription_id: int,
        changed_by: int
    ):

        subscription = SubscriptionService.get_subscription(
            db,
            subscription_id
        )

        if subscription.status == "Cancelled":

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Subscription already cancelled"
            )

        old_status = subscription.status

        subscription.status = "Cancelled"

        SubscriptionService.add_history(
            db=db,
            subscription_id=subscription.id,
            old_plan_id=subscription.plan_id,
            new_plan_id=None,
            old_status=old_status,
            new_status="Cancelled",
            action="Cancelled",
            description="Subscription cancelled",
            changed_by=changed_by
        )

        db.commit()
        db.refresh(subscription)

        return subscription

    # ==================================================
    # HISTORY
    # ==================================================

    @staticmethod
    def get_history(
        db: Session,
        subscription_id: int
    ):

        SubscriptionService.get_subscription(
            db,
            subscription_id
        )

        return (
            SubscriptionHistoryRepository
            .get_by_subscription(
                db,
                subscription_id
            )
        )

    # ==================================================
    # CUSTOMER SUBSCRIPTIONS
    # ==================================================

    @staticmethod
    def get_customer_subscriptions(
        db: Session,
        customer_id: int
    ):

        SubscriptionService.validate_customer(
            db,
            customer_id
        )

        return (
            SubscriptionRepository.get_by_customer(
                db,
                customer_id
            )
        )