from sqlalchemy.orm import Session

from models.service_request_history_model import (
    ServiceRequestHistory
)


class ServiceRequestHistoryRepository:

    @staticmethod
    def create(
        db: Session,
        history: ServiceRequestHistory
    ):

        db.add(history)
        db.commit()
        db.refresh(history)

        return history

    @staticmethod
    def get_by_request(
        db: Session,
        request_id: int
    ):

        return (
            db.query(ServiceRequestHistory)
            .filter(
                ServiceRequestHistory.service_request_id
                == request_id
            )
            .order_by(
                ServiceRequestHistory.created_at.asc()
            )
            .all()
        )