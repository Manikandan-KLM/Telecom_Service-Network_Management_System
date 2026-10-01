from sqlalchemy.orm import Session

from models.subscription_history_model import (
    SubscriptionHistory
)


class SubscriptionHistoryRepository:

    @staticmethod
    def create(
        db: Session,
        history: SubscriptionHistory
    ) -> SubscriptionHistory:

        db.add(history)
        db.commit()
        db.refresh(history)

        return history

    @staticmethod
    def get_by_subscription(
        db: Session,
        subscription_id: int
    ):

        return (
            db.query(SubscriptionHistory)
            .filter(
                SubscriptionHistory.subscription_id
                == subscription_id
            )
            .order_by(
                SubscriptionHistory.created_at.desc()
            )
            .all()
        )