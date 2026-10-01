from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AuditLogResponse(BaseModel):

    id: int

    user_id: int | None

    action: str

    entity: str

    entity_id: str | None

    previous_value: str | None

    new_value: str | None

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )