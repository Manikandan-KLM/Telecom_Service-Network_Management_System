from fastapi import (
    APIRouter,
    Depends,
    Query,
    status
)

from sqlalchemy.orm import Session

from database import get_db

from models.user_model import User

from schemas.service_plan_schema import (
    ServicePlanCreateRequest,
    ServicePlanUpdateRequest,
    ServicePlanStatusRequest,
    ServicePlanResponse,
    ServicePlanComparisonResponse
)

from services.service_plan_service import (
    ServicePlanService
)

from utils.dependencies import (
    get_current_user,
    require_roles
)


router = APIRouter(
    prefix="/api/v1/plans",
    tags=["Service Plans"]
)


# --------------------------------------------------
# 1. CREATE PLAN
# --------------------------------------------------

@router.post(
    "",
    response_model=ServicePlanResponse,
    status_code=status.HTTP_201_CREATED
)
def create_plan(
    request: ServicePlanCreateRequest,

    current_user: User = Depends(
        require_roles(
            "Super Admin",
            "Operations Manager"
        )
    ),

    db: Session = Depends(get_db)
):

    return ServicePlanService.create_plan(
        db=db,
        plan_code=request.plan_code,
        plan_name=request.plan_name,
        plan_type=request.plan_type,
        data_limit=request.data_limit,
        voice_limit=request.voice_limit,
        sms_limit=request.sms_limit,
        validity_days=request.validity_days,
        price=request.price,
        description=request.description
    )


# --------------------------------------------------
# 2. GET SINGLE PLAN
# --------------------------------------------------

@router.get(
    "/{plan_id}",
    response_model=ServicePlanResponse
)
def get_plan(
    plan_id: int,

    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(get_db)
):

    return ServicePlanService.get_plan(
        db,
        plan_id
    )


# --------------------------------------------------
# 3. UPDATE PLAN
# --------------------------------------------------

@router.patch(
    "/{plan_id}",
    response_model=ServicePlanResponse
)
def update_plan(
    plan_id: int,
    request: ServicePlanUpdateRequest,

    current_user: User = Depends(
        require_roles(
            "Super Admin",
            "Operations Manager"
        )
    ),

    db: Session = Depends(get_db)
):

    return ServicePlanService.update_plan(
        db=db,
        plan_id=plan_id,
        plan_name=request.plan_name,
        data_limit=request.data_limit,
        voice_limit=request.voice_limit,
        sms_limit=request.sms_limit,
        validity_days=request.validity_days,
        price=request.price,
        description=request.description
    )


# --------------------------------------------------
# 4. ACTIVATE / DEACTIVATE
# --------------------------------------------------

@router.patch(
    "/{plan_id}/status",
    response_model=ServicePlanResponse
)
def update_plan_status(
    plan_id: int,
    request: ServicePlanStatusRequest,

    current_user: User = Depends(
        require_roles(
            "Super Admin",
            "Operations Manager"
        )
    ),

    db: Session = Depends(get_db)
):

    return ServicePlanService.update_status(
        db=db,
        plan_id=plan_id,
        is_active=request.is_active
    )


# --------------------------------------------------
# 5. SEARCH + FILTER
# --------------------------------------------------

@router.get(
    "",
    response_model=list[ServicePlanResponse]
)
def search_plans(
    search: str | None = Query(
        default=None
    ),

    plan_type: str | None = Query(
        default=None
    ),

    is_active: bool | None = Query(
        default=None
    ),

    min_price: float | None = Query(
        default=None,
        ge=0
    ),

    max_price: float | None = Query(
        default=None,
        ge=0
    ),

    min_validity: int | None = Query(
        default=None,
        gt=0
    ),

    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(get_db)
):

    return ServicePlanService.search_plans(
        db=db,
        search=search,
        plan_type=plan_type,
        is_active=is_active,
        min_price=min_price,
        max_price=max_price,
        min_validity=min_validity
    )


# --------------------------------------------------
# 6. PLAN COMPARISON
# --------------------------------------------------

@router.get(
    "/compare",
    response_model=list[
        ServicePlanComparisonResponse
    ]
)
def compare_plans(
    ids: str = Query(
        description="Comma-separated plan IDs"
    ),

    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(get_db)
):

    plan_ids = []

    for value in ids.split(","):

        value = value.strip()

        if not value.isdigit():

            from fastapi import HTTPException

            raise HTTPException(
                status_code=400,
                detail="Plan IDs must be numbers"
            )

        plan_ids.append(
            int(value)
        )

    return ServicePlanService.compare_plans(
        db=db,
        plan_ids=plan_ids
    )