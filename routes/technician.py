from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database import get_db

from schemas.technician_schema import (
    TechnicianCreateRequest,
    TechnicianUpdateRequest,
    TechnicianSkillRequest,
    TechnicianServiceAreaRequest,
    TechnicianAssignmentRequest,
    TechnicianAssignmentUpdateRequest,
    TechnicianResponse,
    TechnicianAssignmentResponse,
    TechnicianWorkloadResponse
)

from services.technician_service import (
    TechnicianService
)

from utils.dependencies import (
    get_current_user,
    require_roles
)


router = APIRouter(
    prefix="/api/v1/technicians",
    tags=["Field Technicians"]
)


# =====================================================
# REGISTER TECHNICIAN
# =====================================================

@router.post(
    "/",
    response_model=TechnicianResponse
)
def create_technician(
    request: TechnicianCreateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Super Admin",
            "Operations Manager"
        )
    )
):

    return TechnicianService.create_technician(
        db=db,
        user_id=request.user_id,
        technician_code=request.technician_code,
        full_name=request.full_name,
        phone=request.phone,
        availability_status=request.availability_status,
        latitude=request.latitude,
        longitude=request.longitude,
        service_area=request.service_area
    )


# =====================================================
# GET ALL TECHNICIANS
# =====================================================

@router.get(
    "/",
    response_model=list[TechnicianResponse]
)
def get_technicians(
    availability_status: str | None = Query(None),
    service_area: str | None = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    from repositories.technician_repository import (
        TechnicianRepository
    )

    return TechnicianRepository.get_all(
        db,
        availability_status,
        service_area
    )


# =====================================================
# GET TECHNICIAN
# =====================================================

@router.get(
    "/{technician_id}",
    response_model=TechnicianResponse
)
def get_technician(
    technician_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    from repositories.technician_repository import (
        TechnicianRepository
    )

    technician = (
        TechnicianRepository.get_by_id(
            db,
            technician_id
        )
    )

    if not technician:

        from fastapi import HTTPException

        raise HTTPException(
            status_code=404,
            detail="Technician not found"
        )

    return technician


# =====================================================
# UPDATE TECHNICIAN
# =====================================================

@router.patch(
    "/{technician_id}",
    response_model=TechnicianResponse
)
def update_technician(
    technician_id: int,
    request: TechnicianUpdateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Super Admin",
            "Operations Manager"
        )
    )
):

    return TechnicianService.update_technician(
        db=db,
        technician_id=technician_id,
        phone=request.phone,
        availability_status=request.availability_status,
        latitude=request.latitude,
        longitude=request.longitude,
        service_area=request.service_area,
        is_active=request.is_active
    )


# =====================================================
# ADD SKILL
# =====================================================

@router.post(
    "/{technician_id}/skills"
)
def add_skill(
    technician_id: int,
    request: TechnicianSkillRequest,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Super Admin",
            "Operations Manager"
        )
    )
):

    return TechnicianService.add_skill(
        db,
        technician_id,
        request.skill_name,
        request.skill_level
    )


# =====================================================
# GET SKILLS
# =====================================================

@router.get(
    "/{technician_id}/skills"
)
def get_skills(
    technician_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    from repositories.technician_mapping_repository import (
        TechnicianMappingRepository
    )

    return TechnicianMappingRepository.get_skills(
        db,
        technician_id
    )


# =====================================================
# ADD SERVICE AREA
# =====================================================

@router.post(
    "/{technician_id}/service-areas"
)
def add_service_area(
    technician_id: int,
    request: TechnicianServiceAreaRequest,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Super Admin",
            "Operations Manager"
        )
    )
):

    return TechnicianService.add_service_area(
        db,
        technician_id,
        request.area_name
    )


# =====================================================
# GET SERVICE AREAS
# =====================================================

@router.get(
    "/{technician_id}/service-areas"
)
def get_service_areas(
    technician_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    from repositories.technician_mapping_repository import (
        TechnicianMappingRepository
    )

    return (
        TechnicianMappingRepository
        .get_service_areas(
            db,
            technician_id
        )
    )


# =====================================================
# ASSIGN TECHNICIAN
# =====================================================

@router.post(
    "/assign",
    response_model=TechnicianAssignmentResponse
)
def assign_technician(
    request: TechnicianAssignmentRequest,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Super Admin",
            "Operations Manager",
            "Network Engineer"
        )
    )
):

    return TechnicianService.assign_technician(
        db=db,
        technician_id=request.technician_id,
        job_type=request.job_type,
        outage_id=request.outage_id,
        customer_id=request.customer_id,
        job_description=request.job_description
    )


# =====================================================
# REASSIGN TECHNICIAN
# =====================================================

@router.patch(
    "/assignments/{assignment_id}/reassign",
    response_model=TechnicianAssignmentResponse
)
def reassign_technician(
    assignment_id: int,
    technician_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Super Admin",
            "Operations Manager",
            "Network Engineer"
        )
    )
):

    return TechnicianService.reassign_technician(
        db=db,
        assignment_id=assignment_id,
        new_technician_id=technician_id
    )


# =====================================================
# UPDATE JOB STATUS
# =====================================================

@router.patch(
    "/assignments/{assignment_id}",
    response_model=TechnicianAssignmentResponse
)
def update_assignment(
    assignment_id: int,
    request: TechnicianAssignmentUpdateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Super Admin",
            "Operations Manager",
            "Network Engineer",
            "Field Technician"
        )
    )
):

    return TechnicianService.update_assignment_status(
        db=db,
        assignment_id=assignment_id,
        status=request.status,
        notes=request.notes
    )


# =====================================================
# TECHNICIAN WORKLOAD
# =====================================================

@router.get(
    "/{technician_id}/workload",
    response_model=TechnicianWorkloadResponse
)
def technician_workload(
    technician_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    return TechnicianService.get_workload(
        db,
        technician_id
    )


# =====================================================
# PENDING JOBS
# =====================================================

@router.get(
    "/{technician_id}/jobs/pending",
    response_model=list[TechnicianAssignmentResponse]
)
def pending_jobs(
    technician_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    return TechnicianService.get_jobs(
        db,
        technician_id,
        "Pending"
    )


# =====================================================
# COMPLETED JOBS
# =====================================================

@router.get(
    "/{technician_id}/jobs/completed",
    response_model=list[TechnicianAssignmentResponse]
)
def completed_jobs(
    technician_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    return TechnicianService.get_jobs(
        db,
        technician_id,
        "Completed"
    )