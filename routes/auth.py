from fastapi import APIRouter, Depends, Form, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db

from schemas.auth_schema import (
    RegisterRequest,
    LoginResponse,
    RefreshRequest,
    LogoutRequest,
    ChangePasswordRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
)

from services.auth_service import AuthService

from utils.dependencies import get_current_user
from utils.security import (
    decode_token,
    hash_password,
    verify_password,
)

from models.user_model import User
from models.token_model import RevokedToken
from repositories.user_repository import UserRepository
from repositories.token_repository import TokenRepository


router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Authentication"]
)


# ============================================================
# 1. USER REGISTRATION
# ============================================================

@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED
)
def register(
    request: RegisterRequest,
    db: Session = Depends(get_db)
):
    """
    Register a new customer account.

    Public registration always creates a Customer.
    Role cannot be selected during registration.
    """

    user = AuthService.register(
        db=db,
        full_name=request.full_name,
        email=request.email,
        password=request.password
    )

    return {
        "message": "Registration successful",
        "user_id": user.id,
        "role": user.role
    }


# ============================================================
# 2. LOGIN
# ============================================================

@router.post(
    "/login",
    response_model=LoginResponse
)
def login(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Login using email and password.

    Returns:
        - Access Token
        - Refresh Token
    """

    user = AuthService.authenticate(
        db=db,
        email=username,
        password=password
    )

    tokens = AuthService.create_tokens(user)

    return tokens


# ============================================================
# 3. REFRESH TOKEN
# ============================================================

@router.post(
    "/refresh",
    response_model=LoginResponse
)
def refresh_token(
    request: RefreshRequest,
    db: Session = Depends(get_db)
):
    """
    Generate new access and refresh tokens.

    Old refresh token will be revoked.
    """

    try:
        payload = decode_token(
            request.refresh_token
        )

    except ValueError:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )

    # Check token type
    if payload.get("type") != "refresh":

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token required"
        )

    jti = payload.get("jti")

    if not jti:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    # Check whether token was already revoked
    revoked_token = TokenRepository.get_by_jti(
        db,
        jti
    )

    if revoked_token:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has been revoked"
        )

    # Get user ID from token
    user_id = payload.get("sub")

    if not user_id:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    # Get user through repository
    user = UserRepository.get_by_id(
        db,
        int(user_id)
    )

    if not user:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Check account status
    if not user.is_active:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated"
        )

    # Revoke old refresh token
    AuthService.revoke_token(
        db,
        request.refresh_token
    )

    # Generate new tokens
    return AuthService.create_tokens(user)


# ============================================================
# 4. LOGOUT
# ============================================================

@router.post("/logout")
def logout(
    request: LogoutRequest,
    db: Session = Depends(get_db)
):
    """
    Revoke refresh token.
    """

    AuthService.revoke_token(
        db,
        request.refresh_token
    )

    return {
        "message": "Logout successful"
    }


# ============================================================
# 5. CHANGE PASSWORD
# ============================================================

@router.post("/change-password")
def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Change password for logged-in user.
    """

    # Verify old password
    if not verify_password(
        request.current_password,
        current_user.hashed_password
    ):

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )

    # Prevent same password
    if request.current_password == request.new_password:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different"
        )

    # Hash new password
    current_user.hashed_password = hash_password(
        request.new_password
    )

    # Save using repository
    UserRepository.update(
        db,
        current_user
    )

    return {
        "message": "Password changed successfully"
    }


# ============================================================
# 6. FORGOT PASSWORD
# ============================================================

@router.post("/forgot-password")
def forgot_password(
    request: ForgotPasswordRequest,
    db: Session = Depends(get_db)
):
    """
    Generate password reset token.

    Production:
        Send reset link through email.

    Development:
        Token is returned for testing.
    """

    reset_token = AuthService.create_password_reset(
        db=db,
        email=request.email
    )

    response = {
        "message": (
            "If the email exists, "
            "a password reset link will be sent."
        )
    }

    # --------------------------------------------------------
    # DEVELOPMENT ONLY
    # --------------------------------------------------------
    if reset_token:

        response["development_reset_token"] = reset_token

    return response


# ============================================================
# 7. RESET PASSWORD
# ============================================================

@router.post("/reset-password")
def reset_password(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    """
    Reset password using password reset token.
    """

    AuthService.reset_password(
        db=db,
        token=request.token,
        new_password=request.new_password
    )

    return {
        "message": "Password reset successful"
    }