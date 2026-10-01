from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SLARuleCreateRequest(BaseModel):

    rule_name: str = Field(
        min_length=3,
        max_length=100
    )

    ticket_type: str

    priority: str

    customer_type: str

    response_time_minutes: int = Field(
        gt=0
    )

    resolution_time_minutes: int = Field(
        gt=0
    )


class SLARuleResponse(BaseModel):

    id: int
    rule_name: str
    ticket_type: str
    priority: str
    customer_type: str

    response_time_minutes: int
    resolution_time_minutes: int

    is_active: bool

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class TicketSLAResponse(BaseModel):

    id: int
    ticket_id: int
    sla_rule_id: int

    sla_start_time: datetime
    sla_deadline: datetime

    resolution_time_minutes: int | None

    actual_resolution_time: datetime | None

    sla_breached: bool

    escalation_status: str

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )