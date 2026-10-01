from fastapi import (
    APIRouter,
    Depends,
    status
)

from sqlalchemy.orm import Session

from database import get_db
from models.user_model import User

from schemas.subscription_schema import (
    SubscriptionCreateRequest,
    SubscriptionPlanChangeRequest,
    SubscriptionResponse,
    SubscriptionHistoryResponse
)

from services.subscription_service import (
    SubscriptionService
)

from utils.dependencies import (
    get_current_user,
    require_roles
)


router = APIRouter(
    prefix="/api/v1/subscriptions",
    tags=["Subscriptions"]
)


# ==================================================
# NEW SUBSCRIPTION
# ==================================================

@router.post(
    "",
    response_model=SubscriptionResponse,
    status_code=status.HTTP_201_CREATED
)
def create_subscription(
    request: SubscriptionCreateRequest,

    current_user: User = Depends(
        require_roles(
            "Super Admin",
            "Operations Manager",
            "Support Agent"
        )
    ),

    db: Session = Depends(get_db)
):

    return SubscriptionService.create_subscription(
        db=db,
        customer_id=request.customer_id,
        sim_id=request.sim_id,
        plan_id=request.plan_id,
        changed_by=current_user.id
    )


# ==================================================
# GET SUBSCRIPTION
# ==================================================

@router.get(
    "/{subscription_id}",
    response_model=SubscriptionResponse
)
def get_subscription(
    subscription_id: int,

    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(get_db)
):

    return SubscriptionService.get_subscription(
        db,
        subscription_id
    )


# ==================================================
# PLAN UPGRADE
# ==================================================

@router.patch(
    "/{subscription_id}/upgrade",
    response_model=SubscriptionResponse
)
def upgrade_plan(
    subscription_id: int,
    request: SubscriptionPlanChangeRequest,

    current_user: User = Depends(
        require_roles(
            "Super Admin",
            "Operations Manager",
            "Support Agent"
        )
    ),

    db: Session = Depends(get_db)
):

    return SubscriptionService.upgrade_plan(
        db=db,
        subscription_id=subscription_id,
        new_plan_id=request.new_plan_id,
        changed_by=current_user.id
    )


# ==================================================
# PLAN DOWNGRADE
# ==================================================

@router.patch(
    "/{subscription_id}/downgrade",
    response_model=SubscriptionResponse
)
def downgrade_plan(
    subscription_id: int,
    request: SubscriptionPlanChangeRequest,

    current_user: User = Depends(
        require_roles(
            "Super Admin",
            "Operations Manager",
            "Support Agent"
        )
    ),

    db: Session = Depends(get_db)
):

    return SubscriptionService.downgrade_plan(
        db=db,
        subscription_id=subscription_id,
        new_plan_id=request.new_plan_id,
        changed_by=current_user.id
    )


# ==================================================
# RENEW
# ==================================================

@router.post(
    "/{subscription_id}/renew",
    response_model=SubscriptionResponse
)
def renew_subscription(
    subscription_id: int,

    current_user: User = Depends(
        require_roles(
            "Super Admin",
            "Operations Manager",
            "Support Agent"
        )
    ),

    db: Session = Depends(get_db)
):

    return SubscriptionService.renew_subscription(
        db=db,
        subscription_id=subscription_id,
        changed_by=current_user.id
    )


# ==================================================
# SUSPEND
# ==================================================

@router.patch(
    "/{subscription_id}/suspend",
    response_model=SubscriptionResponse
)
def suspend_subscription(
    subscription_id: int,

    current_user: User = Depends(
        require_roles(
            "Super Admin",
            "Operations Manager",
            "Support Agent"
        )
    ),

    db: Session = Depends(get_db)
):

    return SubscriptionService.suspend_subscription(
        db=db,
        subscription_id=subscription_id,
        changed_by=current_user.id
    )


# ==================================================
# REACTIVATE
# ==================================================

@router.patch(
    "/{subscription_id}/reactivate",
    response_model=SubscriptionResponse
)
def reactivate_subscription(
    subscription_id: int,

    current_user: User = Depends(
        require_roles(
            "Super Admin",
            "Operations Manager",
            "Support Agent"
        )
    ),

    db: Session = Depends(get_db)
):

    return SubscriptionService.reactivate_subscription(
        db=db,
        subscription_id=subscription_id,
        changed_by=current_user.id
    )


# ==================================================
# CANCEL
# ==================================================

@router.patch(
    "/{subscription_id}/cancel",
    response_model=SubscriptionResponse
)
def cancel_subscription(
    subscription_id: int,

    current_user: User = Depends(
        require_roles(
            "Super Admin",
            "Operations Manager",
            "Support Agent"
        )
    ),

    db: Session = Depends(get_db)
):

    return SubscriptionService.cancel_subscription(
        db=db,
        subscription_id=subscription_id,
        changed_by=current_user.id
    )


# ==================================================
# SUBSCRIPTION HISTORY
# ==================================================

@router.get(
    "/{subscription_id}/history",
    response_model=list[SubscriptionHistoryResponse]
)
def subscription_history(
    subscription_id: int,

    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(get_db)
):

    return SubscriptionService.get_history(
        db,
        subscription_id
    )


# ==================================================
# CUSTOMER SUBSCRIPTIONS
# ==================================================

@router.get(
    "/customer/{customer_id}",
    response_model=list[SubscriptionResponse]
)
def customer_subscriptions(
    customer_id: int,

    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(get_db)
):

    return SubscriptionService.get_customer_subscriptions(
        db,
        customer_id
    )