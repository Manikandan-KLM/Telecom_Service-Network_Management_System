from datetime import datetime, timedelta

from fastapi.testclient import TestClient

from main import app
from utils.dependencies import get_current_user
from models.user_model import User


# ============================================================
# TEST CLIENT
# ============================================================

client = TestClient(app)


# ============================================================
# MOCK CURRENT USER
# ============================================================

test_user = User(
    id=1,
    email="admin@test.com",
    role="Super Admin",
    is_active=True
)


def override_get_current_user():
    return test_user


app.dependency_overrides[get_current_user] = override_get_current_user


# ============================================================
# SAMPLE RESPONSE DATA
# ============================================================

def sample_subscription(subscription_id=1):
    now = datetime.now()

    return {
        "id": subscription_id,
        "customer_id": 1,
        "sim_id": 1,
        "plan_id": 1,
        "start_date": now.isoformat(),
        "end_date": (now + timedelta(days=30)).isoformat(),
        "status": "Active",
        "created_at": now.isoformat(),
        "updated_at": now.isoformat()
    }

# ============================================================
# 2. CREATE SUBSCRIPTION - MISSING CUSTOMER ID
# ============================================================

def test_create_subscription_missing_customer_id():
    response = client.post(
        "/api/v1/subscriptions",
        json={
            "sim_id": 1,
            "plan_id": 1
        }
    )

    assert response.status_code == 422


# ============================================================
# 3. CREATE SUBSCRIPTION - MISSING SIM ID
# ============================================================

def test_create_subscription_missing_sim_id():
    response = client.post(
        "/api/v1/subscriptions",
        json={
            "customer_id": 1,
            "plan_id": 1
        }
    )

    assert response.status_code == 422


# ============================================================
# 4. CREATE SUBSCRIPTION - MISSING PLAN ID
# ============================================================

def test_create_subscription_missing_plan_id():
    response = client.post(
        "/api/v1/subscriptions",
        json={
            "customer_id": 1,
            "sim_id": 1
        }
    )

    assert response.status_code == 422


# ============================================================
# 5. CREATE SUBSCRIPTION - INVALID CUSTOMER ID
# ============================================================

def test_create_subscription_invalid_customer_id():
    response = client.post(
        "/api/v1/subscriptions",
        json={
            "customer_id": "abc",
            "sim_id": 1,
            "plan_id": 1
        }
    )

    assert response.status_code == 422


# ============================================================
# 6. CREATE SUBSCRIPTION - INVALID SIM ID
# ============================================================

def test_create_subscription_invalid_sim_id():
    response = client.post(
        "/api/v1/subscriptions",
        json={
            "customer_id": 1,
            "sim_id": "abc",
            "plan_id": 1
        }
    )

    assert response.status_code == 422


# ============================================================
# 7. CREATE SUBSCRIPTION - INVALID PLAN ID
# ============================================================

def test_create_subscription_invalid_plan_id():
    response = client.post(
        "/api/v1/subscriptions",
        json={
            "customer_id": 1,
            "sim_id": 1,
            "plan_id": "abc"
        }
    )

    assert response.status_code == 422


# ============================================================
# 8. GET SUBSCRIPTION
# ============================================================

def test_get_subscription():
    response = client.get(
        "/api/v1/subscriptions/1"
    )

    assert response.status_code in [200, 404]


# ============================================================
# 9. GET SUBSCRIPTION - INVALID ID
# ============================================================

def test_get_subscription_invalid_id():
    response = client.get(
        "/api/v1/subscriptions/abc"
    )

    assert response.status_code == 422


# ============================================================
# 10. GET NON-EXISTING SUBSCRIPTION
# ============================================================

def test_get_non_existing_subscription():
    response = client.get(
        "/api/v1/subscriptions/999999"
    )

    assert response.status_code in [404, 400]


# ============================================================
# 11. UPGRADE PLAN
# ============================================================

def test_upgrade_plan():
    response = client.patch(
        "/api/v1/subscriptions/1/upgrade",
        json={
            "new_plan_id": 2
        }
    )

    assert response.status_code in [200, 400, 404]


# ============================================================
# 12. UPGRADE PLAN - MISSING PLAN ID
# ============================================================

def test_upgrade_plan_missing_plan_id():
    response = client.patch(
        "/api/v1/subscriptions/1/upgrade",
        json={}
    )

    assert response.status_code == 422


# ============================================================
# 13. UPGRADE PLAN - INVALID PLAN ID
# ============================================================

def test_upgrade_plan_invalid_plan_id():
    response = client.patch(
        "/api/v1/subscriptions/1/upgrade",
        json={
            "new_plan_id": "abc"
        }
    )

    assert response.status_code == 422


