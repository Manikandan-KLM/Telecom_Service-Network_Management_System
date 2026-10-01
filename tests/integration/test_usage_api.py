from datetime import date, datetime
from fastapi.testclient import TestClient

from main import app
from models.user_model import User
from utils.dependencies import get_current_user


# =====================================================
# TEST CLIENT
# =====================================================

client = TestClient(app)


# =====================================================
# AUTHENTICATION OVERRIDE
# =====================================================

test_user = User(
    id=1,
    email="admin@test.com",
    role="Super Admin",
    is_active=True
)


def override_get_current_user():
    return test_user


app.dependency_overrides[get_current_user] = override_get_current_user


# =====================================================
# 1. CREATE USAGE
# =====================================================

def test_create_usage():
    response = client.post(
        "/api/v1/usage",
        json={
            "subscription_id": 1,
            "usage_type": "Data",
            "usage_amount": 2.5,
            "usage_date": datetime.now().isoformat()
        }
    )

    assert response.status_code in [201, 400, 404]


# =====================================================
# 2. CREATE USAGE - MISSING SUBSCRIPTION ID
# =====================================================

def test_create_usage_missing_subscription_id():
    response = client.post(
        "/api/v1/usage",
        json={
            "usage_type": "Data",
            "usage_amount": 2.5
        }
    )

    assert response.status_code == 422


# =====================================================
# 3. CREATE USAGE - MISSING USAGE TYPE
# =====================================================

def test_create_usage_missing_usage_type():
    response = client.post(
        "/api/v1/usage",
        json={
            "subscription_id": 1,
            "usage_amount": 2.5
        }
    )

    assert response.status_code == 422


# =====================================================
# 4. CREATE USAGE - MISSING USAGE AMOUNT
# =====================================================

def test_create_usage_missing_amount():
    response = client.post(
        "/api/v1/usage",
        json={
            "subscription_id": 1,
            "usage_type": "Data"
        }
    )

    assert response.status_code == 422


# =====================================================
# 5. CREATE USAGE - ZERO AMOUNT
# =====================================================

def test_create_usage_zero_amount():
    response = client.post(
        "/api/v1/usage",
        json={
            "subscription_id": 1,
            "usage_type": "Data",
            "usage_amount": 0
        }
    )

    assert response.status_code == 422


# =====================================================
# 6. CREATE USAGE - NEGATIVE AMOUNT
# =====================================================

def test_create_usage_negative_amount():
    response = client.post(
        "/api/v1/usage",
        json={
            "subscription_id": 1,
            "usage_type": "Data",
            "usage_amount": -10
        }
    )

    assert response.status_code == 422


# =====================================================
# 7. CREATE USAGE - INVALID SUBSCRIPTION ID
# =====================================================

def test_create_usage_invalid_subscription_id():
    response = client.post(
        "/api/v1/usage",
        json={
            "subscription_id": "invalid",
            "usage_type": "Data",
            "usage_amount": 2.5
        }
    )

    assert response.status_code == 422


# =====================================================
# 8. CREATE USAGE - INVALID AMOUNT TYPE
# =====================================================

def test_create_usage_invalid_amount_type():
    response = client.post(
        "/api/v1/usage",
        json={
            "subscription_id": 1,
            "usage_type": "Data",
            "usage_amount": "invalid"
        }
    )

    assert response.status_code == 422


# =====================================================
# 9. CREATE USAGE - INVALID DATE
# =====================================================

def test_create_usage_invalid_date():
    response = client.post(
        "/api/v1/usage",
        json={
            "subscription_id": 1,
            "usage_type": "Data",
            "usage_amount": 2.5,
            "usage_date": "not-a-date"
        }
    )

    assert response.status_code == 422


# =====================================================
# 10. CREATE USAGE - EMPTY BODY
# =====================================================

def test_create_usage_empty_body():
    response = client.post(
        "/api/v1/usage",
        json={}
    )

    assert response.status_code == 422


# =====================================================
# 11. CUSTOMER USAGE
# =====================================================

def test_get_customer_usage():
    response = client.get(
        "/api/v1/usage/customer/1"
    )

    assert response.status_code in [200, 404]


# =====================================================
# 12. CUSTOMER USAGE - INVALID ID
# =====================================================

def test_get_customer_usage_invalid_id():
    response = client.get(
        "/api/v1/usage/customer/abc"
    )

    assert response.status_code == 422


# =====================================================
# 13. SIM USAGE
# =====================================================

def test_get_sim_usage():
    response = client.get(
        "/api/v1/usage/sim/1"
    )

    assert response.status_code in [200, 404]


# =====================================================
# 14. SIM USAGE - INVALID ID
# =====================================================

def test_get_sim_usage_invalid_id():
    response = client.get(
        "/api/v1/usage/sim/abc"
    )

    assert response.status_code == 422


