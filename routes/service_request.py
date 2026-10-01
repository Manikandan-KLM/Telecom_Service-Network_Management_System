from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database import get_db
from models.user_model import User

from schemas.service_request_schema import (
    ServiceRequestCreateRequest,
    ServiceRequestAssignRequest,
    ServiceRequestStatusRequest,
    ServiceRequestResponse,
    ServiceRequestHistoryResponse
)

from services.service_request_service import (
    ServiceRequestService
)

from repositories.service_request_repository import (
    ServiceRequestRepository
)

from utils.dependencies import (
    get_current_user,
    require_roles
)


router = APIRouter(
    prefix="/api/v1/service-requests",
    tags=["Service Requests"]
)


# =========================================================
# 1. CREATE SERVICE REQUEST - CUSTOMER
# =========================================================

@router.post(
    "/",
    response_model=ServiceRequestResponse,
    status_code=201
)
def create_service_request(
    request_data: ServiceRequestCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("Customer")
    )
):
    """
    Customer creates a service request.
    """

    # -----------------------------------------
    # Find customer linked with logged-in user
    # -----------------------------------------

    from models.customer_model import Customer

    customer = (
        db.query(Customer)
        .filter(
            Customer.user_id == current_user.id
        )
        .first()
    )

    if not customer:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=404,
            detail="Customer profile not found"
        )

    return ServiceRequestService.create_request(
        db=db,
        customer_id=customer.id,
        request_type=request_data.request_type,
        description=request_data.description,
        priority=request_data.priority,
        sim_id=request_data.sim_id,
        subscription_id=request_data.subscription_id,
        device_id=request_data.device_id
    )


# =========================================================
# 2. CREATE SERVICE REQUEST - STAFF
# =========================================================

@router.post(
    "/staff",
    response_model=ServiceRequestResponse,
    status_code=201
)
def create_service_request_by_staff(
    customer_id: int,
    request_data: ServiceRequestCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Super Admin",
            "Operations Manager",
            "Support Agent"
        )
    )
):
    """
    Staff can create a service request on behalf of a customer.
    """

    return ServiceRequestService.create_request(
        db=db,
        customer_id=customer_id,
        request_type=request_data.request_type,
        description=request_data.description,
        priority=request_data.priority,
        sim_id=request_data.sim_id,
        subscription_id=request_data.subscription_id,
        device_id=request_data.device_id
    )


# =========================================================
# 3. GET MY SERVICE REQUESTS
# =========================================================

@router.get(
    "/my",
    response_model=list[ServiceRequestResponse]
)
def get_my_service_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("Customer")
    )
):
    """
    Customer can view their own service requests.
    """

    from models.customer_model import Customer

    customer = (
        db.query(Customer)
        .filter(
            Customer.user_id == current_user.id
        )
        .first()
    )

    if not customer:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=404,
            detail="Customer profile not found"
        )

    return ServiceRequestService.get_customer_requests(
        db=db,
        customer_id=customer.id
    )


# =========================================================
# 4. GET ALL SERVICE REQUESTS
# =========================================================

@router.get(
    "/",
    response_model=list[ServiceRequestResponse]
)
def get_all_service_requests(
    status: str | None = Query(
        default=None
    ),
    request_type: str | None = Query(
        default=None
    ),
    priority: str | None = Query(
        default=None
    ),
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
    """
    Staff can view and filter all service requests.
    """

    return ServiceRequestRepository.get_all(
        db=db,
        status=status,
        request_type=request_type,
        priority=priority
    )


# =========================================================
# 5. GET ASSIGNED REQUESTS
# =========================================================

@router.get(
    "/assigned/me",
    response_model=list[ServiceRequestResponse]
)
def get_my_assigned_requests(
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
    """
    Get service requests assigned to logged-in staff.
    """

    return ServiceRequestService.get_assigned_requests(
        db=db,
        user_id=current_user.id
    )


# =========================================================
# 6. ASSIGN SERVICE REQUEST
# =========================================================

@router.patch(
    "/{request_id}/assign",
    response_model=ServiceRequestResponse
)
def assign_service_request(
    request_id: int,
    request_data: ServiceRequestAssignRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Super Admin",
            "Operations Manager",
            "Support Agent"
        )
    )
):
    """
    Assign service request to a staff member.
    """

    return ServiceRequestService.assign_request(
        db=db,
        request_id=request_id,
        assigned_to=request_data.assigned_to,
        changed_by=current_user.id
    )


# =========================================================
# 7. UPDATE SERVICE REQUEST STATUS
# =========================================================

@router.patch(
    "/{request_id}/status",
    response_model=ServiceRequestResponse
)
def update_service_request_status(
    request_id: int,
    request_data: ServiceRequestStatusRequest,
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
    """
    Update service request status.
    """

    return ServiceRequestService.update_status(
        db=db,
        request_id=request_id,
        new_status=request_data.status,
        changed_by=current_user.id,
        remarks=request_data.remarks,
        rejection_reason=request_data.rejection_reason,
        completion_notes=request_data.completion_notes
    )


# =========================================================
# 8. GET SERVICE REQUEST HISTORY
# =========================================================

@router.get(
    "/{request_id}/history",
    response_model=list[ServiceRequestHistoryResponse]
)
def get_service_request_history(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    )
):
    """
    Get complete status history of a service request.
    """

    return ServiceRequestService.get_request_history(
        db=db,
        request_id=request_id
    )


# =========================================================
# 9. GET SINGLE SERVICE REQUEST
# =========================================================

@router.get(
    "/{request_id}",
    response_model=ServiceRequestResponse
)
def get_service_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    )
):
    """
    Get a single service request.
    """

    return ServiceRequestService.get_request(
        db=db,
        request_id=request_id
    )