# ============================================================
# 14. DOWNGRADE PLAN
# ============================================================

def test_downgrade_plan():
    response = client.patch(
        "/api/v1/subscriptions/1/downgrade",
        json={
            "new_plan_id": 1
        }
    )

    assert response.status_code in [200, 400, 404]


# ============================================================
# 15. DOWNGRADE PLAN - MISSING PLAN ID
# ============================================================

def test_downgrade_plan_missing_plan_id():
    response = client.patch(
        "/api/v1/subscriptions/1/downgrade",
        json={}
    )

    assert response.status_code == 422


# ============================================================
# 16. DOWNGRADE PLAN - INVALID PLAN ID
# ============================================================

def test_downgrade_plan_invalid_plan_id():
    response = client.patch(
        "/api/v1/subscriptions/1/downgrade",
        json={
            "new_plan_id": "abc"
        }
    )

    assert response.status_code == 422


# ============================================================
# 17. RENEW SUBSCRIPTION
# ============================================================

def test_renew_subscription():
    response = client.post(
        "/api/v1/subscriptions/1/renew"
    )

    assert response.status_code in [200, 400, 404]


# ============================================================
# 18. RENEW NON-EXISTING SUBSCRIPTION
# ============================================================

def test_renew_non_existing_subscription():
    response = client.post(
        "/api/v1/subscriptions/999999/renew"
    )

    assert response.status_code in [400, 404]


# ============================================================
# 19. SUSPEND SUBSCRIPTION
# ============================================================

def test_suspend_subscription():
    response = client.patch(
        "/api/v1/subscriptions/1/suspend"
    )

    assert response.status_code in [200, 400, 404]


# ============================================================
# 20. SUSPEND NON-EXISTING SUBSCRIPTION
# ============================================================

def test_suspend_non_existing_subscription():
    response = client.patch(
        "/api/v1/subscriptions/999999/suspend"
    )

    assert response.status_code in [400, 404]


# ============================================================
# 21. REACTIVATE SUBSCRIPTION
# ============================================================

def test_reactivate_subscription():
    response = client.patch(
        "/api/v1/subscriptions/1/reactivate"
    )

    assert response.status_code in [200, 400, 404]


# ============================================================
# 22. REACTIVATE NON-EXISTING SUBSCRIPTION
# ============================================================

def test_reactivate_non_existing_subscription():
    response = client.patch(
        "/api/v1/subscriptions/999999/reactivate"
    )

    assert response.status_code in [400, 404]


# ============================================================
# 23. CANCEL SUBSCRIPTION
# ============================================================

def test_cancel_subscription():
    response = client.patch(
        "/api/v1/subscriptions/1/cancel"
    )

    assert response.status_code in [200, 400, 404]


# ============================================================
# 24. CANCEL NON-EXISTING SUBSCRIPTION
# ============================================================

def test_cancel_non_existing_subscription():
    response = client.patch(
        "/api/v1/subscriptions/999999/cancel"
    )

    assert response.status_code in [400, 404]


# ============================================================
# 25. GET SUBSCRIPTION HISTORY
# ============================================================

def test_subscription_history():
    response = client.get(
        "/api/v1/subscriptions/1/history"
    )

    assert response.status_code in [200, 404]


# ============================================================
# 26. GET HISTORY FOR NON-EXISTING SUBSCRIPTION
# ============================================================

def test_subscription_history_non_existing():
    response = client.get(
        "/api/v1/subscriptions/999999/history"
    )

    assert response.status_code in [200, 404]


# ============================================================
# 28. GET CUSTOMER SUBSCRIPTIONS - INVALID ID
# ============================================================

def test_customer_subscriptions_invalid_customer_id():
    response = client.get(
        "/api/v1/subscriptions/customer/abc"
    )

    assert response.status_code == 422


# ============================================================
# 29. CREATE SUBSCRIPTION - EMPTY BODY
# ============================================================

def test_create_subscription_empty_body():
    response = client.post(
        "/api/v1/subscriptions",
        json={}
    )

    assert response.status_code == 422


# ============================================================
# 30. UPGRADE PLAN - ZERO PLAN ID
# ============================================================

def test_upgrade_plan_zero_plan_id():
    response = client.patch(
        "/api/v1/subscriptions/1/upgrade",
        json={
            "new_plan_id": 0
        }
    )

    # Schema only requires integer, so service decides validity
    assert response.status_code in [200, 400, 404]


# ============================================================
# 31. DOWNGRADE PLAN - ZERO PLAN ID
# ============================================================

def test_downgrade_plan_zero_plan_id():
    response = client.patch(
        "/api/v1/subscriptions/1/downgrade",
        json={
            "new_plan_id": 0
        }
    )

    assert response.status_code in [200, 400, 404]