from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SubscriptionCreateRequest(BaseModel):
    customer_id: int
    sim_id: int
    plan_id: int


class SubscriptionPlanChangeRequest(BaseModel):
    new_plan_id: int


class SubscriptionStatusRequest(BaseModel):
    status: str


class SubscriptionResponse(BaseModel):
    id: int
    customer_id: int
    sim_id: int
    plan_id: int
    start_date: datetime
    end_date: datetime
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class SubscriptionHistoryResponse(BaseModel):
    id: int
    subscription_id: int
    old_plan_id: int | None
    new_plan_id: int | None
    old_status: str | None
    new_status: str | None
    action: str
    description: str | None
    changed_by: int
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )