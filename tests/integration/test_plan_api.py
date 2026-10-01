from fastapi.testclient import TestClient

from main import app
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
# AUTH OVERRIDE
# ============================================================

def override_get_current_user():
    return test_user


app.dependency_overrides[
    get_current_user
] = override_get_current_user


# ============================================================
# TEST DATA
# ============================================================

def plan_data():

    return {
        "plan_code": "TEST100",
        "plan_name": "Test Basic Plan",
        "plan_type": "Prepaid",
        "data_limit": 10.0,
        "voice_limit": 100,
        "sms_limit": 100,
        "validity_days": 28,
        "price": 199.0,
        "description": "Test service plan"
    }


# ============================================================
# 1. CREATE PLAN
# ============================================================

def test_create_plan():

    response = client.post(
        "/api/v1/plans",
        json=plan_data()
    )

    assert response.status_code == 201

    data = response.json()

    assert "id" in data
    assert data["plan_code"] == "TEST100"
    assert data["plan_name"] == "Test Basic Plan"
    assert data["plan_type"] == "Prepaid"

    assert data["data_limit"] == 10.0
    assert data["voice_limit"] == 100
    assert data["sms_limit"] == 100

    assert data["validity_days"] == 28
    assert data["price"] == 199.0

    assert data["is_active"] is True



# ============================================================
# 3. GET PLAN NOT FOUND
# ============================================================

def test_get_plan_not_found():

    response = client.get(
        "/api/v1/plans/999999"
    )

    assert response.status_code == 404





# ============================================================
# 5. UPDATE PLAN PARTIALLY
# ============================================================

def test_update_plan_partial():

    create_response = client.post(
        "/api/v1/plans",
        json=plan_data()
    )

    assert create_response.status_code == 201

    plan_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/plans/{plan_id}",
        json={
            "plan_name": "Partial Updated Plan"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["plan_name"] == "Partial Updated Plan"


# ============================================================
# 9. SEARCH BY NAME
# ============================================================

def test_search_plan_by_name():

    response = client.get(
        "/api/v1/plans",
        params={
            "search": "Basic"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)


# ============================================================
# 10. FILTER BY PLAN TYPE
# ============================================================

def test_filter_plan_by_type():

    response = client.get(
        "/api/v1/plans",
        params={
            "plan_type": "Prepaid"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)


# ============================================================
# 11. FILTER BY ACTIVE STATUS
# ============================================================

def test_filter_plan_by_active_status():

    response = client.get(
        "/api/v1/plans",
        params={
            "is_active": True
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)


# ============================================================
# 12. FILTER BY MIN PRICE
# ============================================================

def test_filter_plan_by_min_price():

    response = client.get(
        "/api/v1/plans",
        params={
            "min_price": 100
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)


# ============================================================
# 13. FILTER BY MAX PRICE
# ============================================================

def test_filter_plan_by_max_price():

    response = client.get(
        "/api/v1/plans",
        params={
            "max_price": 500
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)


# ============================================================
# 14. FILTER BY MIN VALIDITY
# ============================================================

def test_filter_plan_by_min_validity():

    response = client.get(
        "/api/v1/plans",
        params={
            "min_validity": 28
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)


# ============================================================
# 15. COMBINATION FILTER
# ============================================================

def test_filter_plans_multiple_filters():

    response = client.get(
        "/api/v1/plans",
        params={
            "plan_type": "Prepaid",
            "is_active": True,
            "min_price": 100,
            "max_price": 500,
            "min_validity": 20
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)





# ============================================================
# 19. INVALID CREATE PLAN - CODE
# ============================================================

def test_create_plan_invalid_code():

    data = plan_data()

    data["plan_code"] = "AB"

    response = client.post(
        "/api/v1/plans",
        json=data
    )

    assert response.status_code == 422


# ============================================================
# 20. INVALID CREATE PLAN - NAME
# ============================================================

def test_create_plan_invalid_name():

    data = plan_data()

    data["plan_name"] = "A"

    response = client.post(
        "/api/v1/plans",
        json=data
    )

    assert response.status_code == 422


# ============================================================
# 21. INVALID DATA LIMIT
# ============================================================

def test_create_plan_negative_data_limit():

    data = plan_data()

    data["data_limit"] = -1

    response = client.post(
        "/api/v1/plans",
        json=data
    )

    assert response.status_code == 422


# ============================================================
# 22. INVALID VOICE LIMIT
# ============================================================

def test_create_plan_negative_voice_limit():

    data = plan_data()

    data["voice_limit"] = -1

    response = client.post(
        "/api/v1/plans",
        json=data
    )

    assert response.status_code == 422


# ============================================================
# 23. INVALID SMS LIMIT
# ============================================================

def test_create_plan_negative_sms_limit():

    data = plan_data()

    data["sms_limit"] = -1

    response = client.post(
        "/api/v1/plans",
        json=data
    )

    assert response.status_code == 422


# ============================================================
# 24. INVALID VALIDITY
# ============================================================

def test_create_plan_invalid_validity():

    data = plan_data()

    data["validity_days"] = 0

    response = client.post(
        "/api/v1/plans",
        json=data
    )

    assert response.status_code == 422


# ============================================================
# 25. INVALID PRICE
# ============================================================

def test_create_plan_negative_price():

    data = plan_data()

    data["price"] = -100

    response = client.post(
        "/api/v1/plans",
        json=data
    )

    assert response.status_code == 422


# ============================================================
# 26. MISSING REQUIRED FIELD
# ============================================================

def test_create_plan_missing_plan_code():

    data = plan_data()

    del data["plan_code"]

    response = client.post(
        "/api/v1/plans",
        json=data
    )

    assert response.status_code == 422


# ============================================================
# 27. INVALID PLAN ID
# ============================================================

def test_get_plan_invalid_id():

    response = client.get(
        "/api/v1/plans/abc"
    )

    assert response.status_code == 422


# ============================================================
# 28. UPDATE NON EXISTING PLAN
# ============================================================

def test_update_non_existing_plan():

    response = client.patch(
        "/api/v1/plans/999999",
        json={
            "plan_name": "Updated Plan"
        }
    )

    assert response.status_code == 404


# ============================================================
# 29. STATUS REQUEST VALIDATION
# ============================================================

def test_invalid_plan_status_request():

    response = client.patch(
        "/api/v1/plans/999999/status",
        json={}
    )

    assert response.status_code == 422