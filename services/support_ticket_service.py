import uuid
from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy.orm import Session

from models.support_ticket_model import SupportTicket

from repositories.support_ticket_repository import (
    SupportTicketRepository
)


class SupportTicketService:

    # =================================================
    # ALLOWED VALUES
    # =================================================

    TICKET_TYPES = {
        "Network Issue",
        "SIM Issue",
        "Data Issue",
        "Voice Issue",
        "Device Issue",
        "Account Issue",
        "Service Request"
    }

    PRIORITIES = {
        "Low",
        "Medium",
        "High",
        "Critical"
    }

    STATUSES = {
        "Open",
        "Assigned",
        "In Progress",
        "Waiting for Customer",
        "Resolved",
        "Closed"
    }

    # =================================================
    # VALIDATE TICKET TYPE
    # =================================================

    @staticmethod
    def validate_ticket_type(
        ticket_type: str
    ):

        if ticket_type not in (
            SupportTicketService.TICKET_TYPES
        ):

            raise HTTPException(
                status_code=400,
                detail="Invalid ticket type"
            )

    # =================================================
    # VALIDATE PRIORITY
    # =================================================

    @staticmethod
    def validate_priority(
        priority: str
    ):

        if priority not in (
            SupportTicketService.PRIORITIES
        ):

            raise HTTPException(
                status_code=400,
                detail="Invalid priority"
            )

    # =================================================
    # VALIDATE STATUS
    # =================================================

    @staticmethod
    def validate_status(
        status: str
    ):

        if status not in (
            SupportTicketService.STATUSES
        ):

            raise HTTPException(
                status_code=400,
                detail="Invalid ticket status"
            )

    # =================================================
    # GENERATE TICKET NUMBER
    # =================================================

    @staticmethod
    def generate_ticket_number() -> str:

        unique_part = uuid.uuid4().hex[:8].upper()

        return f"TKT-{unique_part}"

    # =================================================
    # CREATE TICKET
    # =================================================

    @staticmethod
    def create_ticket(
        db: Session,
        customer_id: int,
        ticket_type: str,
        subject: str,
        description: str,
        priority: str
    ):

        SupportTicketService.validate_ticket_type(
            ticket_type
        )

        SupportTicketService.validate_priority(
            priority
        )

        ticket_number = (
            SupportTicketService
            .generate_ticket_number()
        )

        ticket = SupportTicket(
            ticket_number=ticket_number,
            customer_id=customer_id,
            assigned_to=None,
            ticket_type=ticket_type,
            subject=subject,
            description=description,
            priority=priority,
            status="Open"
        )

        return SupportTicketRepository.create(
            db,
            ticket
        )

    # =================================================
    # GET TICKET
    # =================================================

    @staticmethod
    def get_ticket(
        db: Session,
        ticket_id: int
    ):

        ticket = (
            SupportTicketRepository.get_by_id(
                db,
                ticket_id
            )
        )

        if not ticket:

            raise HTTPException(
                status_code=404,
                detail="Support ticket not found"
            )

        return ticket

    # =================================================
    # ASSIGN TICKET
    # =================================================

    @staticmethod
    def assign_ticket(
        db: Session,
        ticket_id: int,
        assigned_to: int
    ):

        ticket = (
            SupportTicketRepository.get_by_id(
                db,
                ticket_id
            )
        )

        if not ticket:

            raise HTTPException(
                status_code=404,
                detail="Support ticket not found"
            )

        if ticket.status in {
            "Resolved",
            "Closed"
        }:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Resolved or closed ticket "
                    "cannot be assigned"
                )
            )

        ticket.assigned_to = assigned_to

        ticket.status = "Assigned"

        return SupportTicketRepository.update(
            db,
            ticket
        )

    # =================================================
    # UPDATE STATUS
    # =================================================

    @staticmethod
    def update_status(
        db: Session,
        ticket_id: int,
        status: str,
        resolution_notes: str | None = None
    ):

        ticket = (
            SupportTicketRepository.get_by_id(
                db,
                ticket_id
            )
        )

        if not ticket:

            raise HTTPException(
                status_code=404,
                detail="Support ticket not found"
            )

        SupportTicketService.validate_status(
            status
        )

        # ---------------------------------------------
        # CLOSED TICKET
        # ---------------------------------------------

        if ticket.status == "Closed":

            raise HTTPException(
                status_code=400,
                detail="Closed ticket cannot be modified"
            )

        # ---------------------------------------------
        # RESOLVED
        # ---------------------------------------------

        if status == "Resolved":

            if not ticket.assigned_to:

                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Ticket must be assigned "
                        "before resolution"
                    )
                )

            ticket.resolved_at = (
                datetime.now(timezone.utc)
            )

            ticket.resolution_notes = (
                resolution_notes
            )

        # ---------------------------------------------
        # CLOSED
        # ---------------------------------------------

        if status == "Closed":

            if ticket.status != "Resolved":

                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Only resolved tickets "
                        "can be closed"
                    )
                )

            ticket.closed_at = (
                datetime.now(timezone.utc)
            )

        ticket.status = status

        if resolution_notes is not None:

            ticket.resolution_notes = (
                resolution_notes
            )

        return SupportTicketRepository.update(
            db,
            ticket
        )

    # =================================================
    # CUSTOMER TICKETS
    # =================================================

    @staticmethod
    def get_customer_tickets(
        db: Session,
        customer_id: int
    ):

        return (
            SupportTicketRepository
            .get_by_customer(
                db,
                customer_id
            )
        )

    # =================================================
    # ASSIGNED TICKETS
    # =================================================

    @staticmethod
    def get_assigned_tickets(
        db: Session,
        user_id: int
    ):

        return (
            SupportTicketRepository
            .get_by_assigned_user(
                db,
                user_id
            )
        )
    

from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy.orm import Session

from models.support_ticket_model import SupportTicket
from models.ticket_history_model import TicketHistory
from models.ticket_comment_model import TicketComment

from models.user_model import User

from repositories.support_ticket_repository import (
    SupportTicketRepository
)

from repositories.ticket_history_repository import (
    TicketHistoryRepository
)

from repositories.ticket_comment_repository import (
    TicketCommentRepository
)

@staticmethod
def add_history(
        db: Session,
        ticket_id: int,
        changed_by: int,
        action: str,
        description: str,
        old_value: str | None = None,
        new_value: str | None = None
):

     history = TicketHistory(
        ticket_id=ticket_id,
        changed_by=changed_by,
        action=action,
        description=description,
        old_value=old_value,
        new_value=new_value
    )

     return TicketHistoryRepository.create(
        db,
        history
    )


@staticmethod
def assign_agent(
    db: Session,
    ticket_id: int,
    agent_id: int,
    changed_by: int
):

    ticket = SupportTicketRepository.get_by_id(
        db,
        ticket_id
    )

    if not ticket:
        raise HTTPException(
            status_code=404,
            detail="Support ticket not found"
        )

    agent = db.query(User).filter(
        User.id == agent_id
    ).first()

    if not agent:
        raise HTTPException(
            status_code=404,
            detail="Support agent not found"
        )

    if agent.role != "Support Agent":
        raise HTTPException(
            status_code=400,
            detail="Selected user is not a Support Agent"
        )

    if not agent.is_active:
        raise HTTPException(
            status_code=400,
            detail="Support agent is inactive"
        )

    if ticket.status == "Closed":
        raise HTTPException(
            status_code=400,
            detail="Closed ticket cannot be assigned"
        )

    old_agent = ticket.assigned_agent_id

    ticket.assigned_agent_id = agent_id

    if ticket.status == "Open":
        ticket.status = "Assigned"

    SupportTicketRepository.update(
        db,
        ticket
    )

    SupportTicketService.add_history(
        db=db,
        ticket_id=ticket.id,
        changed_by=changed_by,
        action="Agent Assignment",
        description="Support agent assigned to ticket",
        old_value=str(old_agent) if old_agent else None,
        new_value=str(agent_id)
    )

    return ticket



@staticmethod
def assign_technician(
    db: Session,
    ticket_id: int,
    technician_id: int,
    changed_by: int
):

    ticket = SupportTicketRepository.get_by_id(
        db,
        ticket_id
    )

    if not ticket:
        raise HTTPException(
            status_code=404,
            detail="Support ticket not found"
        )

    technician = db.query(User).filter(
        User.id == technician_id
    ).first()

    if not technician:
        raise HTTPException(
            status_code=404,
            detail="Technician not found"
        )

    if technician.role != "Field Technician":
        raise HTTPException(
            status_code=400,
            detail="Selected user is not a Field Technician"
        )

    if not technician.is_active:
        raise HTTPException(
            status_code=400,
            detail="Technician is inactive"
        )

    if ticket.status == "Closed":
        raise HTTPException(
            status_code=400,
            detail="Closed ticket cannot be assigned"
        )

    old_technician = ticket.assigned_technician_id

    ticket.assigned_technician_id = technician_id

    if ticket.status in {"Open", "Assigned"}:
        ticket.status = "In Progress"

    SupportTicketRepository.update(
        db,
        ticket
    )

    SupportTicketService.add_history(
        db=db,
        ticket_id=ticket.id,
        changed_by=changed_by,
        action="Technician Assignment",
        description="Field technician assigned to ticket",
        old_value=(
            str(old_technician)
            if old_technician
            else None
        ),
        new_value=str(technician_id)
    )

    return ticket



@staticmethod
def update_priority(
    db: Session,
    ticket_id: int,
    priority: str,
    changed_by: int
):

    allowed_priorities = {
        "Low",
        "Medium",
        "High",
        "Critical"
    }

    if priority not in allowed_priorities:
        raise HTTPException(
            status_code=400,
            detail="Invalid priority"
        )

    ticket = SupportTicketRepository.get_by_id(
        db,
        ticket_id
    )

    if not ticket:
        raise HTTPException(
            status_code=404,
            detail="Support ticket not found"
        )

    if ticket.status == "Closed":
        raise HTTPException(
            status_code=400,
            detail="Closed ticket cannot be modified"
        )

    old_priority = ticket.priority

    ticket.priority = priority

    SupportTicketRepository.update(
        db,
        ticket
    )

    SupportTicketService.add_history(
        db=db,
        ticket_id=ticket.id,
        changed_by=changed_by,
        action="Priority Changed",
        description="Ticket priority updated",
        old_value=old_priority,
        new_value=priority
    )

    return ticket


@staticmethod
def escalate_ticket(
    db: Session,
    ticket_id: int,
    reason: str,
    changed_by: int
):

    ticket = SupportTicketRepository.get_by_id(
        db,
        ticket_id
    )

    if not ticket:
        raise HTTPException(
            status_code=404,
            detail="Support ticket not found"
        )

    if ticket.status == "Closed":
        raise HTTPException(
            status_code=400,
            detail="Closed ticket cannot be escalated"
        )

    old_level = ticket.escalation_level

    if old_level >= 3:
        raise HTTPException(
            status_code=400,
            detail="Maximum escalation level reached"
        )

    ticket.escalation_level += 1
    ticket.escalation_reason = reason

    # Escalation automatically increases priority
    if ticket.escalation_level == 1:
        ticket.priority = "High"

    elif ticket.escalation_level == 2:
        ticket.priority = "Critical"

    elif ticket.escalation_level == 3:
        ticket.priority = "Critical"

    SupportTicketRepository.update(
        db,
        ticket
    )

    SupportTicketService.add_history(
        db=db,
        ticket_id=ticket.id,
        changed_by=changed_by,
        action="Ticket Escalated",
        description=reason,
        old_value=str(old_level),
        new_value=str(ticket.escalation_level)
    )

    return ticket


@staticmethod
def add_internal_comment(
    db: Session,
    ticket_id: int,
    user_id: int,
    comment_text: str
):

    ticket = SupportTicketRepository.get_by_id(
        db,
        ticket_id
    )

    if not ticket:
        raise HTTPException(
            status_code=404,
            detail="Support ticket not found"
        )

    if ticket.status == "Closed":
        raise HTTPException(
            status_code=400,
            detail="Closed ticket cannot receive comments"
        )

    comment = TicketComment(
        ticket_id=ticket_id,
        user_id=user_id,
        comment=comment_text
    )

    result = TicketCommentRepository.create(
        db,
        comment
    )

    SupportTicketService.add_history(
        db=db,
        ticket_id=ticket_id,
        changed_by=user_id,
        action="Internal Comment",
        description="Internal comment added"
    )

    return result


@staticmethod
def resolve_ticket(
    db: Session,
    ticket_id: int,
    resolution_notes: str,
    changed_by: int
):

    ticket = SupportTicketRepository.get_by_id(
        db,
        ticket_id
    )

    if not ticket:
        raise HTTPException(
            status_code=404,
            detail="Support ticket not found"
        )

    if ticket.status == "Closed":
        raise HTTPException(
            status_code=400,
            detail="Closed ticket cannot be resolved"
        )

    if not ticket.assigned_agent_id and not ticket.assigned_technician_id:
        raise HTTPException(
            status_code=400,
            detail="Ticket must be assigned before resolution"
        )

    if not resolution_notes.strip():
        raise HTTPException(
            status_code=400,
            detail="Resolution notes are required"
        )

    old_status = ticket.status

    ticket.status = "Resolved"
    ticket.resolution_notes = resolution_notes
    ticket.resolved_at = datetime.now(timezone.utc)

    SupportTicketRepository.update(
        db,
        ticket
    )

    SupportTicketService.add_history(
        db=db,
        ticket_id=ticket.id,
        changed_by=changed_by,
        action="Ticket Resolved",
        description="Ticket resolved successfully",
        old_value=old_status,
        new_value="Resolved"
    )

    return ticket



