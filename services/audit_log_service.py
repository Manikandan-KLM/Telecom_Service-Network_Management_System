import json

from sqlalchemy.orm import Session

from models.audit_log_model import AuditLog
from repositories.audit_log_repository import (
    AuditLogRepository
)


class AuditLogService:

    @staticmethod
    def create_log(
        db: Session,
        user_id: int | None,
        action: str,
        entity: str,
        entity_id: int | str | None = None,
        previous_value=None,
        new_value=None
    ):

        previous_json = None
        new_json = None

        if previous_value is not None:

            if isinstance(
                previous_value,
                str
            ):
                previous_json = previous_value

            else:
                previous_json = json.dumps(
                    previous_value,
                    default=str
                )

        if new_value is not None:

            if isinstance(
                new_value,
                str
            ):
                new_json = new_value

            else:
                new_json = json.dumps(
                    new_value,
                    default=str
                )

        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            entity=entity,
            entity_id=(
                str(entity_id)
                if entity_id is not None
                else None
            ),
            previous_value=previous_json,
            new_value=new_json
        )

        return AuditLogRepository.create(
            db,
            audit_log
        )

    @staticmethod
    def get_by_id(
        db: Session,
        audit_id: int
    ):

        return AuditLogRepository.get_by_id(
            db,
            audit_id
        )

    @staticmethod
    def get_all(
        db: Session,
        user_id: int | None = None,
        action: str | None = None,
        entity: str | None = None,
        entity_id: str | None = None
    ):

        return AuditLogRepository.get_all(
            db=db,
            user_id=user_id,
            action=action,
            entity=entity,
            entity_id=entity_id
        )

    @staticmethod
    def get_by_entity(
        db: Session,
        entity: str,
        entity_id: str
    ):

        return AuditLogRepository.get_by_entity(
            db=db,
            entity=entity,
            entity_id=entity_id
        )

    @staticmethod
    def get_by_user(
        db: Session,
        user_id: int
    ):

        return AuditLogRepository.get_by_user(
            db=db,
            user_id=user_id
        )