import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

from fastapi import HTTPException

from services.subscription_service import SubscriptionService


# ============================================================
# VALIDATE CUSTOMER
# ============================================================

@patch("services.subscription_service.CustomerRepository")
def test_validate_customer_success(
    mock_customer_repository
):
    db = MagicMock()

    fake_customer = MagicMock()
    fake_customer.id = 1
    fake_customer.is_active = True

    mock_customer_repository.get_by_id.return_value = (
        fake_customer
    )

    result = SubscriptionService.validate_customer(
        db=db,
        customer_id=1
    )

    assert result == fake_customer

    mock_customer_repository.get_by_id.assert_called_once_with(
        db,
        1
    )


@patch("services.subscription_service.CustomerRepository")
def test_validate_customer_not_found(
    mock_customer_repository
):
    db = MagicMock()

    mock_customer_repository.get_by_id.return_value = None

    with pytest.raises(HTTPException) as exc_info:

        SubscriptionService.validate_customer(
            db=db,
            customer_id=999
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Customer not found"


@patch("services.subscription_service.CustomerRepository")
def test_validate_customer_inactive(
    mock_customer_repository
):
    db = MagicMock()

    fake_customer = MagicMock()
    fake_customer.id = 1
    fake_customer.is_active = False

    mock_customer_repository.get_by_id.return_value = (
        fake_customer
    )

    with pytest.raises(HTTPException) as exc_info:

        SubscriptionService.validate_customer(
            db=db,
            customer_id=1
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == (
        "Customer account is inactive"
    )


# ============================================================
# VALIDATE SIM
# ============================================================

@patch("services.subscription_service.SIMCardRepository")
def test_validate_sim_success(
    mock_sim_repository
):
    db = MagicMock()

    fake_sim = MagicMock()
    fake_sim.id = 1
    fake_sim.customer_id = 10
    fake_sim.status = "Active"

    mock_sim_repository.get_by_id.return_value = fake_sim

    result = SubscriptionService.validate_sim(
        db=db,
        sim_id=1,
        customer_id=10
    )

    assert result == fake_sim

    mock_sim_repository.get_by_id.assert_called_once_with(
        db,
        1
    )


@patch("services.subscription_service.SIMCardRepository")
def test_validate_sim_not_found(
    mock_sim_repository
):
    db = MagicMock()

    mock_sim_repository.get_by_id.return_value = None

    with pytest.raises(HTTPException) as exc_info:

        SubscriptionService.validate_sim(
            db=db,
            sim_id=999,
            customer_id=10
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "SIM card not found"


@patch("services.subscription_service.SIMCardRepository")
def test_validate_sim_wrong_customer(
    mock_sim_repository
):
    db = MagicMock()

    fake_sim = MagicMock()
    fake_sim.customer_id = 20
    fake_sim.status = "Active"

    mock_sim_repository.get_by_id.return_value = fake_sim

    with pytest.raises(HTTPException) as exc_info:

        SubscriptionService.validate_sim(
            db=db,
            sim_id=1,
            customer_id=10
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == (
        "SIM does not belong to the customer"
    )


@patch("services.subscription_service.SIMCardRepository")
def test_validate_sim_inactive(
    mock_sim_repository
):
    db = MagicMock()

    fake_sim = MagicMock()
    fake_sim.customer_id = 10
    fake_sim.status = "Inactive"

    mock_sim_repository.get_by_id.return_value = fake_sim

    with pytest.raises(HTTPException) as exc_info:

        SubscriptionService.validate_sim(
            db=db,
            sim_id=1,
            customer_id=10
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == (
        "Only an Active SIM can have a subscription"
    )


# ============================================================
# VALIDATE PLAN
# ============================================================

@patch("services.subscription_service.ServicePlanRepository")
def test_validate_plan_success(
    mock_plan_repository
):
    db = MagicMock()

    fake_plan = MagicMock()
    fake_plan.id = 1
    fake_plan.is_active = True
    fake_plan.plan_name = "Basic Plan"
    fake_plan.price = 199.0
    fake_plan.validity_days = 28

    mock_plan_repository.get_by_id.return_value = fake_plan

    result = SubscriptionService.validate_plan(
        db=db,
        plan_id=1
    )

    assert result == fake_plan

    mock_plan_repository.get_by_id.assert_called_once_with(
        db,
        1
    )


@patch("services.subscription_service.ServicePlanRepository")
def test_validate_plan_not_found(
    mock_plan_repository
):
    db = MagicMock()

    mock_plan_repository.get_by_id.return_value = None

    with pytest.raises(HTTPException) as exc_info:

        SubscriptionService.validate_plan(
            db=db,
            plan_id=999
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Service plan not found"


@patch("services.subscription_service.ServicePlanRepository")
def test_validate_plan_inactive(
    mock_plan_repository
):
    db = MagicMock()

    fake_plan = MagicMock()
    fake_plan.id = 1
    fake_plan.is_active = False

    mock_plan_repository.get_by_id.return_value = fake_plan

    with pytest.raises(HTTPException) as exc_info:

        SubscriptionService.validate_plan(
            db=db,
            plan_id=1
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == (
        "Service plan is inactive"
    )


# ============================================================
# ADD HISTORY
# ============================================================

@patch("services.subscription_service.SubscriptionHistory")
def test_add_history(
    mock_history_model
):
    db = MagicMock()

    fake_history = MagicMock()

    mock_history_model.return_value = fake_history

    SubscriptionService.add_history(
        db=db,
        subscription_id=1,
        old_plan_id=10,
        new_plan_id=20,
        old_status="Active",
        new_status="Active",
        action="Plan Upgrade",
        description="Plan upgraded",
        changed_by=100
    )

    mock_history_model.assert_called_once_with(
        subscription_id=1,
        old_plan_id=10,
        new_plan_id=20,
        old_status="Active",
        new_status="Active",
        action="Plan Upgrade",
        description="Plan upgraded",
        changed_by=100
    )

    db.add.assert_called_once_with(
        fake_history
    )


# ============================================================
# CREATE SUBSCRIPTION - SUCCESS
# ============================================================

@patch("services.subscription_service.SubscriptionService.add_history")
@patch("services.subscription_service.SubscriptionRepository")
@patch("services.subscription_service.SubscriptionService.validate_plan")
@patch("services.subscription_service.SubscriptionService.validate_sim")
@patch("services.subscription_service.SubscriptionService.validate_customer")
def test_create_subscription_success(
    mock_validate_customer,
    mock_validate_sim,
    mock_validate_plan,
    mock_subscription_repository,
    mock_add_history
):
    db = MagicMock()

    fake_customer = MagicMock()
    fake_customer.id = 10

    fake_sim = MagicMock()
    fake_sim.id = 20

    fake_plan = MagicMock()
    fake_plan.id = 30
    fake_plan.plan_name = "Premium Plan"
    fake_plan.validity_days = 30

    mock_validate_customer.return_value = fake_customer
    mock_validate_sim.return_value = fake_sim
    mock_validate_plan.return_value = fake_plan

    mock_subscription_repository.get_active_by_sim.return_value = (
        None
    )

    subscription = MagicMock()
    subscription.id = 100

    db.flush.side_effect = lambda: setattr(
        subscription,
        "id",
        100
    )

    with patch(
        "services.subscription_service.Subscription",
        return_value=subscription
    ):

        result = SubscriptionService.create_subscription(
            db=db,
            customer_id=10,
            sim_id=20,
            plan_id=30,
            changed_by=500
        )

    assert result == subscription

    mock_validate_customer.assert_called_once_with(
        db,
        10
    )

    mock_validate_sim.assert_called_once_with(
        db,
        20,
        10
    )

    mock_validate_plan.assert_called_once_with(
        db,
        30
    )

    mock_subscription_repository.get_active_by_sim.assert_called_once_with(
        db,
        20
    )

    db.add.assert_called_once_with(
        subscription
    )

    db.flush.assert_called_once()
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(
        subscription
    )

    mock_add_history.assert_called_once()


# ============================================================
# CREATE SUBSCRIPTION - ACTIVE SUBSCRIPTION EXISTS
# ============================================================

@patch("services.subscription_service.SubscriptionRepository")
@patch("services.subscription_service.SubscriptionService.validate_plan")
@patch("services.subscription_service.SubscriptionService.validate_sim")
@patch("services.subscription_service.SubscriptionService.validate_customer")
def test_create_subscription_already_active(
    mock_validate_customer,
    mock_validate_sim,
    mock_validate_plan,
    mock_subscription_repository
):
    db = MagicMock()

    mock_validate_customer.return_value = MagicMock()
    mock_validate_sim.return_value = MagicMock()

    fake_plan = MagicMock()
    fake_plan.validity_days = 30

    mock_validate_plan.return_value = fake_plan

    existing_subscription = MagicMock()

    mock_subscription_repository.get_active_by_sim.return_value = (
        existing_subscription
    )

    with pytest.raises(HTTPException) as exc_info:

        SubscriptionService.create_subscription(
            db=db,
            customer_id=10,
            sim_id=20,
            plan_id=30,
            changed_by=500
        )

    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == (
        "SIM already has an active subscription"
    )

    db.commit.assert_not_called()


# ============================================================
# GET SUBSCRIPTION - SUCCESS
# ============================================================

@patch("services.subscription_service.SubscriptionRepository")
def test_get_subscription_success(
    mock_subscription_repository
):
    db = MagicMock()

    fake_subscription = MagicMock()
    fake_subscription.id = 1

    mock_subscription_repository.get_by_id.return_value = (
        fake_subscription
    )

    result = SubscriptionService.get_subscription(
        db=db,
        subscription_id=1
    )

    assert result == fake_subscription

    mock_subscription_repository.get_by_id.assert_called_once_with(
        db,
        1
    )


# ============================================================
# GET SUBSCRIPTION - NOT FOUND
# ============================================================

@patch("services.subscription_service.SubscriptionRepository")
def test_get_subscription_not_found(
    mock_subscription_repository
):
    db = MagicMock()

    mock_subscription_repository.get_by_id.return_value = None

    with pytest.raises(HTTPException) as exc_info:

        SubscriptionService.get_subscription(
            db=db,
            subscription_id=999
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == (
        "Subscription not found"
    )


# ============================================================
# UPGRADE PLAN - SUCCESS
# ============================================================

@patch("services.subscription_service.SubscriptionService.add_history")
@patch("services.subscription_service.SubscriptionService.validate_plan")
@patch("services.subscription_service.SubscriptionService.get_subscription")
def test_upgrade_plan_success(
    mock_get_subscription,
    mock_validate_plan,
    mock_add_history
):
    db = MagicMock()

    subscription = MagicMock()
    subscription.id = 1
    subscription.status = "Active"
    subscription.plan_id = 10

    old_plan = MagicMock()
    old_plan.id = 10
    old_plan.plan_name = "Basic"
    old_plan.price = 199.0

    new_plan = MagicMock()
    new_plan.id = 20
    new_plan.plan_name = "Premium"
    new_plan.price = 399.0

    mock_get_subscription.return_value = subscription

    mock_validate_plan.side_effect = [
        old_plan,
        new_plan
    ]

    result = SubscriptionService.upgrade_plan(
        db=db,
        subscription_id=1,
        new_plan_id=20,
        changed_by=100
    )

    assert result == subscription
    assert subscription.plan_id == 20

    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(
        subscription
    )

    mock_add_history.assert_called_once()


# ============================================================
# UPGRADE PLAN - INACTIVE SUBSCRIPTION
# ============================================================

@patch("services.subscription_service.SubscriptionService.get_subscription")
def test_upgrade_plan_inactive_subscription(
    mock_get_subscription
):
    db = MagicMock()

    subscription = MagicMock()
    subscription.status = "Suspended"

    mock_get_subscription.return_value = subscription

    with pytest.raises(HTTPException) as exc_info:

        SubscriptionService.upgrade_plan(
            db=db,
            subscription_id=1,
            new_plan_id=20,
            changed_by=100
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == (
        "Only an Active subscription can be upgraded"
    )


# ============================================================
# UPGRADE PLAN - SAME PLAN
# ============================================================

@patch("services.subscription_service.SubscriptionService.validate_plan")
@patch("services.subscription_service.SubscriptionService.get_subscription")
def test_upgrade_plan_same_plan(
    mock_get_subscription,
    mock_validate_plan
):
    db = MagicMock()

    subscription = MagicMock()
    subscription.status = "Active"
    subscription.plan_id = 10

    plan = MagicMock()
    plan.id = 10
    plan.price = 199.0

    mock_get_subscription.return_value = subscription

    mock_validate_plan.return_value = plan

    with pytest.raises(HTTPException) as exc_info:

        SubscriptionService.upgrade_plan(
            db=db,
            subscription_id=1,
            new_plan_id=10,
            changed_by=100
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == (
        "New plan is same as current plan"
    )


# ============================================================
# UPGRADE PLAN - NEW PLAN NOT MORE EXPENSIVE
# ============================================================

@patch("services.subscription_service.SubscriptionService.validate_plan")
@patch("services.subscription_service.SubscriptionService.get_subscription")
def test_upgrade_plan_lower_price(
    mock_get_subscription,
    mock_validate_plan
):
    db = MagicMock()

    subscription = MagicMock()
    subscription.status = "Active"
    subscription.plan_id = 10

    old_plan = MagicMock()
    old_plan.id = 10
    old_plan.price = 399.0

    new_plan = MagicMock()
    new_plan.id = 20
    new_plan.price = 199.0

    mock_get_subscription.return_value = subscription

    mock_validate_plan.side_effect = [
        old_plan,
        new_plan
    ]

    with pytest.raises(HTTPException) as exc_info:

        SubscriptionService.upgrade_plan(
            db=db,
            subscription_id=1,
            new_plan_id=20,
            changed_by=100
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == (
        "Upgrade plan must have a higher price "
        "than current plan"
    )


# ============================================================
# DOWNGRADE PLAN - SUCCESS
# ============================================================

@patch("services.subscription_service.SubscriptionService.add_history")
@patch("services.subscription_service.SubscriptionService.validate_plan")
@patch("services.subscription_service.SubscriptionService.get_subscription")
def test_downgrade_plan_success(
    mock_get_subscription,
    mock_validate_plan,
    mock_add_history
):
    db = MagicMock()

    subscription = MagicMock()
    subscription.id = 1
    subscription.status = "Active"
    subscription.plan_id = 20

    old_plan = MagicMock()
    old_plan.id = 20
    old_plan.plan_name = "Premium"
    old_plan.price = 399.0

    new_plan = MagicMock()
    new_plan.id = 10
    new_plan.plan_name = "Basic"
    new_plan.price = 199.0

    mock_get_subscription.return_value = subscription

    mock_validate_plan.side_effect = [
        old_plan,
        new_plan
    ]

    result = SubscriptionService.downgrade_plan(
        db=db,
        subscription_id=1,
        new_plan_id=10,
        changed_by=100
    )

    assert result == subscription
    assert subscription.plan_id == 10

    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(
        subscription
    )

    mock_add_history.assert_called_once()


# ============================================================
# DOWNGRADE PLAN - INACTIVE SUBSCRIPTION
# ============================================================

@patch("services.subscription_service.SubscriptionService.get_subscription")
def test_downgrade_plan_inactive(
    mock_get_subscription
):
    db = MagicMock()

    subscription = MagicMock()
    subscription.status = "Suspended"

    mock_get_subscription.return_value = subscription

    with pytest.raises(HTTPException) as exc_info:

        SubscriptionService.downgrade_plan(
            db=db,
            subscription_id=1,
            new_plan_id=10,
            changed_by=100
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == (
        "Only an Active subscription can be downgraded"
    )


# ============================================================
# DOWNGRADE PLAN - SAME PLAN
# ============================================================

@patch("services.subscription_service.SubscriptionService.validate_plan")
@patch("services.subscription_service.SubscriptionService.get_subscription")
def test_downgrade_plan_same_plan(
    mock_get_subscription,
    mock_validate_plan
):
    db = MagicMock()

    subscription = MagicMock()
    subscription.status = "Active"
    subscription.plan_id = 10

    plan = MagicMock()
    plan.id = 10
    plan.price = 199.0

    mock_get_subscription.return_value = subscription
    mock_validate_plan.return_value = plan

    with pytest.raises(HTTPException) as exc_info:

        SubscriptionService.downgrade_plan(
            db=db,
            subscription_id=1,
            new_plan_id=10,
            changed_by=100
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == (
        "New plan is same as current plan"
    )


# ============================================================
# DOWNGRADE PLAN - HIGHER PRICE
# ============================================================

@patch("services.subscription_service.SubscriptionService.validate_plan")
@patch("services.subscription_service.SubscriptionService.get_subscription")
def test_downgrade_plan_higher_price(
    mock_get_subscription,
    mock_validate_plan
):
    db = MagicMock()

    subscription = MagicMock()
    subscription.status = "Active"
    subscription.plan_id = 10

    old_plan = MagicMock()
    old_plan.id = 10
    old_plan.price = 199.0

    new_plan = MagicMock()
    new_plan.id = 20
    new_plan.price = 399.0

    mock_get_subscription.return_value = subscription

    mock_validate_plan.side_effect = [
        old_plan,
        new_plan
    ]

    with pytest.raises(HTTPException) as exc_info:

        SubscriptionService.downgrade_plan(
            db=db,
            subscription_id=1,
            new_plan_id=20,
            changed_by=100
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == (
        "Downgrade plan must have a lower price "
        "than current plan"
    )


# ============================================================
# RENEW SUBSCRIPTION - SUCCESS
# ============================================================

@patch("services.subscription_service.SubscriptionService.add_history")
@patch("services.subscription_service.SubscriptionService.validate_plan")
@patch("services.subscription_service.SubscriptionService.get_subscription")
def test_renew_subscription_success(
    mock_get_subscription,
    mock_validate_plan,
    mock_add_history
):
    db = MagicMock()

    old_end_date = (
        datetime.now(timezone.utc)
        + timedelta(days=5)
    )

    subscription = MagicMock()
    subscription.id = 1
    subscription.status = "Active"
    subscription.plan_id = 10
    subscription.end_date = old_end_date

    plan = MagicMock()
    plan.validity_days = 30

    mock_get_subscription.return_value = subscription
    mock_validate_plan.return_value = plan

    result = SubscriptionService.renew_subscription(
        db=db,
        subscription_id=1,
        changed_by=100
    )

    assert result == subscription

    assert subscription.end_date > old_end_date

    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(
        subscription
    )

    mock_add_history.assert_called_once()


# ============================================================
# RENEW SUBSCRIPTION - EXPIRED DATE
# ============================================================

@patch("services.subscription_service.SubscriptionService.add_history")
@patch("services.subscription_service.SubscriptionService.validate_plan")
@patch("services.subscription_service.SubscriptionService.get_subscription")
def test_renew_subscription_expired(
    mock_get_subscription,
    mock_validate_plan,
    mock_add_history
):
    db = MagicMock()

    old_end_date = (
        datetime.now(timezone.utc)
        - timedelta(days=5)
    )

    subscription = MagicMock()
    subscription.id = 1
    subscription.status = "Active"
    subscription.plan_id = 10
    subscription.end_date = old_end_date

    plan = MagicMock()
    plan.validity_days = 30

    mock_get_subscription.return_value = subscription
    mock_validate_plan.return_value = plan

    result = SubscriptionService.renew_subscription(
        db=db,
        subscription_id=1,
        changed_by=100
    )

    assert result == subscription

    assert subscription.end_date > old_end_date

    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(
        subscription
    )


# ============================================================
# RENEW SUBSCRIPTION - INACTIVE
# ============================================================

@patch("services.subscription_service.SubscriptionService.get_subscription")
def test_renew_subscription_inactive(
    mock_get_subscription
):
    db = MagicMock()

    subscription = MagicMock()
    subscription.status = "Suspended"

    mock_get_subscription.return_value = subscription

    with pytest.raises(HTTPException) as exc_info:

        SubscriptionService.renew_subscription(
            db=db,
            subscription_id=1,
            changed_by=100
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == (
        "Only an Active subscription can be renewed"
    )


# ============================================================
# SUSPEND SUBSCRIPTION - SUCCESS
# ============================================================

@patch("services.subscription_service.SubscriptionService.add_history")
@patch("services.subscription_service.SubscriptionService.get_subscription")
def test_suspend_subscription_success(
    mock_get_subscription,
    mock_add_history
):
    db = MagicMock()

    subscription = MagicMock()
    subscription.id = 1
    subscription.plan_id = 10
    subscription.status = "Active"

    mock_get_subscription.return_value = subscription

    result = SubscriptionService.suspend_subscription(
        db=db,
        subscription_id=1,
        changed_by=100
    )

    assert result == subscription
    assert subscription.status == "Suspended"

    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(
        subscription
    )

    mock_add_history.assert_called_once()


# ============================================================
# SUSPEND SUBSCRIPTION - NOT ACTIVE
# ============================================================

@patch("services.subscription_service.SubscriptionService.get_subscription")
def test_suspend_subscription_not_active(
    mock_get_subscription
):
    db = MagicMock()

    subscription = MagicMock()
    subscription.status = "Suspended"

    mock_get_subscription.return_value = subscription

    with pytest.raises(HTTPException) as exc_info:

        SubscriptionService.suspend_subscription(
            db=db,
            subscription_id=1,
            changed_by=100
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == (
        "Only an Active subscription can be suspended"
    )


# ============================================================
# REACTIVATE SUBSCRIPTION - SUCCESS
# ============================================================

@patch("services.subscription_service.SubscriptionService.add_history")
@patch("services.subscription_service.SubscriptionService.get_subscription")
def test_reactivate_subscription_success(
    mock_get_subscription,
    mock_add_history
):
    db = MagicMock()

    subscription = MagicMock()
    subscription.id = 1
    subscription.plan_id = 10
    subscription.status = "Suspended"

    mock_get_subscription.return_value = subscription

    result = SubscriptionService.reactivate_subscription(
        db=db,
        subscription_id=1,
        changed_by=100
    )

    assert result == subscription
    assert subscription.status == "Active"

    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(
        subscription
    )

    mock_add_history.assert_called_once()


# ============================================================
# REACTIVATE SUBSCRIPTION - NOT SUSPENDED
# ============================================================

@patch("services.subscription_service.SubscriptionService.get_subscription")
def test_reactivate_subscription_not_suspended(
    mock_get_subscription
):
    db = MagicMock()

    subscription = MagicMock()
    subscription.status = "Active"

    mock_get_subscription.return_value = subscription

    with pytest.raises(HTTPException) as exc_info:

        SubscriptionService.reactivate_subscription(
            db=db,
            subscription_id=1,
            changed_by=100
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == (
        "Only a Suspended subscription can be reactivated"
    )


# ============================================================
# CANCEL SUBSCRIPTION - SUCCESS
# ============================================================

@patch("services.subscription_service.SubscriptionService.add_history")
@patch("services.subscription_service.SubscriptionService.get_subscription")
def test_cancel_subscription_success(
    mock_get_subscription,
    mock_add_history
):
    db = MagicMock()

    subscription = MagicMock()
    subscription.id = 1
    subscription.plan_id = 10
    subscription.status = "Active"

    mock_get_subscription.return_value = subscription

    result = SubscriptionService.cancel_subscription(
        db=db,
        subscription_id=1,
        changed_by=100
    )

    assert result == subscription
    assert subscription.status == "Cancelled"

    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(
        subscription
    )

    mock_add_history.assert_called_once()


# ============================================================
# CANCEL SUBSCRIPTION - ALREADY CANCELLED
# ============================================================

@patch("services.subscription_service.SubscriptionService.get_subscription")
def test_cancel_subscription_already_cancelled(
    mock_get_subscription
):
    db = MagicMock()

    subscription = MagicMock()
    subscription.status = "Cancelled"

    mock_get_subscription.return_value = subscription

    with pytest.raises(HTTPException) as exc_info:

        SubscriptionService.cancel_subscription(
            db=db,
            subscription_id=1,
            changed_by=100
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == (
        "Subscription already cancelled"
    )


# ============================================================
# GET HISTORY - SUCCESS
# ============================================================

@patch("services.subscription_service.SubscriptionHistoryRepository")
@patch("services.subscription_service.SubscriptionService.get_subscription")
def test_get_history_success(
    mock_get_subscription,
    mock_history_repository
):
    db = MagicMock()

    subscription = MagicMock()
    subscription.id = 1

    fake_history = [
        MagicMock(),
        MagicMock()
    ]

    mock_get_subscription.return_value = subscription

    mock_history_repository.get_by_subscription.return_value = (
        fake_history
    )

    result = SubscriptionService.get_history(
        db=db,
        subscription_id=1
    )

    assert result == fake_history

    mock_get_subscription.assert_called_once_with(
        db,
        1
    )

    mock_history_repository.get_by_subscription.assert_called_once_with(
        db,
        1
    )


# ============================================================
# GET CUSTOMER SUBSCRIPTIONS - SUCCESS
# ============================================================

@patch("services.subscription_service.SubscriptionRepository")
@patch("services.subscription_service.SubscriptionService.validate_customer")
def test_get_customer_subscriptions_success(
    mock_validate_customer,
    mock_subscription_repository
):
    db = MagicMock()

    fake_customer = MagicMock()
    fake_customer.id = 10
    fake_customer.is_active = True

    fake_subscriptions = [
        MagicMock(),
        MagicMock()
    ]

    mock_validate_customer.return_value = fake_customer

    mock_subscription_repository.get_by_customer.return_value = (
        fake_subscriptions
    )

    result = SubscriptionService.get_customer_subscriptions(
        db=db,
        customer_id=10
    )

    assert result == fake_subscriptions

    mock_validate_customer.assert_called_once_with(
        db,
        10
    )

    mock_subscription_repository.get_by_customer.assert_called_once_with(
        db,
        10
    )


# ============================================================
# GET CUSTOMER SUBSCRIPTIONS - INACTIVE CUSTOMER
# ============================================================

@patch("services.subscription_service.SubscriptionService.validate_customer")
def test_get_customer_subscriptions_inactive_customer(
    mock_validate_customer
):
    db = MagicMock()

    mock_validate_customer.side_effect = HTTPException(
        status_code=400,
        detail="Customer account is inactive"
    )

    with pytest.raises(HTTPException) as exc_info:

        SubscriptionService.get_customer_subscriptions(
            db=db,
            customer_id=10
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == (
        "Customer account is inactive"
    )
