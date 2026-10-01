from sqlalchemy.orm import Session

from models.subscription_model import Subscription


class SubscriptionRepository:

    @staticmethod
    def get_by_id(
        db: Session,
        subscription_id: int
    ) -> Subscription | None:

        return (
            db.query(Subscription)
            .filter(
                Subscription.id == subscription_id
            )
            .first()
        )

    @staticmethod
    def get_active_by_sim(
        db: Session,
        sim_id: int
    ) -> Subscription | None:

        return (
            db.query(Subscription)
            .filter(
                Subscription.sim_id == sim_id,
                Subscription.status == "Active"
            )
            .first()
        )

    @staticmethod
    def get_active_by_customer(
        db: Session,
        customer_id: int
    ):

        return (
            db.query(Subscription)
            .filter(
                Subscription.customer_id == customer_id,
                Subscription.status == "Active"
            )
            .all()
        )

    @staticmethod
    def create(
        db: Session,
        subscription: Subscription
    ) -> Subscription:

        db.add(subscription)
        db.commit()
        db.refresh(subscription)

        return subscription

    @staticmethod
    def update(
        db: Session,
        subscription: Subscription
    ) -> Subscription:

        db.commit()
        db.refresh(subscription)

        return subscription

    @staticmethod
    def get_by_customer(
        db: Session,
        customer_id: int
    ):

        return (
            db.query(Subscription)
            .filter(
                Subscription.customer_id == customer_id
            )
            .order_by(
                Subscription.created_at.desc()
            )
            .all()
        )

    @staticmethod
    def get_by_sim(
        db: Session,
        sim_id: int
    ):

        return (
            db.query(Subscription)
            .filter(
                Subscription.sim_id == sim_id
            )
            .order_by(
                Subscription.created_at.desc()
            )
            .all()
        )

    