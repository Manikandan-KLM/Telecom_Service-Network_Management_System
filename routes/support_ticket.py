from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database import get_db

from schemas.support_ticket_schema import (
    SupportTicketCreateRequest,
    SupportTicketAssignRequest,
    SupportTicketStatusRequest,
    SupportTicketResponse
)

from services.support_ticket_service import (
    SupportTicketService
)

from repositories.support_ticket_repository import (
    SupportTicketRepository
)

from utils.dependencies import (
    get_current_user,
    require_roles
)

from models.user_model import User

from schemas.support_ticket_schema import (
    AgentAssignmentRequest,
    TechnicianAssignmentRequest,
    PriorityUpdateRequest,
    EscalationRequest,
    InternalCommentRequest,
    SupportTicketResponse,
    TicketHistoryResponse,
    TicketCommentResponse,
    SupportTicketStatusRequest
)

from services.support_ticket_service import (
    SupportTicketService
)

from utils.dependencies import (
    get_current_user,
    require_roles
)


router = APIRouter(
    prefix="/api/v1/support-tickets",
    tags=["Customer Support Tickets"]
)


# =====================================================
# CREATE TICKET
# =====================================================

@router.post(
    "/",
    response_model=SupportTicketResponse
)
def create_ticket(
    request: SupportTicketCreateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    # Customer should create ticket for himself
    if current_user.role == "Customer":

        from repositories.customer_repository import (
            CustomerRepository
        )

        customer = (
            CustomerRepository.get_by_user_id(
                db,
                current_user.id
            )
        )

        if not customer:

            from fastapi import HTTPException

            raise HTTPException(
                status_code=404,
                detail="Customer profile not found"
            )

        customer_id = customer.id

    else:

        raise_permission = (
            current_user.role not in {
                "Super Admin",
                "Operations Manager",
                "Support Agent"
            }
        )

        if raise_permission:

            from fastapi import HTTPException

            raise HTTPException(
                status_code=403,
                detail="You do not have permission"
            )

        raise_id = None

        # Staff can use customer_id only if we
        # add it to schema later.
        from fastapi import HTTPException

        raise HTTPException(
            status_code=400,
            detail=(
                "Staff ticket creation should "
                "use a customer-specific endpoint"
            )
        )

    return SupportTicketService.create_ticket(
        db=db,
        customer_id=customer_id,
        ticket_type=request.ticket_type,
        subject=request.subject,
        description=request.description,
        priority=request.priority
    )


# =====================================================
# GET SINGLE TICKET
# =====================================================

@router.get(
    "/{ticket_id}",
    response_model=SupportTicketResponse
)
def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    ticket = SupportTicketService.get_ticket(
        db,
        ticket_id
    )

    # Customer can see only own ticket
    if current_user.role == "Customer":

        from repositories.customer_repository import (
            CustomerRepository
        )

        customer = (
            CustomerRepository.get_by_user_id(
                db,
                current_user.id
            )
        )

        if not customer or ticket.customer_id != customer.id:

            from fastapi import HTTPException

            raise HTTPException(
                status_code=403,
                detail="You can access only your tickets"
            )

    return ticket


# =====================================================
# GET MY TICKETS
# =====================================================

@router.get(
    "/my/tickets",
    response_model=list[SupportTicketResponse]
)
def get_my_tickets(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    if current_user.role != "Customer":

        from fastapi import HTTPException

        raise HTTPException(
            status_code=403,
            detail="Only customers can use this endpoint"
        )

    from repositories.customer_repository import (
        CustomerRepository
    )

    customer = (
        CustomerRepository.get_by_user_id(
            db,
            current_user.id
        )
    )

    if not customer:

        from fastapi import HTTPException

        raise HTTPException(
            status_code=404,
            detail="Customer profile not found"
        )

    return SupportTicketService.get_customer_tickets(
        db,
        customer.id
    )


# =====================================================
# GET ALL TICKETS
# =====================================================

@router.get(
    "/",
    response_model=list[SupportTicketResponse]
)
def get_all_tickets(
    status: str | None = Query(None),
    ticket_type: str | None = Query(None),
    priority: str | None = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Super Admin",
            "Operations Manager",
            "Support Agent"
        )
    )
):

    return SupportTicketRepository.get_all(
        db,
        status=status,
        ticket_type=ticket_type,
        priority=priority
    )


# =====================================================
# ASSIGN TICKET
# =====================================================

@router.patch(
    "/{ticket_id}/assign",
    response_model=SupportTicketResponse
)
def assign_ticket(
    ticket_id: int,
    request: SupportTicketAssignRequest,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Super Admin",
            "Operations Manager",
            "Support Agent"
        )
    )
):

    return SupportTicketService.assign_ticket(
        db=db,
        ticket_id=ticket_id,
        assigned_to=request.assigned_to
    )


# =====================================================
# UPDATE STATUS
# =====================================================

@router.patch(
    "/{ticket_id}/status",
    response_model=SupportTicketResponse
)
def update_ticket_status(
    ticket_id: int,
    request: SupportTicketStatusRequest,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Super Admin",
            "Operations Manager",
            "Support Agent",
            "Field Technician"
        )
    )
):

    return SupportTicketService.update_status(
        db=db,
        ticket_id=ticket_id,
        status=request.status,
        resolution_notes=request.resolution_notes
    )


# =====================================================
# MY ASSIGNED TICKETS
# =====================================================

@router.get(
    "/assigned/me",
    response_model=list[SupportTicketResponse]
)
def get_my_assigned_tickets(
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Support Agent",
            "Operations Manager",
            "Super Admin"
        )
    )
):

    return SupportTicketService.get_assigned_tickets(
        db,
        current_user.id
    )


@router.patch(
    "/{ticket_id}/assign-agent",
    response_model=SupportTicketResponse
)
def assign_agent(
    ticket_id: int,
    request: AgentAssignmentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Super Admin",
            "Operations Manager"
        )
    )
):

    return SupportTicketService.assign_agent(
        db=db,
        ticket_id=ticket_id,
        agent_id=request.agent_id,
        changed_by=current_user.id
    )


@router.patch(
    "/{ticket_id}/assign-technician",
    response_model=SupportTicketResponse
)
def assign_technician(
    ticket_id: int,
    request: TechnicianAssignmentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Super Admin",
            "Operations Manager",
            "Support Agent"
        )
    )
):

    return SupportTicketService.assign_technician(
        db=db,
        ticket_id=ticket_id,
        technician_id=request.technician_id,
        changed_by=current_user.id
    )


@router.patch(
    "/{ticket_id}/priority",
    response_model=SupportTicketResponse
)
def update_priority(
    ticket_id: int,
    request: PriorityUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Super Admin",
            "Operations Manager",
            "Support Agent"
        )
    )
):

    return SupportTicketService.update_priority(
        db=db,
        ticket_id=ticket_id,
        priority=request.priority,
        changed_by=current_user.id
    )


@router.patch(
    "/{ticket_id}/escalate",
    response_model=SupportTicketResponse
)
def escalate_ticket(
    ticket_id: int,
    request: EscalationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Super Admin",
            "Operations Manager",
            "Support Agent"
        )
    )
):

    return SupportTicketService.escalate_ticket(
        db=db,
        ticket_id=ticket_id,
        reason=request.escalation_reason,
        changed_by=current_user.id
    )


@router.post(
    "/{ticket_id}/comments",
    response_model=TicketCommentResponse
)
def add_internal_comment(
    ticket_id: int,
    request: InternalCommentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Super Admin",
            "Operations Manager",
            "Support Agent",
            "Network Engineer",
            "Field Technician"
        )
    )
):

    return SupportTicketService.add_internal_comment(
        db=db,
        ticket_id=ticket_id,
        user_id=current_user.id,
        comment_text=request.comment
    )


@router.get(
    "/{ticket_id}/comments",
    response_model=list[TicketCommentResponse]
)
def get_internal_comments(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Super Admin",
            "Operations Manager",
            "Support Agent",
            "Network Engineer",
            "Field Technician"
        )
    )
):

    return SupportTicketService.get_internal_comments(
        db,
        ticket_id
    )

@router.patch(
    "/{ticket_id}/resolve",
    response_model=SupportTicketResponse
)
def resolve_ticket(
    ticket_id: int,
    request: SupportTicketStatusRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Super Admin",
            "Operations Manager",
            "Support Agent",
            "Field Technician"
        )
    )
):

    return SupportTicketService.resolve_ticket(
        db=db,
        ticket_id=ticket_id,
        resolution_notes=request.resolution_notes or "",
        changed_by=current_user.id
    )


@router.get(
    "/{ticket_id}/history",
    response_model=list[TicketHistoryResponse]
)
def get_ticket_history(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Super Admin",
            "Operations Manager",
            "Support Agent",
            "Network Engineer",
            "Field Technician"
        )
    )
):

    return SupportTicketService.get_ticket_history(
        db,
        ticket_id
    )


@router.get(
    "/assigned/agent",
    response_model=list[SupportTicketResponse]
)
def get_agent_tickets(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Support Agent"
        )
    )
):

    return SupportTicketRepository.get_by_agent(
        db,
        current_user.id
    )


@router.get(
    "/assigned/technician",
    response_model=list[SupportTicketResponse]
)
def get_technician_tickets(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Field Technician"
        )
    )
):

    return SupportTicketRepository.get_by_technician(
        db,
        current_user.id
    )