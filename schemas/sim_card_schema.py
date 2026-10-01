from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SIMCardCreateRequest(BaseModel):
    sim_number: str = Field(
        min_length=10,
        max_length=30
    )

    sim_type: str

    customer_id: int | None = None

    plan_id: int | None = None


class SIMCardUpdateRequest(BaseModel):
    sim_type: str | None = None
    customer_id: int | None = None
    plan_id: int | None = None


class SIMStatusRequest(BaseModel):
    status: str


class SIMReplacementRequest(BaseModel):
    new_sim_id: int
    reason: str = Field(
        min_length=3,
        max_length=100
    )
    remarks: str | None = None


class SIMCardResponse(BaseModel):
    id: int
    sim_number: str
    sim_type: str
    status: str
    activation_date: datetime | None
    customer_id: int | None
    plan_id: int | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class SIMReplacementHistoryResponse(BaseModel):
    id: int
    old_sim_id: int
    new_sim_id: int
    customer_id: int
    reason: str
    remarks: str | None
    replaced_by: int
    replaced_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )