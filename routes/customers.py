from fastapi import (
    APIRouter,
    Depends,
    Query,
    status
)

from sqlalchemy.orm import Session

from database import get_db

from models.user_model import User

from schemas.customer_schema import (
    CustomerCreateRequest,
    CustomerResponse,
    CustomerUpdateRequest,
    CustomerContactUpdateRequest,
    CustomerAddressUpdateRequest,
    KYCStatusRequest,
    CustomerStatusRequest,
    CustomerHistoryResponse
)

from services.customer_service import (
    CustomerService
)

from utils.dependencies import (
    get_current_user,
    require_roles
)


router = APIRouter(
    prefix="/api/v1/customers",
    tags=["Customers"]
)


# --------------------------------------------------
# 1. CUSTOMER REGISTRATION
# --------------------------------------------------

@router.post(
    "",
    response_model=CustomerResponse,
    status_code=status.HTTP_201_CREATED
)
def create_customer(
    request: CustomerCreateRequest,
    current_user: User = Depends(
        require_roles(
            "Super Admin",
            "Operations Manager",
            "Support Agent",
            "Customer"
        )
    ),
    db: Session = Depends(get_db)
):

    return CustomerService.create_customer(
        db=db,
        user_id=current_user.id,
        full_name=request.full_name,
        email=request.email,
        phone=request.phone,
        address_line1=request.address_line1,
        address_line2=request.address_line2,
        city=request.city,
        state=request.state,
        postal_code=request.postal_code,
        country=request.country
    )


# --------------------------------------------------
# 2. CUSTOMER PROFILE
# --------------------------------------------------

@router.get(
    "/{customer_id}",
    response_model=CustomerResponse
)
def get_customer(
    customer_id: int,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db)
):

    return CustomerService.get_customer(
        db,
        customer_id
    )


# --------------------------------------------------
# 3. UPDATE CUSTOMER PROFILE
# --------------------------------------------------

@router.patch(
    "/{customer_id}",
    response_model=CustomerResponse
)
def update_customer_profile(
    customer_id: int,
    request: CustomerUpdateRequest,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db)
):

    return CustomerService.update_profile(
        db=db,
        customer_id=customer_id,
        full_name=request.full_name,
        phone=request.phone,
        changed_by=current_user.id
    )


# --------------------------------------------------
# 4. CONTACT DETAILS
# --------------------------------------------------

@router.patch(
    "/{customer_id}/contact",
    response_model=CustomerResponse
)
def update_contact_details(
    customer_id: int,
    request: CustomerContactUpdateRequest,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db)
):

    return CustomerService.update_contact(
        db=db,
        customer_id=customer_id,
        phone=request.phone,
        changed_by=current_user.id
    )


# --------------------------------------------------
# 5. ADDRESS MANAGEMENT
# --------------------------------------------------

@router.patch(
    "/{customer_id}/address",
    response_model=CustomerResponse
)
def update_address(
    customer_id: int,
    request: CustomerAddressUpdateRequest,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db)
):

    return CustomerService.update_address(
        db=db,
        customer_id=customer_id,
        address_line1=request.address_line1,
        address_line2=request.address_line2,
        city=request.city,
        state=request.state,
        postal_code=request.postal_code,
        country=request.country,
        changed_by=current_user.id
    )


# --------------------------------------------------
# 6. KYC STATUS
# --------------------------------------------------

@router.patch(
    "/{customer_id}/kyc",
    response_model=CustomerResponse
)
def update_kyc(
    customer_id: int,
    request: KYCStatusRequest,
    current_user: User = Depends(
        require_roles(
            "Super Admin",
            "Operations Manager",
            "Support Agent"
        )
    ),
    db: Session = Depends(get_db)
):

    return CustomerService.update_kyc_status(
        db=db,
        customer_id=customer_id,
        kyc_status=request.kyc_status,
        changed_by=current_user.id
    )


# --------------------------------------------------
# 7. ACTIVATE / DEACTIVATE CUSTOMER
# --------------------------------------------------

@router.patch(
    "/{customer_id}/status",
    response_model=CustomerResponse
)
def update_customer_status(
    customer_id: int,
    request: CustomerStatusRequest,
    current_user: User = Depends(
        require_roles(
            "Super Admin",
            "Operations Manager"
        )
    ),
    db: Session = Depends(get_db)
):

    return CustomerService.update_status(
        db=db,
        customer_id=customer_id,
        is_active=request.is_active,
        changed_by=current_user.id
    )


# --------------------------------------------------
# 8. CUSTOMER SEARCH + FILTER
# --------------------------------------------------

@router.get(
    "",
    response_model=list[CustomerResponse]
)
def search_customers(
    search: str | None = Query(
        default=None
    ),

    kyc_status: str | None = Query(
        default=None
    ),

    is_active: bool | None = Query(
        default=None
    ),

    city: str | None = Query(
        default=None
    ),

    current_user: User = Depends(
        require_roles(
            "Super Admin",
            "Operations Manager",
            "Support Agent"
        )
    ),

    db: Session = Depends(get_db)
):

    return CustomerService.search_customers(
        db=db,
        search=search,
        kyc_status=kyc_status,
        is_active=is_active,
        city=city
    )


# --------------------------------------------------
# 9. CUSTOMER HISTORY
# --------------------------------------------------

@router.get(
    "/{customer_id}/history",
    response_model=list[CustomerHistoryResponse]
)
def customer_history(
    customer_id: int,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db)
):

    return CustomerService.get_history(
        db,
        customer_id
    )