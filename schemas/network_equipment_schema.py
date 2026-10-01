from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field
)


class NetworkEquipmentCreateRequest(BaseModel):

    equipment_code: str = Field(
        min_length=3,
        max_length=50
    )

    equipment_name: str = Field(
        min_length=2,
        max_length=100
    )

    equipment_type: str

    manufacturer: str = Field(
        min_length=2,
        max_length=100
    )

    model_number: str = Field(
        min_length=2,
        max_length=100
    )

    tower_id: int | None = None

    installation_date: datetime

    maintenance_schedule: str | None = None

    notes: str | None = None


class NetworkEquipmentUpdateRequest(BaseModel):

    equipment_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100
    )

    manufacturer: str | None = None

    model_number: str | None = None

    tower_id: int | None = None

    installation_date: datetime | None = None

    maintenance_schedule: str | None = None

    notes: str | None = None


class EquipmentMetricsRequest(BaseModel):

    cpu_usage: float = Field(
        ge=0,
        le=100
    )

    memory_usage: float = Field(
        ge=0,
        le=100
    )

    network_status: str

    last_heartbeat: datetime | None = None


class EquipmentHealthRequest(BaseModel):

    health_status: str


class NetworkEquipmentResponse(BaseModel):

    id: int

    equipment_code: str

    equipment_name: str

    equipment_type: str

    manufacturer: str

    model_number: str

    tower_id: int | None

    installation_date: datetime

    maintenance_schedule: str | None

    health_status: str

    cpu_usage: float

    memory_usage: float

    network_status: str

    last_heartbeat: datetime | None

    downtime_minutes: float

    notes: str | None

    created_at: datetime

    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )