from sqlalchemy.orm import Session

from models.customer_history_model import CustomerHistory


class CustomerHistoryRepository:

    @staticmethod
    def create(
        db: Session,
        history: CustomerHistory
    ) -> CustomerHistory:

        db.add(history)
        db.commit()
        db.refresh(history)

        return history

    @staticmethod
    def get_by_customer_id(
        db: Session,
        customer_id: int
    ):

        return (
            db.query(CustomerHistory)
            .filter(
                CustomerHistory.customer_id == customer_id
            )
            .order_by(
                CustomerHistory.created_at.desc()
            )
            .all()
        )