# =====================================================
# 15. SUBSCRIPTION USAGE
# =====================================================

def test_get_subscription_usage():
    response = client.get(
        "/api/v1/usage/subscription/1"
    )

    assert response.status_code in [200, 404]


# =====================================================
# 16. SUBSCRIPTION USAGE - INVALID ID
# =====================================================

def test_get_subscription_usage_invalid_id():
    response = client.get(
        "/api/v1/usage/subscription/abc"
    )

    assert response.status_code == 422


# =====================================================
# 17. USAGE SUMMARY
# =====================================================

def test_get_usage_summary():
    response = client.get(
        "/api/v1/usage/subscription/1/summary"
    )

    assert response.status_code in [200, 404]


# =====================================================
# 18. USAGE SUMMARY - INVALID ID
# =====================================================

def test_get_usage_summary_invalid_id():
    response = client.get(
        "/api/v1/usage/subscription/abc/summary"
    )

    assert response.status_code == 422


# =====================================================
# 19. DAILY USAGE
# =====================================================

def test_get_daily_usage():
    response = client.get(
        "/api/v1/usage/subscription/1/daily",
        params={
            "usage_date": date.today().isoformat()
        }
    )

    assert response.status_code in [200, 400, 404]


# =====================================================
# 20. DAILY USAGE - MISSING DATE
# =====================================================

def test_get_daily_usage_missing_date():
    response = client.get(
        "/api/v1/usage/subscription/1/daily"
    )

    assert response.status_code == 422


# =====================================================
# 21. DAILY USAGE - INVALID DATE
# =====================================================

def test_get_daily_usage_invalid_date():
    response = client.get(
        "/api/v1/usage/subscription/1/daily",
        params={
            "usage_date": "invalid-date"
        }
    )

    assert response.status_code == 422


# =====================================================
# 22. DAILY USAGE - INVALID SUBSCRIPTION ID
# =====================================================

def test_get_daily_usage_invalid_subscription_id():
    response = client.get(
        "/api/v1/usage/subscription/abc/daily",
        params={
            "usage_date": date.today().isoformat()
        }
    )

    assert response.status_code == 422


# =====================================================
# 23. MONTHLY USAGE
# =====================================================

def test_get_monthly_usage():
    today = date.today()

    response = client.get(
        "/api/v1/usage/subscription/1/monthly",
        params={
            "year": today.year,
            "month": today.month
        }
    )

    assert response.status_code in [200, 400, 404]


# =====================================================
# 24. MONTHLY USAGE - MISSING YEAR
# =====================================================

def test_get_monthly_usage_missing_year():
    response = client.get(
        "/api/v1/usage/subscription/1/monthly",
        params={
            "month": 1
        }
    )

    assert response.status_code == 422


# =====================================================
# 25. MONTHLY USAGE - MISSING MONTH
# =====================================================

def test_get_monthly_usage_missing_month():
    response = client.get(
        "/api/v1/usage/subscription/1/monthly",
        params={
            "year": 2026
        }
    )

    assert response.status_code == 422


# =====================================================
# 26. MONTHLY USAGE - INVALID YEAR
# =====================================================

def test_get_monthly_usage_invalid_year():
    response = client.get(
        "/api/v1/usage/subscription/1/monthly",
        params={
            "year": "invalid",
            "month": 1
        }
    )

    assert response.status_code == 422


# =====================================================
# 27. MONTHLY USAGE - INVALID MONTH TYPE
# =====================================================

def test_get_monthly_usage_invalid_month_type():
    response = client.get(
        "/api/v1/usage/subscription/1/monthly",
        params={
            "year": 2026,
            "month": "invalid"
        }
    )

    assert response.status_code == 422


# =====================================================
# 28. MONTHLY USAGE - INVALID SUBSCRIPTION ID
# =====================================================

def test_get_monthly_usage_invalid_subscription_id():
    response = client.get(
        "/api/v1/usage/subscription/abc/monthly",
        params={
            "year": 2026,
            "month": 1
        }
    )

    assert response.status_code == 422


# =====================================================
# 29. CUSTOMER USAGE - NON-EXISTING CUSTOMER
# =====================================================

def test_customer_usage_non_existing_customer():
    response = client.get(
        "/api/v1/usage/customer/999999"
    )

    assert response.status_code in [200, 404]


# =====================================================
# 30. SIM USAGE - NON-EXISTING SIM
# =====================================================

def test_sim_usage_non_existing_sim():
    response = client.get(
        "/api/v1/usage/sim/999999"
    )

    assert response.status_code in [200, 404]


# =====================================================
# 31. SUBSCRIPTION USAGE - NON-EXISTING SUBSCRIPTION
# =====================================================

def test_subscription_usage_non_existing_subscription():
    response = client.get(
        "/api/v1/usage/subscription/999999"
    )

    assert response.status_code in [200, 404]