from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models.user_model import User

from schemas.audit_log_schema import (
    AuditLogResponse
)

from services.audit_log_service import (
    AuditLogService
)

from utils.dependencies import (
    require_roles
)


router = APIRouter(
    prefix="/api/v1/audit-logs",
    tags=["Audit Logs"]
)


@router.get(
    "/",
    response_model=list[AuditLogResponse]
)
def get_audit_logs(
    user_id: int | None = None,
    action: str | None = None,
    entity: str | None = None,
    entity_id: str | None = None,

    db: Session = Depends(get_db),

    current_user: User = Depends(
        require_roles(
            "Super Admin",
            "Operations Manager"
        )
    )
):

    return AuditLogService.get_all(
        db=db,
        user_id=user_id,
        action=action,
        entity=entity,
        entity_id=entity_id
    )


@router.get(
    "/user/{user_id}",
    response_model=list[AuditLogResponse]
)
def get_user_audit_logs(
    user_id: int,

    db: Session = Depends(get_db),

    current_user: User = Depends(
        require_roles(
            "Super Admin",
            "Operations Manager"
        )
    )
):

    return AuditLogService.get_by_user(
        db=db,
        user_id=user_id
    )


@router.get(
    "/entity/{entity}/{entity_id}",
    response_model=list[AuditLogResponse]
)
def get_entity_audit_logs(
    entity: str,
    entity_id: str,

    db: Session = Depends(get_db),

    current_user: User = Depends(
        require_roles(
            "Super Admin",
            "Operations Manager"
        )
    )
):

    return AuditLogService.get_by_entity(
        db=db,
        entity=entity,
        entity_id=entity_id
    )


@router.get(
    "/{audit_id}",
    response_model=AuditLogResponse
)
def get_audit_log(
    audit_id: int,

    db: Session = Depends(get_db),

    current_user: User = Depends(
        require_roles(
            "Super Admin",
            "Operations Manager"
        )
    )
):

    return AuditLogService.get_by_id(
        db=db,
        audit_id=audit_id
    )