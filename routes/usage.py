from datetime import date

from fastapi import (
    APIRouter,
    Depends,
    status
)

from sqlalchemy.orm import Session

from database import get_db
from models.user_model import User

from schemas.usage_schema import (
    UsageCreateRequest,
    UsageResponse,
    UsageSummaryResponse
)

from services.usage_service import (
    UsageService
)

from utils.dependencies import (
    get_current_user,
    require_roles
)


router = APIRouter(
    prefix="/api/v1/usage",
    tags=["Usage Tracking"]
)


# ------------------------------------------------
# CREATE USAGE
# ------------------------------------------------

@router.post(
    "",
    response_model=UsageResponse,
    status_code=status.HTTP_201_CREATED
)
def create_usage(
    request: UsageCreateRequest,
    current_user: User = Depends(
        require_roles(
            "Super Admin",
            "Operations Manager",
            "Network Engineer",
            "Field Technician"
        )
    ),
    db: Session = Depends(get_db)
):

    return UsageService.create_usage(
        db=db,
        subscription_id=request.subscription_id,
        usage_type=request.usage_type,
        usage_amount=request.usage_amount,
        usage_date=request.usage_date
    )


# ------------------------------------------------
# CUSTOMER USAGE
# ------------------------------------------------

@router.get(
    "/customer/{customer_id}",
    response_model=list[UsageResponse]
)
def customer_usage(
    customer_id: int,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db)
):

    return UsageService.get_customer_usage(
        db,
        customer_id
    )


# ------------------------------------------------
# SIM USAGE
# ------------------------------------------------

@router.get(
    "/sim/{sim_id}",
    response_model=list[UsageResponse]
)
def sim_usage(
    sim_id: int,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db)
):

    return UsageService.get_sim_usage(
        db,
        sim_id
    )


# ------------------------------------------------
# SUBSCRIPTION USAGE
# ------------------------------------------------

@router.get(
    "/subscription/{subscription_id}",
    response_model=list[UsageResponse]
)
def subscription_usage(
    subscription_id: int,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db)
):

    return UsageService.get_subscription_usage(
        db,
        subscription_id
    )


# ------------------------------------------------
# USAGE SUMMARY
# ------------------------------------------------

@router.get(
    "/subscription/{subscription_id}/summary",
    response_model=UsageSummaryResponse
)
def usage_summary(
    subscription_id: int,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db)
):

    return UsageService.get_usage_summary(
        db,
        subscription_id
    )


# ------------------------------------------------
# DAILY USAGE
# ------------------------------------------------

@router.get(
    "/subscription/{subscription_id}/daily"
)
def daily_usage(
    subscription_id: int,
    usage_date: date,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db)
):

    return UsageService.get_daily_usage(
        db=db,
        subscription_id=subscription_id,
        date_value=usage_date
    )


# ------------------------------------------------
# MONTHLY USAGE
# ------------------------------------------------

@router.get(
    "/subscription/{subscription_id}/monthly"
)
def monthly_usage(
    subscription_id: int,
    year: int,
    month: int,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db)
):

    return UsageService.get_monthly_usage(
        db=db,
        subscription_id=subscription_id,
        year=year,
        month=month
    )