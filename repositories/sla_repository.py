from sqlalchemy.orm import Session

from models.sla_rule_model import SLARule
from models.ticket_sla_model import TicketSLA


class SLARepository:

    @staticmethod
    def create_rule(
        db: Session,
        rule: SLARule
    ):

        db.add(rule)
        db.commit()
        db.refresh(rule)

        return rule

    @staticmethod
    def get_rule_by_id(
        db: Session,
        rule_id: int
    ):

        return (
            db.query(SLARule)
            .filter(
                SLARule.id == rule_id
            )
            .first()
        )

    @staticmethod
    def find_matching_rule(
        db: Session,
        ticket_type: str,
        priority: str,
        customer_type: str
    ):

        return (
            db.query(SLARule)
            .filter(
                SLARule.ticket_type == ticket_type,
                SLARule.priority == priority,
                SLARule.customer_type == customer_type,
                SLARule.is_active == True
            )
            .first()
        )

    @staticmethod
    def create_ticket_sla(
        db: Session,
        ticket_sla: TicketSLA
    ):

        db.add(ticket_sla)
        db.commit()
        db.refresh(ticket_sla)

        return ticket_sla

    @staticmethod
    def get_ticket_sla(
        db: Session,
        ticket_id: int
    ):

        return (
            db.query(TicketSLA)
            .filter(
                TicketSLA.ticket_id == ticket_id
            )
            .first()
        )

    @staticmethod
    def update_ticket_sla(
        db: Session,
        ticket_sla: TicketSLA
    ):

        db.commit()
        db.refresh(ticket_sla)

        return ticket_sla