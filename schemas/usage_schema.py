from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class UsageCreateRequest(BaseModel):
    subscription_id: int

    usage_type: str

    usage_amount: float = Field(
        gt=0
    )

    usage_date: datetime | None = None


class UsageResponse(BaseModel):
    id: int
    customer_id: int
    sim_id: int
    subscription_id: int
    usage_type: str
    usage_amount: float
    usage_date: datetime
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class UsageSummaryResponse(BaseModel):
    customer_id: int
    sim_id: int
    subscription_id: int

    data_used: float
    voice_used: float
    sms_used: float

    data_quota: float
    voice_quota: float
    sms_quota: float

    data_percentage: float
    voice_percentage: float
    sms_percentage: float

    data_remaining: float
    voice_remaining: float
    sms_remaining: float


class UsagePercentageResponse(BaseModel):
    usage_type: str
    used: float
    quota: float
    percentage: float
    remaining: float