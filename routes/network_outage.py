from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database import get_db

from schemas.network_outage_schema import (
    NetworkOutageCreateRequest,
    NetworkOutageResponse,
    NetworkOutageUpdateRequest,
    OutageAffectedResponse
)

from services.network_outage_service import (
    NetworkOutageService
)

from utils.dependencies import (
    get_current_user,
    require_roles
)


router = APIRouter(
    prefix="/api/v1/outages",
    tags=["Network Outages"]
)


# =====================================================
# CREATE OUTAGE
# =====================================================

@router.post(
    "/",
    response_model=NetworkOutageResponse
)
def create_outage(
    request: NetworkOutageCreateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Super Admin",
            "Operations Manager",
            "Network Engineer"
        )
    )
):

    return NetworkOutageService.create_outage(
        db=db,
        outage_code=request.outage_code,
        outage_type=request.outage_type,
        severity=request.severity,
        description=request.description,
        start_time=request.start_time,
        expected_resolution=request.expected_resolution,
        tower_ids=request.tower_ids,
        created_by=current_user.id
    )


# =====================================================
# GET ALL OUTAGES
# =====================================================

@router.get(
    "/",
    response_model=list[NetworkOutageResponse]
)
def get_outages(
    severity: str | None = Query(None),
    status: str | None = Query(None),
    outage_type: str | None = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    return NetworkOutageService.get_all_outages(
        db=db,
        severity=severity,
        status=status,
        outage_type=outage_type
    )


# =====================================================
# GET AFFECTED DATA
# =====================================================

@router.get(
    "/{outage_id}/affected",
    response_model=OutageAffectedResponse
)
def get_affected_data(
    outage_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    return NetworkOutageService.get_affected_data(
        db,
        outage_id
    )


# =====================================================
# UPDATE OUTAGE
# =====================================================

@router.patch(
    "/{outage_id}",
    response_model=NetworkOutageResponse
)
def update_outage(
    outage_id: int,
    request: NetworkOutageUpdateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Super Admin",
            "Operations Manager",
            "Network Engineer"
        )
    )
):

    return NetworkOutageService.update_outage(
        db=db,
        outage_id=outage_id,
        outage_type=request.outage_type,
        severity=request.severity,
        description=request.description,
        expected_resolution=request.expected_resolution,
        actual_resolution=request.actual_resolution,
        status=request.status
    )


# =====================================================
# GET OUTAGE BY ID
# =====================================================

@router.get(
    "/{outage_id}",
    response_model=NetworkOutageResponse
)
def get_outage(
    outage_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    return NetworkOutageService.get_outage(
        db,
        outage_id
    )