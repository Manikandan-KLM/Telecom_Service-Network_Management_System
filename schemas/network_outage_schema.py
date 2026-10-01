from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class NetworkOutageCreateRequest(BaseModel):
    outage_code: str = Field(
        min_length=3,
        max_length=50
    )

    outage_type: str = Field(
        min_length=2,
        max_length=50
    )

    severity: str = "Low"

    description: str | None = None

    start_time: datetime

    expected_resolution: datetime | None = None

    tower_ids: list[int] = Field(
        min_length=1
    )


class NetworkOutageUpdateRequest(BaseModel):
    outage_type: str | None = None

    severity: str | None = None

    description: str | None = None

    expected_resolution: datetime | None = None

    actual_resolution: datetime | None = None

    status: str | None = None


class NetworkOutageStatusRequest(BaseModel):
    status: str


class NetworkOutageResponse(BaseModel):
    id: int
    outage_code: str
    outage_type: str
    severity: str
    description: str | None
    start_time: datetime
    expected_resolution: datetime | None
    actual_resolution: datetime | None
    status: str
    created_by: int
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class OutageAffectedResponse(BaseModel):
    outage_id: int
    outage_code: str
    affected_tower_ids: list[int]
    affected_customer_ids: list[int]
    affected_tower_count: int
    affected_customer_count: int