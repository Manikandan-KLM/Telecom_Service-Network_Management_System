from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ServiceRequestCreateRequest(BaseModel):

    request_type: str

    description: str = Field(
        min_length=5,
        max_length=5000
    )

    priority: str = "Medium"

    sim_id: int | None = None

    subscription_id: int | None = None

    device_id: int | None = None


class ServiceRequestAssignRequest(BaseModel):

    assigned_to: int


class ServiceRequestStatusRequest(BaseModel):

    status: str

    remarks: str | None = None

    rejection_reason: str | None = None

    completion_notes: str | None = None


class ServiceRequestResponse(BaseModel):

    id: int

    request_number: str

    customer_id: int

    sim_id: int | None

    subscription_id: int | None
    device_id: int | None

    request_type: str
    description: str

    status: str
    priority: str

    assigned_to: int | None

    rejection_reason: str | None
    completion_notes: str | None

    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None

    model_config = ConfigDict(
        from_attributes=True
    )


class ServiceRequestHistoryResponse(BaseModel):

    id: int

    service_request_id: int

    changed_by: int

    old_status: str | None

    new_status: str

    remarks: str | None

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )