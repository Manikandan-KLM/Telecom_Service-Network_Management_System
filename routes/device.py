from fastapi import (
    APIRouter,
    Depends,
    Query,
    status
)

from sqlalchemy.orm import Session

from database import get_db
from models.user_model import User

from schemas.device_schema import (
    DeviceCreateRequest,
    DeviceUpdateRequest,
    DeviceStatusRequest,
    DeviceSIMAssignRequest,
    DeviceResponse,
    DeviceSIMMappingResponse
)

from services.device_service import (
    DeviceService
)

from utils.dependencies import (
    get_current_user,
    require_roles
)


router = APIRouter(
    prefix="/api/v1/devices",
    tags=["Devices"]
)


# ==================================================
# SEARCH DEVICES
# ==================================================

@router.get(
    "",
    response_model=list[DeviceResponse]
)
def search_devices(
    search: str | None = Query(
        default=None
    ),

    manufacturer: str | None = Query(
        default=None
    ),

    device_type: str | None = Query(
        default=None
    ),

    device_status: str | None = Query(
        default=None
    ),

    customer_id: int | None = Query(
        default=None
    ),

    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(get_db)
):

    return DeviceService.search_devices(
        db=db,
        search=search,
        manufacturer=manufacturer,
        device_type=device_type,
        device_status=device_status,
        customer_id=customer_id
    )


# ==================================================
# CREATE DEVICE
# ==================================================

@router.post(
    "",
    response_model=DeviceResponse,
    status_code=status.HTTP_201_CREATED
)
def create_device(
    request: DeviceCreateRequest,

    current_user: User = Depends(
        require_roles(
            "Super Admin",
            "Operations Manager",
            "Network Engineer"
        )
    ),

    db: Session = Depends(get_db)
):

    return DeviceService.create_device(
        db=db,
        imei=request.imei,
        device_model=request.device_model,
        manufacturer=request.manufacturer,
        device_type=request.device_type,
        customer_id=request.customer_id
    )


# ==================================================
# GET DEVICE
# ==================================================

@router.get(
    "/{device_id}",
    response_model=DeviceResponse
)
def get_device(
    device_id: int,

    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(get_db)
):

    return DeviceService.get_device(
        db,
        device_id
    )


# ==================================================
# UPDATE DEVICE
# ==================================================

@router.patch(
    "/{device_id}",
    response_model=DeviceResponse
)
def update_device(
    device_id: int,
    request: DeviceUpdateRequest,

    current_user: User = Depends(
        require_roles(
            "Super Admin",
            "Operations Manager",
            "Network Engineer"
        )
    ),

    db: Session = Depends(get_db)
):

    return DeviceService.update_device(
        db=db,
        device_id=device_id,
        device_model=request.device_model,
        manufacturer=request.manufacturer,
        device_type=request.device_type,
        customer_id=request.customer_id
    )


# ==================================================
# CHANGE STATUS
# ==================================================

@router.patch(
    "/{device_id}/status",
    response_model=DeviceResponse
)
def change_device_status(
    device_id: int,
    request: DeviceStatusRequest,

    current_user: User = Depends(
        require_roles(
            "Super Admin",
            "Operations Manager",
            "Network Engineer"
        )
    ),

    db: Session = Depends(get_db)
):

    return DeviceService.update_status(
        db=db,
        device_id=device_id,
        new_status=request.status
    )


# ==================================================
# ASSIGN SIM
# ==================================================

@router.post(
    "/{device_id}/sim",
    response_model=DeviceSIMMappingResponse,
    status_code=status.HTTP_201_CREATED
)
def assign_sim(
    device_id: int,
    request: DeviceSIMAssignRequest,

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

    return DeviceService.assign_sim(
        db=db,
        device_id=device_id,
        sim_id=request.sim_id
    )


# ==================================================
# UNASSIGN SIM
# ==================================================

@router.delete(
    "/{device_id}/sim",
    response_model=DeviceSIMMappingResponse
)
def unassign_sim(
    device_id: int,

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

    return DeviceService.unassign_sim(
        db=db,
        device_id=device_id
    )


# ==================================================
# SIM MAPPING HISTORY
# ==================================================

@router.get(
    "/{device_id}/sim-history",
    response_model=list[DeviceSIMMappingResponse]
)
def sim_mapping_history(
    device_id: int,

    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(get_db)
):

    return DeviceService.get_sim_history(
        db,
        device_id
    )