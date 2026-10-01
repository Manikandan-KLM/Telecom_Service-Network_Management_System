from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class CustomerCreateRequest(BaseModel):
    full_name: str = Field(
        min_length=2,
        max_length=100
    )

    email: EmailStr

    phone: str = Field(
        min_length=7,
        max_length=20
    )

    address_line1: str = Field(
        min_length=3,
        max_length=255
    )

    address_line2: str | None = Field(
        default=None,
        max_length=255
    )

    city: str = Field(
        min_length=2,
        max_length=100
    )

    state: str = Field(
        min_length=2,
        max_length=100
    )

    postal_code: str = Field(
        min_length=3,
        max_length=20
    )

    country: str = Field(
        default="India",
        max_length=100
    )


class CustomerUpdateRequest(BaseModel):
    full_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100
    )

    phone: str | None = Field(
        default=None,
        min_length=7,
        max_length=20
    )


class CustomerContactUpdateRequest(BaseModel):
    phone: str = Field(
        min_length=7,
        max_length=20
    )


class CustomerAddressUpdateRequest(BaseModel):
    address_line1: str = Field(
        min_length=3,
        max_length=255
    )

    address_line2: str | None = Field(
        default=None,
        max_length=255
    )

    city: str = Field(
        min_length=2,
        max_length=100
    )

    state: str = Field(
        min_length=2,
        max_length=100
    )

    postal_code: str = Field(
        min_length=3,
        max_length=20
    )

    country: str = Field(
        default="India",
        max_length=100
    )


class KYCStatusRequest(BaseModel):
    kyc_status: str


class CustomerStatusRequest(BaseModel):
    is_active: bool


class CustomerResponse(BaseModel):
    id: int
    user_id: int
    customer_number: str
    full_name: str
    email: str
    phone: str

    address_line1: str
    address_line2: str | None

    city: str
    state: str
    postal_code: str
    country: str

    kyc_status: str
    is_active: bool

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class CustomerHistoryResponse(BaseModel):
    id: int
    customer_id: int
    action: str
    description: str
    changed_by: int | None
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )