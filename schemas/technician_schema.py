from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# =====================================================
# TECHNICIAN REGISTRATION
# =====================================================

class TechnicianCreateRequest(BaseModel):

    user_id: int

    technician_code: str = Field(
        min_length=3,
        max_length=50
    )

    full_name: str = Field(
        min_length=2,
        max_length=100
    )

    phone: str = Field(
        min_length=10,
        max_length=20
    )

    availability_status: str = "Available"

    latitude: float | None = Field(
        default=None,
        ge=-90,
        le=90
    )

    longitude: float | None = Field(
        default=None,
        ge=-180,
        le=180
    )

    service_area: str = Field(
        min_length=2,
        max_length=255
    )


# =====================================================
# TECHNICIAN UPDATE
# =====================================================

class TechnicianUpdateRequest(BaseModel):

    phone: str | None = None

    availability_status: str | None = None

    latitude: float | None = Field(
        default=None,
        ge=-90,
        le=90
    )

    longitude: float | None = Field(
        default=None,
        ge=-180,
        le=180
    )

    service_area: str | None = None

    is_active: bool | None = None


# =====================================================
# SKILL
# =====================================================

class TechnicianSkillRequest(BaseModel):

    skill_name: str = Field(
        min_length=2,
        max_length=100
    )

    skill_level: str = "Intermediate"


# =====================================================
# SERVICE AREA
# =====================================================

class TechnicianServiceAreaRequest(BaseModel):

    area_name: str = Field(
        min_length=2,
        max_length=100
    )


# =====================================================
# ASSIGN TECHNICIAN
# =====================================================

class TechnicianAssignmentRequest(BaseModel):

    technician_id: int

    job_type: str = Field(
        min_length=2,
        max_length=50
    )

    outage_id: int | None = None

    customer_id: int | None = None

    job_description: str | None = None


# =====================================================
# UPDATE ASSIGNMENT
# =====================================================

class TechnicianAssignmentUpdateRequest(BaseModel):

    status: str | None = None

    notes: str | None = None


# =====================================================
# RESPONSE
# =====================================================

class TechnicianResponse(BaseModel):

    id: int
    user_id: int
    technician_code: str
    full_name: str
    phone: str
    availability_status: str
    latitude: float | None
    longitude: float | None
    service_area: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class TechnicianAssignmentResponse(BaseModel):

    id: int
    technician_id: int
    outage_id: int | None
    customer_id: int | None
    job_type: str
    job_description: str | None
    status: str
    assigned_at: datetime
    started_at: datetime | None
    completed_at: datetime | None
    notes: str | None

    model_config = ConfigDict(
        from_attributes=True
    )


class TechnicianWorkloadResponse(BaseModel):

    technician_id: int
    technician_code: str
    technician_name: str
    pending_jobs: int
    in_progress_jobs: int
    completed_jobs: int
    total_jobs: int