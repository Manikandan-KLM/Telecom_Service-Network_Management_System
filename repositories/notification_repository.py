from sqlalchemy.orm import Session

from models.notification_model import Notification


class NotificationRepository:

    # =========================================================
    # CREATE
    # =========================================================

    @staticmethod
    def create(
        db: Session,
        notification: Notification
    ):

        db.add(notification)

        db.commit()

        db.refresh(notification)

        return notification

    # =========================================================
    # GET BY ID
    # =========================================================

    @staticmethod
    def get_by_id(
        db: Session,
        notification_id: int
    ):

        return (
            db.query(Notification)
            .filter(
                Notification.id == notification_id
            )
            .first()
        )

    # =========================================================
    # GET USER NOTIFICATIONS
    # =========================================================

    @staticmethod
    def get_by_user(
        db: Session,
        user_id: int
    ):

        return (
            db.query(Notification)
            .filter(
                Notification.user_id == user_id
            )
            .order_by(
                Notification.created_at.desc()
            )
            .all()
        )

    # =========================================================
    # GET UNREAD
    # =========================================================

    @staticmethod
    def get_unread_by_user(
        db: Session,
        user_id: int
    ):

        return (
            db.query(Notification)
            .filter(
                Notification.user_id == user_id,
                Notification.is_read == False
            )
            .order_by(
                Notification.created_at.desc()
            )
            .all()
        )

    # =========================================================
    # UPDATE
    # =========================================================

    @staticmethod
    def update(
        db: Session,
        notification: Notification
    ):

        db.commit()

        db.refresh(notification)

        return notification