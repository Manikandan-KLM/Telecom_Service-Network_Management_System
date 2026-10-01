from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):

    full_name: str = Field(
        min_length=2,
        max_length=100
    )

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=100
    )


class LoginResponse(BaseModel):

    access_token: str

    refresh_token: str

    token_type: str = "bearer"


class RefreshRequest(BaseModel):

    refresh_token: str


class LogoutRequest(BaseModel):

    refresh_token: str


class ChangePasswordRequest(BaseModel):

    current_password: str

    new_password: str = Field(
        min_length=8,
        max_length=100
    )


class ForgotPasswordRequest(BaseModel):

    email: EmailStr


class ResetPasswordRequest(BaseModel):

    token: str

    new_password: str = Field(
        min_length=8,
        max_length=100
    )