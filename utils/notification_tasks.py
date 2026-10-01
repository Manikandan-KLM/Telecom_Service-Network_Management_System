from sqlalchemy.orm import Session

from database import SessionLocal

from services.notification_service import (
    NotificationService
)


def send_ticket_assignment_notification(
    user_id: int,
    ticket_id: int,
    ticket_number: str
):
    """
    Background task for ticket assignment.
    """

    db: Session = SessionLocal()

    try:

        NotificationService.notify_ticket_assignment(
            db=db,
            user_id=user_id,
            ticket_id=ticket_id,
            ticket_number=ticket_number
        )

    finally:

        db.close()


def send_sla_breach_notification(
    user_id: int,
    ticket_id: int,
    ticket_number: str
):
    """
    Background task for SLA breach.
    """

    db: Session = SessionLocal()

    try:

        NotificationService.notify_sla_breach(
            db=db,
            user_id=user_id,
            ticket_id=ticket_id,
            ticket_number=ticket_number
        )

    finally:

        db.close()


def send_network_outage_notification(
    user_id: int,
    outage_id: int,
    outage_description: str
):
    """
    Background task for network outage.
    """

    db: Session = SessionLocal()

    try:

        NotificationService.notify_network_outage(
            db=db,
            user_id=user_id,
            outage_id=outage_id,
            outage_description=outage_description
        )

    finally:

        db.close()


def send_service_restoration_notification(
    user_id: int,
    outage_id: int,
    outage_description: str
):
    """
    Background task for service restoration.
    """

    db: Session = SessionLocal()

    try:

        NotificationService.notify_service_restoration(
            db=db,
            user_id=user_id,
            outage_id=outage_id,
            outage_description=outage_description
        )

    finally:

        db.close()