from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UserResponse(BaseModel):

    id: int

    full_name: str

    email: str

    role: str

    is_active: bool

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class ChangeRoleRequest(BaseModel):

    role: str


class AccountStatusRequest(BaseModel):

    is_active: bool