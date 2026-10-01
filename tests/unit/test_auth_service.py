import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

from fastapi import HTTPException

from services.auth_service import AuthService


# ============================================================
# REGISTER
# ============================================================

@patch("services.auth_service.UserRepository")
@patch("services.auth_service.hash_password")
def test_register_success(
    mock_hash_password,
    mock_user_repository
):
    db = MagicMock()

    mock_hash_password.return_value = "hashed_password"

    mock_user_repository.get_by_email.return_value = None

    fake_user = MagicMock()
    fake_user.email = "test@example.com"
    fake_user.role = "Customer"
    fake_user.is_active = True

    mock_user_repository.create.return_value = fake_user

    result = AuthService.register(
        db=db,
        full_name="Test User",
        email="test@example.com",
        password="password123"
    )

    assert result == fake_user

    mock_user_repository.get_by_email.assert_called_once_with(
        db,
        "test@example.com"
    )

    mock_hash_password.assert_called_once_with(
        "password123"
    )

    mock_user_repository.create.assert_called_once()


# ============================================================
# REGISTER - DUPLICATE EMAIL
# ============================================================

@patch("services.auth_service.UserRepository")
def test_register_duplicate_email(
    mock_user_repository
):
    db = MagicMock()

    existing_user = MagicMock()

    mock_user_repository.get_by_email.return_value = existing_user

    with pytest.raises(HTTPException) as exc_info:

        AuthService.register(
            db=db,
            full_name="Test User",
            email="test@example.com",
            password="password123"
        )

    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == "Email already registered"

    mock_user_repository.create.assert_not_called()


# ============================================================
# AUTHENTICATE - SUCCESS
# ============================================================

@patch("services.auth_service.verify_password")
@patch("services.auth_service.UserRepository")
def test_authenticate_success(
    mock_user_repository,
    mock_verify_password
):
    db = MagicMock()

    fake_user = MagicMock()
    fake_user.email = "test@example.com"
    fake_user.hashed_password = "hashed_password"
    fake_user.is_active = True

    mock_user_repository.get_by_email.return_value = fake_user
    mock_verify_password.return_value = True

    result = AuthService.authenticate(
        db=db,
        email="test@example.com",
        password="password123"
    )

    assert result == fake_user

    mock_user_repository.get_by_email.assert_called_once_with(
        db,
        "test@example.com"
    )

    mock_verify_password.assert_called_once_with(
        "password123",
        "hashed_password"
    )


# ============================================================
# AUTHENTICATE - USER NOT FOUND
# ============================================================

@patch("services.auth_service.UserRepository")
def test_authenticate_invalid_email(
    mock_user_repository
):
    db = MagicMock()

    mock_user_repository.get_by_email.return_value = None

    with pytest.raises(HTTPException) as exc_info:

        AuthService.authenticate(
            db=db,
            email="wrong@example.com",
            password="password123"
        )

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid email or password"


# ============================================================
# AUTHENTICATE - WRONG PASSWORD
# ============================================================

@patch("services.auth_service.verify_password")
@patch("services.auth_service.UserRepository")
def test_authenticate_wrong_password(
    mock_user_repository,
    mock_verify_password
):
    db = MagicMock()

    fake_user = MagicMock()
    fake_user.hashed_password = "hashed_password"
    fake_user.is_active = True

    mock_user_repository.get_by_email.return_value = fake_user
    mock_verify_password.return_value = False

    with pytest.raises(HTTPException) as exc_info:

        AuthService.authenticate(
            db=db,
            email="test@example.com",
            password="wrongpassword"
        )

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid email or password"


# ============================================================
# AUTHENTICATE - DEACTIVATED ACCOUNT
# ============================================================

@patch("services.auth_service.verify_password")
@patch("services.auth_service.UserRepository")
def test_authenticate_deactivated_user(
    mock_user_repository,
    mock_verify_password
):
    db = MagicMock()

    fake_user = MagicMock()
    fake_user.hashed_password = "hashed_password"
    fake_user.is_active = False

    mock_user_repository.get_by_email.return_value = fake_user
    mock_verify_password.return_value = True

    with pytest.raises(HTTPException) as exc_info:

        AuthService.authenticate(
            db=db,
            email="test@example.com",
            password="password123"
        )

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Account is deactivated"


# ============================================================
# CREATE TOKENS
# ============================================================

@patch("services.auth_service.create_token")
def test_create_tokens(
    mock_create_token
):
    fake_user = MagicMock()
    fake_user.id = 1

    mock_create_token.side_effect = [
        ("access_token_value", datetime.now(timezone.utc)),
        ("refresh_token_value", datetime.now(timezone.utc))
    ]

    result = AuthService.create_tokens(fake_user)

    assert result["access_token"] == "access_token_value"
    assert result["refresh_token"] == "refresh_token_value"
    assert result["token_type"] == "bearer"

    assert mock_create_token.call_count == 2


# ============================================================
# CREATE PASSWORD RESET
# ============================================================

@patch("services.auth_service.PasswordResetRepository")
@patch("services.auth_service.hash_reset_token")
@patch("services.auth_service.generate_reset_token")
@patch("services.auth_service.UserRepository")
def test_create_password_reset_success(
    mock_user_repository,
    mock_generate_reset_token,
    mock_hash_reset_token,
    mock_password_reset_repository
):
    db = MagicMock()

    fake_user = MagicMock()
    fake_user.id = 1

    mock_user_repository.get_by_email.return_value = fake_user

    mock_generate_reset_token.return_value = "raw-reset-token"

    mock_hash_reset_token.return_value = "hashed-reset-token"

    result = AuthService.create_password_reset(
        db=db,
        email="test@example.com"
    )

    assert result == "raw-reset-token"

    mock_user_repository.get_by_email.assert_called_once_with(
        db,
        "test@example.com"
    )

    mock_generate_reset_token.assert_called_once()

    mock_hash_reset_token.assert_called_once_with(
        "raw-reset-token"
    )

    mock_password_reset_repository.create.assert_called_once()


# ============================================================
# CREATE PASSWORD RESET - USER NOT FOUND
# ============================================================

@patch("services.auth_service.UserRepository")
def test_create_password_reset_user_not_found(
    mock_user_repository
):
    db = MagicMock()

    mock_user_repository.get_by_email.return_value = None

    result = AuthService.create_password_reset(
        db=db,
        email="unknown@example.com"
    )

    assert result is None


# ============================================================
# RESET PASSWORD - SUCCESS
# ============================================================

@patch("services.auth_service.PasswordResetRepository")
@patch("services.auth_service.UserRepository")
@patch("services.auth_service.hash_password")
@patch("services.auth_service.hash_reset_token")
def test_reset_password_success(
    mock_hash_reset_token,
    mock_hash_password,
    mock_user_repository,
    mock_password_reset_repository
):
    db = MagicMock()

    mock_hash_reset_token.return_value = "hashed-token"

    reset_record = MagicMock()

    reset_record.user_id = 1
    reset_record.used = False
    reset_record.expires_at = (
        datetime.now(timezone.utc)
        + timedelta(minutes=10)
    )

    fake_user = MagicMock()
    fake_user.id = 1

    mock_password_reset_repository.get_valid_token.return_value = (
        reset_record
    )

    mock_user_repository.get_by_id.return_value = fake_user

    mock_hash_password.return_value = "new_hashed_password"

    result = AuthService.reset_password(
        db=db,
        token="raw-token",
        new_password="newpassword123"
    )

    assert result == fake_user

    mock_hash_reset_token.assert_called_once_with(
        "raw-token"
    )

    mock_hash_password.assert_called_once_with(
        "newpassword123"
    )

    assert fake_user.hashed_password == "new_hashed_password"
    assert reset_record.used is True

    mock_user_repository.update.assert_called_once_with(
        db,
        fake_user
    )

    mock_password_reset_repository.update.assert_called_once_with(
        db,
        reset_record
    )


# ============================================================
# RESET PASSWORD - INVALID TOKEN
# ============================================================

@patch("services.auth_service.PasswordResetRepository")
@patch("services.auth_service.hash_reset_token")
def test_reset_password_invalid_token(
    mock_hash_reset_token,
    mock_password_reset_repository
):
    db = MagicMock()

    mock_hash_reset_token.return_value = "hashed-token"

    mock_password_reset_repository.get_valid_token.return_value = None

    with pytest.raises(HTTPException) as exc_info:

        AuthService.reset_password(
            db=db,
            token="invalid-token",
            new_password="newpassword123"
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Invalid reset token"


# ============================================================
# RESET PASSWORD - EXPIRED TOKEN
# ============================================================

@patch("services.auth_service.PasswordResetRepository")
@patch("services.auth_service.hash_reset_token")
def test_reset_password_expired_token(
    mock_hash_reset_token,
    mock_password_reset_repository
):
    db = MagicMock()

    mock_hash_reset_token.return_value = "hashed-token"

    reset_record = MagicMock()

    reset_record.expires_at = (
        datetime.now(timezone.utc)
        - timedelta(minutes=10)
    )

    mock_password_reset_repository.get_valid_token.return_value = (
        reset_record
    )

    with pytest.raises(HTTPException) as exc_info:

        AuthService.reset_password(
            db=db,
            token="expired-token",
            new_password="newpassword123"
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Reset token expired"


# ============================================================
# RESET PASSWORD - USER NOT FOUND
# ============================================================

@patch("services.auth_service.PasswordResetRepository")
@patch("services.auth_service.UserRepository")
@patch("services.auth_service.hash_reset_token")
def test_reset_password_user_not_found(
    mock_hash_reset_token,
    mock_user_repository,
    mock_password_reset_repository
):
    db = MagicMock()

    mock_hash_reset_token.return_value = "hashed-token"

    reset_record = MagicMock()

    reset_record.user_id = 999
    reset_record.expires_at = (
        datetime.now(timezone.utc)
        + timedelta(minutes=10)
    )

    mock_password_reset_repository.get_valid_token.return_value = (
        reset_record
    )

    mock_user_repository.get_by_id.return_value = None

    with pytest.raises(HTTPException) as exc_info:

        AuthService.reset_password(
            db=db,
            token="valid-token",
            new_password="newpassword123"
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "User not found"
