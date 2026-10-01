from sqlalchemy.orm import Session

from models.ticket_history_model import TicketHistory


class TicketHistoryRepository:

    @staticmethod
    def create(
        db: Session,
        history: TicketHistory
    ) -> TicketHistory:

        db.add(history)
        db.commit()
        db.refresh(history)

        return history

    @staticmethod
    def get_by_ticket(
        db: Session,
        ticket_id: int
    ):

        return (
            db.query(TicketHistory)
            .filter(
                TicketHistory.ticket_id == ticket_id
            )
            .order_by(
                TicketHistory.created_at.desc()
            )
            .all()
        )