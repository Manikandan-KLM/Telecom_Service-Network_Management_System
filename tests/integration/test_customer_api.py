import pytest

from fastapi.testclient import TestClient

from main import app
from database import get_db
from utils.dependencies import get_current_user

from models.user_model import User


client = TestClient(app)


# ============================================================
# TEST USER
# ============================================================

test_user = User(
    id=1,
    email="admin@test.com",
    role="Super Admin",
    is_active=True
)


# ============================================================
# OVERRIDE CURRENT USER
# ============================================================

def override_get_current_user():
    return test_user


app.dependency_overrides[
    get_current_user
] = override_get_current_user


# ============================================================
# DATABASE OVERRIDE
# ============================================================

@pytest.fixture
def db_session():
    """
    Replace this with your test database session
    if your project already has a conftest.py database fixture.
    """

    yield None


# ============================================================
# TEST DATA
# ============================================================

def customer_data():

    return {
        "full_name": "Test Customer",
        "email": "testcustomer@example.com",
        "phone": "9876543210",
        "address_line1": "123 Main Street",
        "address_line2": "Near Bus Stand",
        "city": "Nagercoil",
        "state": "Tamil Nadu",
        "postal_code": "629001",
        "country": "India"
    }


# ============================================================
# 1. CREATE CUSTOMER
# ============================================================

def test_create_customer():

    response = client.post(
        "/api/v1/customers",
        json=customer_data()
    )

    assert response.status_code == 201

    data = response.json()

    assert "id" in data
    assert "user_id" in data
    assert "customer_number" in data

    assert data["full_name"] == "Test Customer"
    assert data["email"] == "testcustomer@example.com"
    assert data["phone"] == "9876543210"

    assert data["city"] == "Nagercoil"
    assert data["state"] == "Tamil Nadu"

    assert "kyc_status" in data
    assert "is_active" in data


# ============================================================
# 2. GET CUSTOMER
# ============================================================

def test_get_customer():

    create_response = client.post(
        "/api/v1/customers",
        json=customer_data()
    )

    assert create_response.status_code == 201

    customer_id = create_response.json()["id"]

    response = client.get(
        f"/api/v1/customers/{customer_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == customer_id
    assert data["full_name"] == "Test Customer"


# ============================================================
# 3. CUSTOMER NOT FOUND
# ============================================================

def test_get_customer_not_found():

    response = client.get(
        "/api/v1/customers/999999"
    )

    assert response.status_code == 404


# ============================================================
# 4. UPDATE CUSTOMER PROFILE
# ============================================================

def test_update_customer_profile():

    create_response = client.post(
        "/api/v1/customers",
        json=customer_data()
    )

    assert create_response.status_code == 201

    customer_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/customers/{customer_id}",
        json={
            "full_name": "Updated Customer",
            "phone": "9999999999"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["full_name"] == "Updated Customer"
    assert data["phone"] == "9999999999"


# ============================================================
# 5. UPDATE CONTACT
# ============================================================

def test_update_customer_contact():

    create_response = client.post(
        "/api/v1/customers",
        json=customer_data()
    )

    assert create_response.status_code == 201

    customer_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/customers/{customer_id}/contact",
        json={
            "phone": "8888888888"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["phone"] == "8888888888"


# ============================================================
# 6. UPDATE ADDRESS
# ============================================================

def test_update_customer_address():

    create_response = client.post(
        "/api/v1/customers",
        json=customer_data()
    )

    assert create_response.status_code == 201

    customer_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/customers/{customer_id}/address",
        json={
            "address_line1": "456 New Street",
            "address_line2": "Near Railway Station",
            "city": "Chennai",
            "state": "Tamil Nadu",
            "postal_code": "600001",
            "country": "India"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["address_line1"] == "456 New Street"
    assert data["city"] == "Chennai"
    assert data["postal_code"] == "600001"


# ============================================================
# 7. UPDATE KYC
# ============================================================

def test_update_kyc_status():

    create_response = client.post(
        "/api/v1/customers",
        json=customer_data()
    )

    assert create_response.status_code == 201

    customer_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/customers/{customer_id}/kyc",
        json={
            "kyc_status": "Verified"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["kyc_status"] == "Verified"


# ============================================================
# 8. DEACTIVATE CUSTOMER
# ============================================================

def test_deactivate_customer():

    create_response = client.post(
        "/api/v1/customers",
        json=customer_data()
    )

    assert create_response.status_code == 201

    customer_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/customers/{customer_id}/status",
        json={
            "is_active": False
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["is_active"] is False


# ============================================================
# 9. ACTIVATE CUSTOMER
# ============================================================

def test_activate_customer():

    create_response = client.post(
        "/api/v1/customers",
        json=customer_data()
    )

    assert create_response.status_code == 201

    customer_id = create_response.json()["id"]

    # deactivate
    response = client.patch(
        f"/api/v1/customers/{customer_id}/status",
        json={
            "is_active": False
        }
    )

    assert response.status_code == 200

    # activate
    response = client.patch(
        f"/api/v1/customers/{customer_id}/status",
        json={
            "is_active": True
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["is_active"] is True


# ============================================================
# 10. SEARCH CUSTOMERS
# ============================================================

def test_search_customers():

    response = client.get(
        "/api/v1/customers"
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)


# ============================================================
# 11. SEARCH BY NAME
# ============================================================

def test_search_customer_by_name():

    response = client.get(
        "/api/v1/customers",
        params={
            "search": "Test"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)


# ============================================================
# 12. FILTER BY CITY
# ============================================================

def test_filter_customer_by_city():

    response = client.get(
        "/api/v1/customers",
        params={
            "city": "Nagercoil"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)


# ============================================================
# 13. FILTER BY ACTIVE STATUS
# ============================================================

def test_filter_customer_by_active_status():

    response = client.get(
        "/api/v1/customers",
        params={
            "is_active": True
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)


# ============================================================
# 14. FILTER BY KYC
# ============================================================

def test_filter_customer_by_kyc_status():

    response = client.get(
        "/api/v1/customers",
        params={
            "kyc_status": "Verified"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)


# ============================================================
# 15. CUSTOMER HISTORY
# ============================================================

def test_customer_history():

    create_response = client.post(
        "/api/v1/customers",
        json=customer_data()
    )

    assert create_response.status_code == 201

    customer_id = create_response.json()["id"]

    response = client.get(
        f"/api/v1/customers/{customer_id}/history"
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)


# ============================================================
# 16. INVALID EMAIL
# ============================================================

def test_create_customer_invalid_email():

    data = customer_data()

    data["email"] = "invalid-email"

    response = client.post(
        "/api/v1/customers",
        json=data
    )

    assert response.status_code == 422


# ============================================================
# 17. INVALID PHONE
# ============================================================

def test_create_customer_invalid_phone():

    data = customer_data()

    data["phone"] = "123"

    response = client.post(
        "/api/v1/customers",
        json=data
    )

    assert response.status_code == 422


# ============================================================
# 18. MISSING FULL NAME
# ============================================================

def test_create_customer_missing_name():

    data = customer_data()

    del data["full_name"]

    response = client.post(
        "/api/v1/customers",
        json=data
    )

    assert response.status_code == 422


# ============================================================
# 19. INVALID CUSTOMER ID
# ============================================================

def test_get_customer_invalid_id():

    response = client.get(
        "/api/v1/customers/abc"
    )

    assert response.status_code == 422

