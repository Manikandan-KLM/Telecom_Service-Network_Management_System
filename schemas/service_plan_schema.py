from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field
)


class ServicePlanCreateRequest(BaseModel):

    plan_code: str = Field(
        min_length=3,
        max_length=50
    )

    plan_name: str = Field(
        min_length=2,
        max_length=100
    )

    plan_type: str

    data_limit: float = Field(
        default=0,
        ge=0
    )

    voice_limit: int = Field(
        default=0,
        ge=0
    )

    sms_limit: int = Field(
        default=0,
        ge=0
    )

    validity_days: int = Field(
        gt=0
    )

    price: float = Field(
        ge=0
    )

    description: str | None = None


class ServicePlanUpdateRequest(BaseModel):

    plan_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100
    )

    data_limit: float | None = Field(
        default=None,
        ge=0
    )

    voice_limit: int | None = Field(
        default=None,
        ge=0
    )

    sms_limit: int | None = Field(
        default=None,
        ge=0
    )

    validity_days: int | None = Field(
        default=None,
        gt=0
    )

    price: float | None = Field(
        default=None,
        ge=0
    )

    description: str | None = None


class ServicePlanStatusRequest(BaseModel):

    is_active: bool


class ServicePlanResponse(BaseModel):

    id: int
    plan_code: str
    plan_name: str
    plan_type: str

    data_limit: float
    voice_limit: int
    sms_limit: int

    validity_days: int
    price: float

    description: str | None

    is_active: bool

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class ServicePlanComparisonResponse(BaseModel):

    id: int
    plan_code: str
    plan_name: str
    plan_type: str

    data_limit: float
    voice_limit: int
    sms_limit: int

    validity_days: int
    price: float

    is_active: bool

    model_config = ConfigDict(
        from_attributes=True
    )