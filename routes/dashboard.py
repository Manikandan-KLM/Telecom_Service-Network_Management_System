from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db

from models.user_model import User

from schemas.dashboard_schema import (
    OperationsDashboardResponse
)

from services.dashboard_service import (
    DashboardService
)

from utils.dependencies import (
    require_roles
)


router = APIRouter(
    prefix="/api/v1/dashboard",
    tags=["Operations Dashboard"]
)


# =========================================================
# OPERATIONS DASHBOARD
# =========================================================

@router.get(
    "/operations",
    response_model=OperationsDashboardResponse
)
def get_operations_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Super Admin",
            "Operations Manager"
        )
    )
):

    return DashboardService.get_operations_dashboard(
        db=db
    )