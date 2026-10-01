from sqlalchemy.orm import Session

from models.support_ticket_model import SupportTicket


class SupportTicketRepository:

    # =================================================
    # GET BY ID
    # =================================================

    @staticmethod
    def get_by_id(
        db: Session,
        ticket_id: int
    ) -> SupportTicket | None:

        return (
            db.query(SupportTicket)
            .filter(
                SupportTicket.id == ticket_id
            )
            .first()
        )

    # =================================================
    # GET BY NUMBER
    # =================================================

    @staticmethod
    def get_by_number(
        db: Session,
        ticket_number: str
    ) -> SupportTicket | None:

        return (
            db.query(SupportTicket)
            .filter(
                SupportTicket.ticket_number
                == ticket_number
            )
            .first()
        )

    # =================================================
    # CREATE
    # =================================================

    @staticmethod
    def create(
        db: Session,
        ticket: SupportTicket
    ) -> SupportTicket:

        db.add(ticket)
        db.commit()
        db.refresh(ticket)

        return ticket

    # =================================================
    # UPDATE
    # =================================================

    @staticmethod
    def update(
        db: Session,
        ticket: SupportTicket
    ) -> SupportTicket:

        db.commit()
        db.refresh(ticket)

        return ticket

    # =================================================
    # CUSTOMER TICKETS
    # =================================================

    @staticmethod
    def get_by_customer(
        db: Session,
        customer_id: int
    ):

        return (
            db.query(SupportTicket)
            .filter(
                SupportTicket.customer_id
                == customer_id
            )
            .order_by(
                SupportTicket.created_at.desc()
            )
            .all()
        )

    # =================================================
    # ASSIGNED TICKETS
    # =================================================

    @staticmethod
    def get_by_assigned_user(
        db: Session,
        user_id: int
    ):

        return (
            db.query(SupportTicket)
            .filter(
                SupportTicket.assigned_to
                == user_id
            )
            .order_by(
                SupportTicket.created_at.desc()
            )
            .all()
        )

    # =================================================
    # ALL TICKETS
    # =================================================

    @staticmethod
    def get_all(
        db: Session,
        status: str | None = None,
        ticket_type: str | None = None,
        priority: str | None = None
    ):

        query = db.query(SupportTicket)

        if status:

            query = query.filter(
                SupportTicket.status == status
            )

        if ticket_type:

            query = query.filter(
                SupportTicket.ticket_type
                == ticket_type
            )

        if priority:

            query = query.filter(
                SupportTicket.priority
                == priority
            )

        return (
            query
            .order_by(
                SupportTicket.created_at.desc()
            )
            .all()
        )


    @staticmethod
    def get_by_agent(
        db: Session,
        agent_id: int
):

     return (
        db.query(SupportTicket)
        .filter(
            SupportTicket.assigned_agent_id == agent_id
        )
        .order_by(
            SupportTicket.created_at.desc()
        )
        .all()
    )


@staticmethod
def get_by_technician(
    db: Session,
    technician_id: int
):

    return (
        db.query(SupportTicket)
        .filter(
            SupportTicket.assigned_technician_id == technician_id
        )
        .order_by(
            SupportTicket.created_at.desc()
        )
        .all()
    )