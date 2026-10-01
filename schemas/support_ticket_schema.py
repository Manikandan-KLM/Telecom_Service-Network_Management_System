from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# =====================================================
# CREATE TICKET
# =====================================================

class SupportTicketCreateRequest(BaseModel):

    ticket_type: str

    subject: str = Field(
        min_length=3,
        max_length=200
    )

    description: str = Field(
        min_length=5,
        max_length=5000
    )

    priority: str = "Medium"


# =====================================================
# ASSIGN TICKET
# =====================================================

class SupportTicketAssignRequest(BaseModel):

    assigned_to: int


# =====================================================
# STATUS UPDATE
# =====================================================

class SupportTicketStatusRequest(BaseModel):

    status: str

    resolution_notes: str | None = None


# =====================================================
# RESPONSE
# =====================================================

class SupportTicketResponse(BaseModel):

    id: int
    ticket_number: str
    customer_id: int
    assigned_to: int | None

    ticket_type: str
    subject: str
    description: str

    priority: str
    status: str

    resolution_notes: str | None

    created_at: datetime
    updated_at: datetime

    resolved_at: datetime | None
    closed_at: datetime | None

    model_config = ConfigDict(
        from_attributes=True
    )



from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SupportTicketCreateRequest(BaseModel):
    ticket_type: str
    subject: str = Field(min_length=3, max_length=200)
    description: str = Field(min_length=5, max_length=5000)
    priority: str = "Medium"


class AgentAssignmentRequest(BaseModel):
    agent_id: int


class TechnicianAssignmentRequest(BaseModel):
    technician_id: int


class PriorityUpdateRequest(BaseModel):
    priority: str


class EscalationRequest(BaseModel):
    escalation_reason: str = Field(
        min_length=5,
        max_length=1000
    )


class InternalCommentRequest(BaseModel):
    comment: str = Field(
        min_length=1,
        max_length=5000
    )


class SupportTicketStatusRequest(BaseModel):
    status: str
    resolution_notes: str | None = None


class SupportTicketResponse(BaseModel):
    id: int
    ticket_number: str
    customer_id: int

    assigned_agent_id: int | None
    assigned_technician_id: int | None

    ticket_type: str
    subject: str
    description: str

    priority: str
    status: str

    escalation_level: int
    escalation_reason: str | None

    resolution_notes: str | None

    created_at: datetime
    updated_at: datetime
    resolved_at: datetime | None
    closed_at: datetime | None

    model_config = ConfigDict(
        from_attributes=True
    )


class TicketHistoryResponse(BaseModel):
    id: int
    ticket_id: int
    changed_by: int
    action: str
    description: str
    old_value: str | None
    new_value: str | None
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class TicketCommentResponse(BaseModel):
    id: int
    ticket_id: int
    user_id: int
    comment: str
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )