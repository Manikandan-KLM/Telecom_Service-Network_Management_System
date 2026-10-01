from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from sqlalchemy.orm import Session

from models.sla_rule_model import SLARule
from models.ticket_sla_model import TicketSLA
from models.support_ticket_model import SupportTicket
from models.customer_model import Customer

from repositories.sla_repository import SLARepository


class SLAService:

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

    CUSTOMER_TYPES = {
        "Regular",
        "Premium",
        "Enterprise"
    }

    @staticmethod
    def validate_rule_data(
        ticket_type: str,
        priority: str,
        customer_type: str
    ):

        if ticket_type not in SLAService.TICKET_TYPES:
            raise HTTPException(
                status_code=400,
                detail="Invalid ticket type"
            )

        if priority not in SLAService.PRIORITIES:
            raise HTTPException(
                status_code=400,
                detail="Invalid priority"
            )

        if customer_type not in SLAService.CUSTOMER_TYPES:
            raise HTTPException(
                status_code=400,
                detail="Invalid customer type"
            )

    @staticmethod
    def create_rule(
        db: Session,
        rule_data
    ):

        SLAService.validate_rule_data(
            rule_data.ticket_type,
            rule_data.priority,
            rule_data.customer_type
        )

        rule = SLARule(
            rule_name=rule_data.rule_name,
            ticket_type=rule_data.ticket_type,
            priority=rule_data.priority,
            customer_type=rule_data.customer_type,
            response_time_minutes=(
                rule_data.response_time_minutes
            ),
            resolution_time_minutes=(
                rule_data.resolution_time_minutes
            ),
            is_active=True
        )

        return SLARepository.create_rule(
            db,
            rule
        )


    @staticmethod
    def find_rule_for_ticket(
        db: Session,
        ticket: SupportTicket
):

        customer = (
           db.query(Customer)
           .filter(
            Customer.id == ticket.customer_id
            )
            .first()
    )

        if not customer:
           raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

        rule = SLARepository.find_matching_rule(
           db=db,
           ticket_type=ticket.ticket_type,
           priority=ticket.priority,
           customer_type=customer.customer_type
    )

        if not rule:
         raise HTTPException(
            status_code=404,
            detail="No matching SLA rule found"
        )

        return rule


    @staticmethod
    def start_sla(
        db: Session,
        ticket: SupportTicket
):

        existing = SLARepository.get_ticket_sla(
            db,
            ticket.id
    )

        if existing:
         return existing

        rule = SLAService.find_rule_for_ticket(
           db,
           ticket
    )

        start_time = datetime.now(timezone.utc)

        deadline = (
            start_time
            + timedelta(
              minutes=rule.resolution_time_minutes
            )
    )

        ticket_sla = TicketSLA(
            ticket_id=ticket.id,
            sla_rule_id=rule.id,
            sla_start_time=start_time,
            sla_deadline=deadline,
            resolution_time_minutes=None,
            actual_resolution_time=None,
            sla_breached=False,
            escalation_status="Normal"
    )

        return SLARepository.create_ticket_sla(
           db,
           ticket_sla
    )


    @staticmethod
    def complete_sla(
        db: Session,
        ticket_id: int
):

        ticket_sla = SLARepository.get_ticket_sla(
           db,
           ticket_id
    )

        if not ticket_sla:
           return None

        resolved_at = datetime.now(timezone.utc)

        duration = (
            resolved_at
            - ticket_sla.sla_start_time
        )

        resolution_minutes = int(
           duration.total_seconds() / 60
        )

        ticket_sla.actual_resolution_time = resolved_at

        ticket_sla.resolution_time_minutes = (
            resolution_minutes
        )

        if resolved_at > ticket_sla.sla_deadline:

            ticket_sla.sla_breached = True
            ticket_sla.escalation_status = "Breached"

        else:

            ticket_sla.sla_breached = False
            ticket_sla.escalation_status = "Resolved"

        return SLARepository.update_ticket_sla(
           db,
           ticket_sla
        )
    

    @staticmethod
    def get_breached_tickets(
        db: Session
):

        now = datetime.now(timezone.utc)

        records = (
          db.query(
            TicketSLA,
            SupportTicket
        )
         .join(
            SupportTicket,
            TicketSLA.ticket_id
            == SupportTicket.id
        )
         .filter(
            TicketSLA.sla_deadline < now,
            SupportTicket.status.notin_(
                ["Resolved", "Closed"]
            )
        )
        .all()
    )

        results = []

        for sla, ticket in records:

           sla.sla_breached = True
           sla.escalation_status = "Breached"

        results.append({
            "ticket_id": ticket.id,
            "ticket_number": ticket.ticket_number,
            "priority": ticket.priority,
            "status": ticket.status,
            "sla_deadline": sla.sla_deadline,
            "sla_breached": True,
            "escalation_status": "Breached"
        })

        db.commit()

        return results