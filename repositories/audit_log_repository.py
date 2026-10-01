from sqlalchemy.orm import Session

from models.audit_log_model import AuditLog


class AuditLogRepository:

    @staticmethod
    def create(
        db: Session,
        audit_log: AuditLog
    ):

        db.add(audit_log)
        db.commit()
        db.refresh(audit_log)

        return audit_log

    @staticmethod
    def get_by_id(
        db: Session,
        audit_id: int
    ):

        return (
            db.query(AuditLog)
            .filter(
                AuditLog.id == audit_id
            )
            .first()
        )

    @staticmethod
    def get_all(
        db: Session,
        user_id: int | None = None,
        action: str | None = None,
        entity: str | None = None,
        entity_id: str | None = None
    ):

        query = db.query(AuditLog)

        if user_id is not None:
            query = query.filter(
                AuditLog.user_id == user_id
            )

        if action:
            query = query.filter(
                AuditLog.action == action
            )

        if entity:
            query = query.filter(
                AuditLog.entity == entity
            )

        if entity_id:
            query = query.filter(
                AuditLog.entity_id == entity_id
            )

        return (
            query
            .order_by(
                AuditLog.created_at.desc()
            )
            .all()
        )

    @staticmethod
    def get_by_entity(
        db: Session,
        entity: str,
        entity_id: str
    ):

        return (
            db.query(AuditLog)
            .filter(
                AuditLog.entity == entity,
                AuditLog.entity_id == entity_id
            )
            .order_by(
                AuditLog.created_at.desc()
            )
            .all()
        )

    @staticmethod
    def get_by_user(
        db: Session,
        user_id: int
    ):

        return (
            db.query(AuditLog)
            .filter(
                AuditLog.user_id == user_id
            )
            .order_by(
                AuditLog.created_at.desc()
            )
            .all()
        )