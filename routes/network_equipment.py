from fastapi import (
    APIRouter,
    Depends,
    status
)

from sqlalchemy.orm import Session

from database import get_db
from models.user_model import User

from schemas.network_equipment_schema import (
    NetworkEquipmentCreateRequest,
    NetworkEquipmentUpdateRequest,
    EquipmentMetricsRequest,
    EquipmentHealthRequest,
    NetworkEquipmentResponse
)

from services.network_equipment_service import (
    NetworkEquipmentService
)

from utils.dependencies import (
    get_current_user,
    require_roles
)


router = APIRouter(
    prefix="/api/v1/equipment",
    tags=["Network Equipment"]
)


# ==================================================
# CREATE EQUIPMENT
# ==================================================

@router.post(
    "",
    response_model=NetworkEquipmentResponse,
    status_code=status.HTTP_201_CREATED
)
def create_equipment(
    request: NetworkEquipmentCreateRequest,

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

    return NetworkEquipmentService.create_equipment(
        db=db,
        equipment_code=request.equipment_code,
        equipment_name=request.equipment_name,
        equipment_type=request.equipment_type,
        manufacturer=request.manufacturer,
        model_number=request.model_number,
        tower_id=request.tower_id,
        installation_date=request.installation_date,
        maintenance_schedule=request.maintenance_schedule,
        notes=request.notes
    )


# ==================================================
# SEARCH EQUIPMENT
# ==================================================

@router.get(
    "",
    response_model=list[NetworkEquipmentResponse]
)
def search_equipment(
    search: str | None = None,
    equipment_type: str | None = None,
    health_status: str | None = None,
    network_status: str | None = None,
    tower_id: int | None = None,

    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(get_db)
):

    return NetworkEquipmentService.search_equipment(
        db=db,
        search=search,
        equipment_type=equipment_type,
        health_status=health_status,
        network_status=network_status,
        tower_id=tower_id
    )


# ==================================================
# GET EQUIPMENT
# ==================================================

@router.get(
    "/{equipment_id}",
    response_model=NetworkEquipmentResponse
)
def get_equipment(
    equipment_id: int,

    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(get_db)
):

    return NetworkEquipmentService.get_equipment(
        db,
        equipment_id
    )


# ==================================================
# UPDATE EQUIPMENT
# ==================================================

@router.patch(
    "/{equipment_id}",
    response_model=NetworkEquipmentResponse
)
def update_equipment(
    equipment_id: int,
    request: NetworkEquipmentUpdateRequest,

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

    return NetworkEquipmentService.update_equipment(
        db=db,
        equipment_id=equipment_id,
        data=request
    )


# ==================================================
# UPDATE METRICS
# ==================================================

@router.patch(
    "/{equipment_id}/metrics",
    response_model=NetworkEquipmentResponse
)
def update_metrics(
    equipment_id: int,
    request: EquipmentMetricsRequest,

    current_user: User = Depends(
        require_roles(
            "Super Admin",
            "Network Engineer",
            "Field Technician"
        )
    ),

    db: Session = Depends(get_db)
):

    return NetworkEquipmentService.update_metrics(
        db=db,
        equipment_id=equipment_id,
        cpu_usage=request.cpu_usage,
        memory_usage=request.memory_usage,
        network_status=request.network_status,
        last_heartbeat=request.last_heartbeat
    )


# ==================================================
# UPDATE HEALTH
# ==================================================

@router.patch(
    "/{equipment_id}/health",
    response_model=NetworkEquipmentResponse
)
def update_health(
    equipment_id: int,
    request: EquipmentHealthRequest,

    current_user: User = Depends(
        require_roles(
            "Super Admin",
            "Network Engineer"
        )
    ),

    db: Session = Depends(get_db)
):

    return NetworkEquipmentService.update_health(
        db=db,
        equipment_id=equipment_id,
        health_status=request.health_status
    )


# ==================================================
# DOWNTIME
# ==================================================

@router.get(
    "/{equipment_id}/downtime"
)
def equipment_downtime(
    equipment_id: int,

    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(get_db)
):

    return NetworkEquipmentService.calculate_downtime(
        db,
        equipment_id
    )