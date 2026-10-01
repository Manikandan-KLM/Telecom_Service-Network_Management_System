from fastapi import (
    APIRouter,
    Depends,
    status
)

from sqlalchemy.orm import Session

from database import get_db
from models.user_model import User

from schemas.network_tower_schema import (
    NetworkTowerCreateRequest,
    NetworkTowerUpdateRequest,
    NetworkTowerStatusRequest,
    NetworkTowerResponse
)

from services.network_tower_service import (
    NetworkTowerService
)

from utils.dependencies import (
    get_current_user,
    require_roles
)


router = APIRouter(
    prefix="/api/v1/towers",
    tags=["Network Towers"]
)


# ==================================================
# CREATE TOWER
# ==================================================

@router.post(
    "",
    response_model=NetworkTowerResponse,
    status_code=status.HTTP_201_CREATED
)
def create_tower(
    request: NetworkTowerCreateRequest,

    current_user: User = Depends(
        require_roles(
            "Super Admin",
            "Operations Manager",
            "Network Engineer"
        )
    ),

    db: Session = Depends(get_db)
):

    return NetworkTowerService.create_tower(
        db=db,
        tower_number=request.tower_number,
        tower_name=request.tower_name,
        tower_type=request.tower_type,
        latitude=request.latitude,
        longitude=request.longitude,
        coverage_area=request.coverage_area,
        capacity=request.capacity
    )


# ==================================================
# SEARCH TOWERS
# ==================================================

@router.get(
    "",
    response_model=list[NetworkTowerResponse]
)
def search_towers(
    search: str | None = None,
    tower_type: str | None = None,
    tower_status: str | None = None,

    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(get_db)
):

    return NetworkTowerService.search_towers(
        db=db,
        search=search,
        tower_type=tower_type,
        tower_status=tower_status
    )


# ==================================================
# GET TOWER
# ==================================================

@router.get(
    "/{tower_id}",
    response_model=NetworkTowerResponse
)
def get_tower(
    tower_id: int,

    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(get_db)
):

    return NetworkTowerService.get_tower(
        db,
        tower_id
    )


# ==================================================
# UPDATE TOWER
# ==================================================

@router.patch(
    "/{tower_id}",
    response_model=NetworkTowerResponse
)
def update_tower(
    tower_id: int,
    request: NetworkTowerUpdateRequest,

    current_user: User = Depends(
        require_roles(
            "Super Admin",
            "Operations Manager",
            "Network Engineer"
        )
    ),

    db: Session = Depends(get_db)
):

    return NetworkTowerService.update_tower(
        db=db,
        tower_id=tower_id,
        data=request
    )


# ==================================================
# UPDATE STATUS
# ==================================================

@router.patch(
    "/{tower_id}/status",
    response_model=NetworkTowerResponse
)
def update_tower_status(
    tower_id: int,
    request: NetworkTowerStatusRequest,

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

    return NetworkTowerService.update_status(
        db=db,
        tower_id=tower_id,
        new_status=request.status
    )


# ==================================================
# DELETE / DECOMMISSIONED TOWER
# ==================================================

@router.delete(
    "/{tower_id}",
    response_model=NetworkTowerResponse
)
def delete_tower(
    tower_id: int,

    current_user: User = Depends(
        require_roles(
            "Super Admin",
            "Operations Manager"
        )
    ),

    db: Session = Depends(get_db)
):

    return NetworkTowerService.delete_tower(
        db,
        tower_id
    )