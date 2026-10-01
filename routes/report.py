from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db

from models.user_model import User

from services.report_service import (
    ReportService
)

from utils.dependencies import (
    require_roles
)


router = APIRouter(
    prefix="/api/v1/reports",
    tags=["Advanced Reports"]
)


# =========================================================
# 1. CUSTOMER GROWTH
# =========================================================

@router.get("/customer-growth")
def customer_growth_report(
    start_date: date | None = None,
    end_date: date | None = None,
    customer_id: int | None = None,
    location: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Super Admin",
            "Operations Manager"
        )
    )
):

    try:

        return ReportService.customer_growth(
            db=db,
            start_date=start_date,
            end_date=end_date,
            customer_id=customer_id,
            location=location
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )


# =========================================================
# 2. SUBSCRIPTION TRENDS
# =========================================================

@router.get("/subscription-trends")
def subscription_trends_report(
    start_date: date | None = None,
    end_date: date | None = None,
    customer_id: int | None = None,
    plan_id: int | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Super Admin",
            "Operations Manager"
        )
    )
):

    try:

        return ReportService.subscription_trends(
            db=db,
            start_date=start_date,
            end_date=end_date,
            customer_id=customer_id,
            plan_id=plan_id,
            status=status
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )


# =========================================================
# 3. PLAN POPULARITY
# =========================================================

@router.get("/plan-popularity")
def plan_popularity_report(
    start_date: date | None = None,
    end_date: date | None = None,
    customer_id: int | None = None,
    plan_id: int | None = None,
    search: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Super Admin",
            "Operations Manager"
        )
    )
):

    return ReportService.plan_popularity(
        db=db,
        start_date=start_date,
        end_date=end_date,
        customer_id=customer_id,
        plan_id=plan_id,
        search=search
    )


# =========================================================
# 4. DATA CONSUMPTION
# =========================================================

@router.get("/data-consumption")
def data_consumption_report(
    start_date: date | None = None,
    end_date: date | None = None,
    customer_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Super Admin",
            "Operations Manager"
        )
    )
):

    return ReportService.data_consumption(
        db=db,
        start_date=start_date,
        end_date=end_date,
        customer_id=customer_id
    )


# =========================================================
# 5. NETWORK UPTIME
# =========================================================

@router.get("/network-uptime")
def network_uptime_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Super Admin",
            "Operations Manager",
            "Network Engineer"
        )
    )
):

    return ReportService.network_uptime(
        db=db
    )


# =========================================================
# 6. OUTAGE FREQUENCY
# =========================================================

@router.get("/outage-frequency")
def outage_frequency_report(
    start_date: date | None = None,
    end_date: date | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Super Admin",
            "Operations Manager",
            "Network Engineer"
        )
    )
):

    return ReportService.outage_frequency(
        db=db,
        start_date=start_date,
        end_date=end_date
    )


# =========================================================
# 7. TICKET RESOLUTION TIME
# =========================================================

@router.get("/ticket-resolution-time")
def ticket_resolution_report(
    start_date: date | None = None,
    end_date: date | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Super Admin",
            "Operations Manager",
            "Support Agent"
        )
    )
):

    return ReportService.ticket_resolution_time(
        db=db,
        start_date=start_date,
        end_date=end_date,
        status=status
    )


# =========================================================
# 8. SLA PERFORMANCE
# =========================================================

@router.get("/sla-performance")
def sla_performance_report(
    start_date: date | None = None,
    end_date: date | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Super Admin",
            "Operations Manager",
            "Support Agent"
        )
    )
):

    return ReportService.sla_performance(
        db=db,
        start_date=start_date,
        end_date=end_date
    )


# =========================================================
# 9. TECHNICIAN PERFORMANCE
# =========================================================

@router.get("/technician-performance")
def technician_performance_report(
    technician_id: int | None = None,
    search: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Super Admin",
            "Operations Manager",
            "Network Engineer"
        )
    )
):

    return ReportService.technician_performance(
        db=db,
        technician_id=technician_id,
        search=search
    )


# =========================================================
# 10. CUSTOMER SERVICE TRENDS
# =========================================================

@router.get("/customer-service-trends")
def customer_service_trends_report(
    start_date: date | None = None,
    end_date: date | None = None,
    customer_id: int | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Super Admin",
            "Operations Manager",
            "Support Agent"
        )
    )
):

    return ReportService.customer_service_trends(
        db=db,
        start_date=start_date,
        end_date=end_date,
        customer_id=customer_id,
        status=status
    )