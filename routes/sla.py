from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database import get_db

from models.user_model import User

from schemas.sla_schema import (
    SLARuleCreateRequest,
    SLARuleResponse,
    TicketSLAResponse
)



from repositories.sla_repository import SLARepository

from services.sla_service import SLAService

from utils.dependencies import (
    get_current_user,
    require_roles
)


router = APIRouter(
    prefix="/api/v1/sla",
    tags=["SLA Management"]
)

@router.post(
    "/rules",
    response_model=SLARuleResponse
)
def create_sla_rule(
    request: SLARuleCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Super Admin",
            "Operations Manager"
        )
    )
):

    return SLAService.create_rule(
        db,
        request
    )

@router.get(
    "/tickets/{ticket_id}",
    response_model=TicketSLAResponse
)
def get_ticket_sla(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    )
):

    sla = SLARepository.get_ticket_sla(
        db,
        ticket_id
    )

    if not sla:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=404,
            detail="SLA record not found"
        )

    return sla




@router.get(
    "/monitor/breached"
)
def get_breached_tickets(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Super Admin",
            "Operations Manager",
            "Support Agent"
        )
    )
):

    return {
        "tickets": SLAService.get_breached_tickets(
            db
        )
    }


@router.get(
    "/monitor/soon-to-breach"
)
def get_soon_to_breach_tickets(
    warning_minutes: int = Query(
        default=30,
        ge=1,
        le=1440
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Super Admin",
            "Operations Manager",
            "Support Agent"
        )
    )
):

    return {
        "warning_minutes": warning_minutes,
        "tickets": SLAService.get_soon_to_breach_tickets(
            db,
            warning_minutes
        )
    }

@router.get(
    "/monitor"
)
def monitor_sla(
    warning_minutes: int = Query(
        default=30,
        ge=1,
        le=1440
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Super Admin",
            "Operations Manager",
            "Support Agent"
        )
    )
):

    return SLAService.get_sla_monitoring(
        db,
        warning_minutes
    )