import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch

from routes import auth
from database import get_db
from utils.dependencies import get_current_user


# ============================================================
# Test App Setup
# ============================================================

app = FastAPI()

app.include_router(auth.router)


def override_get_db():
    db = MagicMock()
    yield db


app.dependency_overrides[get_db] = override_get_db


# ============================================================
# Test Client
# ============================================================

client = TestClient(app)


# ============================================================
# Mock User Helper
# ============================================================

def create_mock_user(
    user_id=1,
    full_name="Test User",
    email="test@example.com",
    role="Customer",
    is_active=True,
    hashed_password="hashed_password"
):
    user = MagicMock()

    user.id = user_id
    user.full_name = full_name
    user.email = email
    user.role = role
    user.is_active = is_active
    user.hashed_password = hashed_password

    return user



def test_register_invalid_email():

    response = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Test User",
            "email": "invalid-email",
            "password": "password123"
        }
    )

    assert response.status_code == 422


def test_register_short_password():

    response = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Test User",
            "email": "test@example.com",
            "password": "123"
        }
    )

    assert response.status_code == 422


def test_register_short_name():

    response = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "A",
            "email": "test@example.com",
            "password": "password123"
        }
    )

    assert response.status_code == 422


def test_login_missing_username():

    response = client.post(
        "/api/v1/auth/login",
        data={
            "password": "password123"
        }
    )

    assert response.status_code == 422


def test_login_missing_password():

    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "test@example.com"
        }
    )

    assert response.status_code == 422



def test_logout_missing_refresh_token():

    response = client.post(
        "/api/v1/auth/logout",
        json={}
    )

    assert response.status_code == 422



def test_change_password_short_new_password():

    mock_user = create_mock_user()

    app.dependency_overrides[
        get_current_user
    ] = lambda: mock_user

    response = client.post(
        "/api/v1/auth/change-password",
        json={
            "current_password": "oldpassword",
            "new_password": "short"
        }
    )

    assert response.status_code == 422

    app.dependency_overrides.pop(
        get_current_user,
        None
    )



def test_forgot_password_invalid_email():

    response = client.post(
        "/api/v1/auth/forgot-password",
        json={
            "email": "invalid-email"
        }
    )

    assert response.status_code == 422



def test_reset_password_short_password():

    response = client.post(
        "/api/v1/auth/reset-password",
        json={
            "token": "reset-token",
            "new_password": "short"
        }
    )

    assert response.status_code == 422


# ============================================================
# 8. ROUTE VALIDATION
# ============================================================

def test_register_missing_fields():

    response = client.post(
        "/api/v1/auth/register",
        json={}
    )

    assert response.status_code == 422


def test_refresh_missing_body():

    response = client.post(
        "/api/v1/auth/refresh",
        json={}
    )

    assert response.status_code == 422


def test_logout_missing_body():

    response = client.post(
        "/api/v1/auth/logout",
        json={}
    )

    assert response.status_code == 422


def test_reset_password_missing_token():

    response = client.post(
        "/api/v1/auth/reset-password",
        json={
            "new_password": "newpassword123"
        }
    )

    assert response.status_code == 422