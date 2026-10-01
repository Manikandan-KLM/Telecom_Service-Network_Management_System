from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy.orm import Session

from models.notification_model import Notification

from repositories.notification_repository import (
    NotificationRepository
)


class NotificationService:

    # =========================================================
    # ALLOWED NOTIFICATION TYPES
    # =========================================================

    NOTIFICATION_TYPES = {
        "Ticket Assignment",
        "SLA Breach",
        "Network Outage",
        "Service Restoration",
        "Plan Expiry",
        "Usage Threshold",
        "SIM Suspension",
        "Maintenance Schedule"
    }

    # =========================================================
    # CREATE NOTIFICATION
    # =========================================================

    @staticmethod
    def create_notification(
        db: Session,
        user_id: int,
        notification_type: str,
        title: str,
        message: str,
        entity_type: str | None = None,
        entity_id: int | None = None
    ):

        # -----------------------------------------
        # Validate notification type
        # -----------------------------------------

        if notification_type not in (
            NotificationService.NOTIFICATION_TYPES
        ):

            raise HTTPException(
                status_code=400,
                detail=(
                    f"Invalid notification type. "
                    f"Allowed values: "
                    f"{', '.join(NotificationService.NOTIFICATION_TYPES)}"
                )
            )

        # -----------------------------------------
        # Create notification
        # -----------------------------------------

        notification = Notification(
            user_id=user_id,
            notification_type=notification_type,
            title=title,
            message=message,
            entity_type=entity_type,
            entity_id=entity_id,
            is_read=False
        )

        return NotificationRepository.create(
            db,
            notification
        )

    # =========================================================
    # TICKET ASSIGNMENT
    # =========================================================

    @staticmethod
    def notify_ticket_assignment(
        db: Session,
        user_id: int,
        ticket_id: int,
        ticket_number: str
    ):

        return NotificationService.create_notification(
            db=db,
            user_id=user_id,
            notification_type="Ticket Assignment",
            title="New Support Ticket Assigned",
            message=(
                f"Support ticket {ticket_number} "
                f"has been assigned to you."
            ),
            entity_type="SupportTicket",
            entity_id=ticket_id
        )

    # =========================================================
    # SLA BREACH
    # =========================================================

    @staticmethod
    def notify_sla_breach(
        db: Session,
        user_id: int,
        ticket_id: int,
        ticket_number: str
    ):

        return NotificationService.create_notification(
            db=db,
            user_id=user_id,
            notification_type="SLA Breach",
            title="SLA Breach Alert",
            message=(
                f"SLA has been breached for "
                f"support ticket {ticket_number}."
            ),
            entity_type="SupportTicket",
            entity_id=ticket_id
        )

    # =========================================================
    # NETWORK OUTAGE
    # =========================================================

    @staticmethod
    def notify_network_outage(
        db: Session,
        user_id: int,
        outage_id: int,
        outage_description: str
    ):

        return NotificationService.create_notification(
            db=db,
            user_id=user_id,
            notification_type="Network Outage",
            title="Network Outage Alert",
            message=(
                f"Network outage reported: "
                f"{outage_description}"
            ),
            entity_type="NetworkOutage",
            entity_id=outage_id
        )

    # =========================================================
    # SERVICE RESTORATION
    # =========================================================

    @staticmethod
    def notify_service_restoration(
        db: Session,
        user_id: int,
        outage_id: int,
        outage_description: str
    ):

        return NotificationService.create_notification(
            db=db,
            user_id=user_id,
            notification_type="Service Restoration",
            title="Service Restored",
            message=(
                f"Network service has been restored. "
                f"Details: {outage_description}"
            ),
            entity_type="NetworkOutage",
            entity_id=outage_id
        )

    # =========================================================
    # PLAN EXPIRY
    # =========================================================

    @staticmethod
    def notify_plan_expiry(
        db: Session,
        user_id: int,
        subscription_id: int,
        plan_name: str,
        expiry_date: str
    ):

        return NotificationService.create_notification(
            db=db,
            user_id=user_id,
            notification_type="Plan Expiry",
            title="Plan Expiry Reminder",
            message=(
                f"Your plan '{plan_name}' "
                f"will expire on {expiry_date}."
            ),
            entity_type="Subscription",
            entity_id=subscription_id
        )

    # =========================================================
    # USAGE THRESHOLD
    # =========================================================

    @staticmethod
    def notify_usage_threshold(
        db: Session,
        user_id: int,
        subscription_id: int,
        usage_type: str,
        percentage: float
    ):

        return NotificationService.create_notification(
            db=db,
            user_id=user_id,
            notification_type="Usage Threshold",
            title="Usage Threshold Alert",
            message=(
                f"Your {usage_type} usage has reached "
                f"{percentage:.2f}% of your plan quota."
            ),
            entity_type="Subscription",
            entity_id=subscription_id
        )

    # =========================================================
    # SIM SUSPENSION
    # =========================================================

    @staticmethod
    def notify_sim_suspension(
        db: Session,
        user_id: int,
        sim_id: int,
        sim_number: str
    ):

        return NotificationService.create_notification(
            db=db,
            user_id=user_id,
            notification_type="SIM Suspension",
            title="SIM Suspended",
            message=(
                f"Your SIM {sim_number} "
                f"has been suspended."
            ),
            entity_type="SIM",
            entity_id=sim_id
        )

    # =========================================================
    # MAINTENANCE SCHEDULE
    # =========================================================

    @staticmethod
    def notify_maintenance_schedule(
        db: Session,
        user_id: int,
        equipment_id: int,
        equipment_name: str,
        maintenance_date: str
    ):

        return NotificationService.create_notification(
            db=db,
            user_id=user_id,
            notification_type="Maintenance Schedule",
            title="Maintenance Scheduled",
            message=(
                f"Maintenance for {equipment_name} "
                f"is scheduled on {maintenance_date}."
            ),
            entity_type="NetworkEquipment",
            entity_id=equipment_id
        )

    # =========================================================
    # GET USER NOTIFICATIONS
    # =========================================================

    @staticmethod
    def get_user_notifications(
        db: Session,
        user_id: int
    ):

        return NotificationRepository.get_by_user(
            db,
            user_id
        )

    # =========================================================
    # GET UNREAD NOTIFICATIONS
    # =========================================================

    @staticmethod
    def get_unread_notifications(
        db: Session,
        user_id: int
    ):

        return NotificationRepository.get_unread_by_user(
            db,
            user_id
        )

    # =========================================================
    # MARK AS READ
    # =========================================================

    @staticmethod
    def mark_as_read(
        db: Session,
        notification_id: int,
        user_id: int
    ):

        notification = (
            NotificationRepository.get_by_id(
                db,
                notification_id
            )
        )

        if not notification:

            raise HTTPException(
                status_code=404,
                detail="Notification not found"
            )

        # -----------------------------------------
        # User ownership
        # -----------------------------------------

        if notification.user_id != user_id:

            raise HTTPException(
                status_code=403,
                detail="You cannot modify this notification"
            )

        # -----------------------------------------
        # Already read
        # -----------------------------------------

        if notification.is_read:

            return notification

        # -----------------------------------------
        # Mark read
        # -----------------------------------------

        notification.is_read = True

        notification.read_at = (
            datetime.now(timezone.utc)
        )

        return NotificationRepository.update(
            db,
            notification
        )