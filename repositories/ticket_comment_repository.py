from sqlalchemy.orm import Session

from models.ticket_comment_model import TicketComment


class TicketCommentRepository:

    @staticmethod
    def create(
        db: Session,
        comment: TicketComment
    ) -> TicketComment:

        db.add(comment)
        db.commit()
        db.refresh(comment)

        return comment

    @staticmethod
    def get_by_ticket(
        db: Session,
        ticket_id: int
    ):

        return (
            db.query(TicketComment)
            .filter(
                TicketComment.ticket_id == ticket_id
            )
            .order_by(
                TicketComment.created_at.desc()
            )
            .all()
        )