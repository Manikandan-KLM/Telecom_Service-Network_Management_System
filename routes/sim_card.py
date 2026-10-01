from fastapi import (
    APIRouter,
    Depends,
    Query,
    status
)

from sqlalchemy.orm import Session

from database import get_db
from models.user_model import User

from schemas.sim_card_schema import (
    SIMCardCreateRequest,
    SIMCardUpdateRequest,
    SIMStatusRequest,
    SIMReplacementRequest,
    SIMCardResponse,
    SIMReplacementHistoryResponse
)

from services.sim_card_service import (
    SIMCardService
)

from utils.dependencies import (
    get_current_user,
    require_roles
)


router = APIRouter(
    prefix="/api/v1/sims",
    tags=["SIM Cards"]
)


# --------------------------------------------------
# CREATE SIM
# --------------------------------------------------

@router.post(
    "",
    response_model=SIMCardResponse,
    status_code=status.HTTP_201_CREATED
)
def create_sim(
    request: SIMCardCreateRequest,
    current_user: User = Depends(
        require_roles(
            "Super Admin",
            "Operations Manager"
        )
    ),
    db: Session = Depends(get_db)
):

    return SIMCardService.create_sim(
        db=db,
        sim_number=request.sim_number,
        sim_type=request.sim_type,
        customer_id=request.customer_id,
        plan_id=request.plan_id
    )


# --------------------------------------------------
# SEARCH / FILTER SIMS
# --------------------------------------------------

@router.get(
    "",
    response_model=list[SIMCardResponse]
)
def search_sims(
    search: str | None = Query(
        default=None
    ),

    sim_type: str | None = Query(
        default=None
    ),

    sim_status: str | None = Query(
        default=None
    ),

    customer_id: int | None = Query(
        default=None
    ),

    plan_id: int | None = Query(
        default=None
    ),

    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(get_db)
):

    return SIMCardService.search_sims(
        db=db,
        search=search,
        sim_type=sim_type,
        status=sim_status,
        customer_id=customer_id,
        plan_id=plan_id
    )


# --------------------------------------------------
# GET SIM
# --------------------------------------------------

@router.get(
    "/{sim_id}",
    response_model=SIMCardResponse
)
def get_sim(
    sim_id: int,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db)
):

    return SIMCardService.get_sim(
        db,
        sim_id
    )


# --------------------------------------------------
# UPDATE SIM
# --------------------------------------------------

@router.patch(
    "/{sim_id}",
    response_model=SIMCardResponse
)
def update_sim(
    sim_id: int,
    request: SIMCardUpdateRequest,
    current_user: User = Depends(
        require_roles(
            "Super Admin",
            "Operations Manager"
        )
    ),
    db: Session = Depends(get_db)
):

    return SIMCardService.update_sim(
        db=db,
        sim_id=sim_id,
        sim_type=request.sim_type,
        customer_id=request.customer_id,
        plan_id=request.plan_id
    )


# --------------------------------------------------
# CHANGE STATUS
# --------------------------------------------------

@router.patch(
    "/{sim_id}/status",
    response_model=SIMCardResponse
)
def change_sim_status(
    sim_id: int,
    request: SIMStatusRequest,
    current_user: User = Depends(
        require_roles(
            "Super Admin",
            "Operations Manager",
            "Network Engineer"
        )
    ),
    db: Session = Depends(get_db)
):

    return SIMCardService.update_status(
        db=db,
        sim_id=sim_id,
        new_status=request.status
    )


# --------------------------------------------------
# REPLACE SIM
# --------------------------------------------------

@router.post(
    "/{sim_id}/replace",
    response_model=SIMCardResponse
)
def replace_sim(
    sim_id: int,
    request: SIMReplacementRequest,
    current_user: User = Depends(
        require_roles(
            "Super Admin",
            "Operations Manager",
            "Support Agent",
            "Field Technician"
        )
    ),
    db: Session = Depends(get_db)
):

    return SIMCardService.replace_sim(
        db=db,
        old_sim_id=sim_id,
        new_sim_id=request.new_sim_id,
        reason=request.reason,
        remarks=request.remarks,
        replaced_by=current_user.id
    )


# --------------------------------------------------
# REPLACEMENT HISTORY BY CUSTOMER
# --------------------------------------------------

@router.get(
    "/history/customer/{customer_id}",
    response_model=list[SIMReplacementHistoryResponse]
)
def customer_replacement_history(
    customer_id: int,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db)
):

    return SIMCardService.get_replacement_history(
        db=db,
        customer_id=customer_id
    )


# --------------------------------------------------
# REPLACEMENT HISTORY BY SIM
# --------------------------------------------------

@router.get(
    "/history/sim/{sim_id}",
    response_model=list[SIMReplacementHistoryResponse]
)
def sim_replacement_history(
    sim_id: int,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db)
):

    return SIMCardService.get_replacement_history(
        db=db,
        sim_id=sim_id
    )