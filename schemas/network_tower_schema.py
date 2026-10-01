from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field
)


class NetworkTowerCreateRequest(BaseModel):

    tower_number: str = Field(
        min_length=3,
        max_length=50
    )

    tower_name: str = Field(
        min_length=2,
        max_length=100
    )

    tower_type: str

    latitude: float = Field(
        ge=-90,
        le=90
    )

    longitude: float = Field(
        ge=-180,
        le=180
    )

    coverage_area: float = Field(
        gt=0
    )

    capacity: int = Field(
        gt=0
    )


class NetworkTowerUpdateRequest(BaseModel):

    tower_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100
    )

    tower_type: str | None = None

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

    coverage_area: float | None = Field(
        default=None,
        gt=0
    )

    capacity: int | None = Field(
        default=None,
        gt=0
    )


class NetworkTowerStatusRequest(BaseModel):

    status: str


class NetworkTowerResponse(BaseModel):

    id: int
    tower_number: str
    tower_name: str
    tower_type: str
    latitude: float
    longitude: float
    coverage_area: float
    capacity: int
    status: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )