from datetime import datetime

from sqlalchemy.orm import Session

from models.usage_model import UsageRecord


class UsageRepository:

    @staticmethod
    def create(
        db: Session,
        usage: UsageRecord
    ) -> UsageRecord:

        db.add(usage)
        db.commit()
        db.refresh(usage)

        return usage

    @staticmethod
    def get_by_id(
        db: Session,
        usage_id: int
    ) -> UsageRecord | None:

        return (
            db.query(UsageRecord)
            .filter(
                UsageRecord.id == usage_id
            )
            .first()
        )

    @staticmethod
    def get_by_subscription(
        db: Session,
        subscription_id: int
    ):

        return (
            db.query(UsageRecord)
            .filter(
                UsageRecord.subscription_id == subscription_id
            )
            .order_by(
                UsageRecord.usage_date.desc()
            )
            .all()
        )

    @staticmethod
    def get_by_sim(
        db: Session,
        sim_id: int
    ):

        return (
            db.query(UsageRecord)
            .filter(
                UsageRecord.sim_id == sim_id
            )
            .order_by(
                UsageRecord.usage_date.desc()
            )
            .all()
        )

    @staticmethod
    def get_by_customer(
        db: Session,
        customer_id: int
    ):

        return (
            db.query(UsageRecord)
            .filter(
                UsageRecord.customer_id == customer_id
            )
            .order_by(
                UsageRecord.usage_date.desc()
            )
            .all()
        )

    @staticmethod
    def get_between_dates(
        db: Session,
        subscription_id: int,
        start_date: datetime,
        end_date: datetime
    ):

        return (
            db.query(UsageRecord)
            .filter(
                UsageRecord.subscription_id == subscription_id,
                UsageRecord.usage_date >= start_date,
                UsageRecord.usage_date < end_date
            )
            .order_by(
                UsageRecord.usage_date.asc()
            )
            .all()
        )