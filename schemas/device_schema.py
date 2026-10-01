from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DeviceCreateRequest(BaseModel):

    imei: str = Field(
        min_length=15,
        max_length=15
    )

    device_model: str = Field(
        min_length=2,
        max_length=100
    )

    manufacturer: str = Field(
        min_length=2,
        max_length=100
    )

    device_type: str

    customer_id: int | None = None


class DeviceUpdateRequest(BaseModel):

    device_model: str | None = Field(
        default=None,
        min_length=2,
        max_length=100
    )

    manufacturer: str | None = Field(
        default=None,
        min_length=2,
        max_length=100
    )

    device_type: str | None = None

    customer_id: int | None = None


class DeviceStatusRequest(BaseModel):

    status: str


class DeviceSIMAssignRequest(BaseModel):

    sim_id: int


class DeviceResponse(BaseModel):

    id: int
    imei: str
    device_model: str
    manufacturer: str
    device_type: str
    status: str
    customer_id: int | None
    is_active: bool
    registered_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class DeviceSIMMappingResponse(BaseModel):

    id: int
    device_id: int
    sim_id: int
    is_active: bool
    assigned_at: datetime
    unassigned_at: datetime | None

    model_config = ConfigDict(
        from_attributes=True
    )