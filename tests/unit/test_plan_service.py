import pytest
from unittest.mock import MagicMock, patch

from fastapi import HTTPException

from services.service_plan_service import ServicePlanService


# ============================================================
# VALIDATE PLAN TYPE
# ============================================================

@pytest.mark.parametrize(
    "plan_type",
    [
        "Prepaid",
        "Postpaid",
        "Data",
        "Voice",
        "SMS",
    ]
)
def test_validate_plan_type_success(plan_type):
    result = ServicePlanService.validate_plan_type(
        plan_type
    )

    assert result is None


def test_validate_plan_type_invalid():
    with pytest.raises(HTTPException) as exc_info:

        ServicePlanService.validate_plan_type(
            "Invalid"
        )

    assert exc_info.value.status_code == 400

    assert (
        exc_info.value.detail
        == (
            "Invalid plan type. "
            "Allowed values: "
            "Prepaid, Postpaid, Data, Voice, SMS"
        )
    )


# ============================================================
# CREATE PLAN - SUCCESS
# ============================================================

@patch("services.service_plan_service.ServicePlanRepository")
def test_create_plan_success(
    mock_plan_repository
):
    db = MagicMock()

    mock_plan_repository.get_by_code.return_value = None

    fake_plan = MagicMock()
    fake_plan.id = 1

    mock_plan_repository.create.return_value = fake_plan

    result = ServicePlanService.create_plan(
        db=db,
        plan_code="basic001",
        plan_name="Basic Plan",
        plan_type="Prepaid",
        data_limit=10.0,
        voice_limit=100,
        sms_limit=100,
        validity_days=28,
        price=199.0,
        description="Basic prepaid plan"
    )

    assert result == fake_plan

    mock_plan_repository.get_by_code.assert_called_once_with(
        db,
        "basic001"
    )

    mock_plan_repository.create.assert_called_once()

    plan_object = (
        mock_plan_repository.create.call_args.args[1]
    )

    assert plan_object.plan_code == "BASIC001"
    assert plan_object.plan_name == "Basic Plan"
    assert plan_object.plan_type == "Prepaid"
    assert plan_object.data_limit == 10.0
    assert plan_object.voice_limit == 100
    assert plan_object.sms_limit == 100
    assert plan_object.validity_days == 28
    assert plan_object.price == 199.0
    assert plan_object.description == "Basic prepaid plan"
    assert plan_object.is_active is True


# ============================================================
# CREATE PLAN - INVALID PLAN TYPE
# ============================================================

@patch("services.service_plan_service.ServicePlanRepository")
def test_create_plan_invalid_plan_type(
    mock_plan_repository
):
    db = MagicMock()

    with pytest.raises(HTTPException) as exc_info:

        ServicePlanService.create_plan(
            db=db,
            plan_code="basic001",
            plan_name="Basic Plan",
            plan_type="Invalid",
            data_limit=10.0,
            voice_limit=100,
            sms_limit=100,
            validity_days=28,
            price=199.0,
            description="Basic plan"
        )

    assert exc_info.value.status_code == 400

    assert (
        exc_info.value.detail
        == (
            "Invalid plan type. "
            "Allowed values: "
            "Prepaid, Postpaid, Data, Voice, SMS"
        )
    )

    mock_plan_repository.get_by_code.assert_not_called()

    mock_plan_repository.create.assert_not_called()


# ============================================================
# CREATE PLAN - DUPLICATE PLAN CODE
# ============================================================

@patch("services.service_plan_service.ServicePlanRepository")
def test_create_plan_duplicate_code(
    mock_plan_repository
):
    db = MagicMock()

    existing_plan = MagicMock()

    mock_plan_repository.get_by_code.return_value = (
        existing_plan
    )

    with pytest.raises(HTTPException) as exc_info:

        ServicePlanService.create_plan(
            db=db,
            plan_code="BASIC001",
            plan_name="Basic Plan",
            plan_type="Prepaid",
            data_limit=10.0,
            voice_limit=100,
            sms_limit=100,
            validity_days=28,
            price=199.0,
            description="Basic plan"
        )

    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == "Plan code already exists"

    mock_plan_repository.create.assert_not_called()


# ============================================================
# GET PLAN - SUCCESS
# ============================================================

@patch("services.service_plan_service.ServicePlanRepository")
def test_get_plan_success(
    mock_plan_repository
):
    db = MagicMock()

    fake_plan = MagicMock()
    fake_plan.id = 1

    mock_plan_repository.get_by_id.return_value = (
        fake_plan
    )

    result = ServicePlanService.get_plan(
        db=db,
        plan_id=1
    )

    assert result == fake_plan

    mock_plan_repository.get_by_id.assert_called_once_with(
        db,
        1
    )


# ============================================================
# GET PLAN - NOT FOUND
# ============================================================

@patch("services.service_plan_service.ServicePlanRepository")
def test_get_plan_not_found(
    mock_plan_repository
):
    db = MagicMock()

    mock_plan_repository.get_by_id.return_value = None

    with pytest.raises(HTTPException) as exc_info:

        ServicePlanService.get_plan(
            db=db,
            plan_id=999
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Service plan not found"


# ============================================================
# UPDATE PLAN - ALL FIELDS
# ============================================================

@patch("services.service_plan_service.ServicePlanRepository")
def test_update_plan_success(
    mock_plan_repository
):
    db = MagicMock()

    fake_plan = MagicMock()

    fake_plan.id = 1
    fake_plan.plan_name = "Old Plan"
    fake_plan.data_limit = 5.0
    fake_plan.voice_limit = 50
    fake_plan.sms_limit = 50
    fake_plan.validity_days = 20
    fake_plan.price = 99.0
    fake_plan.description = "Old description"

    mock_plan_repository.get_by_id.return_value = (
        fake_plan
    )

    mock_plan_repository.update.return_value = (
        fake_plan
    )

    result = ServicePlanService.update_plan(
        db=db,
        plan_id=1,
        plan_name="New Plan",
        data_limit=20.0,
        voice_limit=200,
        sms_limit=200,
        validity_days=56,
        price=299.0,
        description="Updated plan"
    )

    assert result == fake_plan

    assert fake_plan.plan_name == "New Plan"
    assert fake_plan.data_limit == 20.0
    assert fake_plan.voice_limit == 200
    assert fake_plan.sms_limit == 200
    assert fake_plan.validity_days == 56
    assert fake_plan.price == 299.0
    assert fake_plan.description == "Updated plan"

    mock_plan_repository.update.assert_called_once_with(
        db,
        fake_plan
    )


# ============================================================
# UPDATE PLAN - PARTIAL UPDATE
# ============================================================

@patch("services.service_plan_service.ServicePlanRepository")
def test_update_plan_partial_update(
    mock_plan_repository
):
    db = MagicMock()

    fake_plan = MagicMock()

    fake_plan.id = 1
    fake_plan.plan_name = "Old Plan"
    fake_plan.data_limit = 10.0
    fake_plan.voice_limit = 100
    fake_plan.sms_limit = 100
    fake_plan.validity_days = 28
    fake_plan.price = 199.0
    fake_plan.description = "Old description"

    mock_plan_repository.get_by_id.return_value = (
        fake_plan
    )

    mock_plan_repository.update.return_value = (
        fake_plan
    )

    result = ServicePlanService.update_plan(
        db=db,
        plan_id=1,
        plan_name="Updated Plan",
        data_limit=None,
        voice_limit=None,
        sms_limit=None,
        validity_days=None,
        price=None,
        description=None
    )

    assert result == fake_plan

    assert fake_plan.plan_name == "Updated Plan"

    mock_plan_repository.update.assert_called_once_with(
        db,
        fake_plan
    )


# ============================================================
# UPDATE PLAN - NOT FOUND
# ============================================================

@patch("services.service_plan_service.ServicePlanRepository")
def test_update_plan_not_found(
    mock_plan_repository
):
    db = MagicMock()

    mock_plan_repository.get_by_id.return_value = None

    with pytest.raises(HTTPException) as exc_info:

        ServicePlanService.update_plan(
            db=db,
            plan_id=999,
            plan_name="Updated Plan",
            data_limit=None,
            voice_limit=None,
            sms_limit=None,
            validity_days=None,
            price=None,
            description=None
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Service plan not found"

    mock_plan_repository.update.assert_not_called()


# ============================================================
# UPDATE STATUS - ACTIVATE
# ============================================================

@patch("services.service_plan_service.ServicePlanRepository")
def test_update_status_activate(
    mock_plan_repository
):
    db = MagicMock()

    fake_plan = MagicMock()
    fake_plan.id = 1
    fake_plan.is_active = False

    mock_plan_repository.get_by_id.return_value = (
        fake_plan
    )

    mock_plan_repository.update.return_value = (
        fake_plan
    )

    result = ServicePlanService.update_status(
        db=db,
        plan_id=1,
        is_active=True
    )

    assert result == fake_plan
    assert fake_plan.is_active is True

    mock_plan_repository.update.assert_called_once_with(
        db,
        fake_plan
    )


# ============================================================
# UPDATE STATUS - DEACTIVATE
# ============================================================

@patch("services.service_plan_service.ServicePlanRepository")
def test_update_status_deactivate(
    mock_plan_repository
):
    db = MagicMock()

    fake_plan = MagicMock()
    fake_plan.id = 1
    fake_plan.is_active = True

    mock_plan_repository.get_by_id.return_value = (
        fake_plan
    )

    mock_plan_repository.update.return_value = (
        fake_plan
    )

    result = ServicePlanService.update_status(
        db=db,
        plan_id=1,
        is_active=False
    )

    assert result == fake_plan
    assert fake_plan.is_active is False

    mock_plan_repository.update.assert_called_once_with(
        db,
        fake_plan
    )


# ============================================================
# UPDATE STATUS - NOT FOUND
# ============================================================

@patch("services.service_plan_service.ServicePlanRepository")
def test_update_status_not_found(
    mock_plan_repository
):
    db = MagicMock()

    mock_plan_repository.get_by_id.return_value = None

    with pytest.raises(HTTPException) as exc_info:

        ServicePlanService.update_status(
            db=db,
            plan_id=999,
            is_active=True
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Service plan not found"

    mock_plan_repository.update.assert_not_called()


# ============================================================
# SEARCH PLANS - SUCCESS
# ============================================================

@patch("services.service_plan_service.ServicePlanRepository")
def test_search_plans_success(
    mock_plan_repository
):
    db = MagicMock()

    fake_plans = [
        MagicMock(),
        MagicMock()
    ]

    mock_plan_repository.search.return_value = (
        fake_plans
    )

    result = ServicePlanService.search_plans(
        db=db,
        search="basic",
        plan_type="Prepaid",
        is_active=True,
        min_price=100.0,
        max_price=500.0,
        min_validity=28
    )

    assert result == fake_plans

    mock_plan_repository.search.assert_called_once_with(
        db=db,
        search="basic",
        plan_type="Prepaid",
        is_active=True,
        min_price=100.0,
        max_price=500.0,
        min_validity=28
    )


# ============================================================
# SEARCH PLANS - NO FILTERS
# ============================================================

@patch("services.service_plan_service.ServicePlanRepository")
def test_search_plans_without_filters(
    mock_plan_repository
):
    db = MagicMock()

    fake_plans = [
        MagicMock()
    ]

    mock_plan_repository.search.return_value = (
        fake_plans
    )

    result = ServicePlanService.search_plans(
        db=db
    )

    assert result == fake_plans

    mock_plan_repository.search.assert_called_once_with(
        db=db,
        search=None,
        plan_type=None,
        is_active=None,
        min_price=None,
        max_price=None,
        min_validity=None
    )


# ============================================================
# SEARCH PLANS - INVALID PLAN TYPE
# ============================================================

@patch("services.service_plan_service.ServicePlanRepository")
def test_search_plans_invalid_plan_type(
    mock_plan_repository
):
    db = MagicMock()

    with pytest.raises(HTTPException) as exc_info:

        ServicePlanService.search_plans(
            db=db,
            plan_type="Invalid"
        )

    assert exc_info.value.status_code == 400

    assert (
        exc_info.value.detail
        == (
            "Invalid plan type. "
            "Allowed values: "
            "Prepaid, Postpaid, Data, Voice, SMS"
        )
    )

    mock_plan_repository.search.assert_not_called()


# ============================================================
# COMPARE PLANS - SUCCESS
# ============================================================

@patch("services.service_plan_service.ServicePlanRepository")
def test_compare_plans_success(
    mock_plan_repository
):
    db = MagicMock()

    fake_plans = [
        MagicMock(id=1),
        MagicMock(id=2),
        MagicMock(id=3)
    ]

    mock_plan_repository.get_multiple_by_ids.return_value = (
        fake_plans
    )

    result = ServicePlanService.compare_plans(
        db=db,
        plan_ids=[1, 2, 3]
    )

    assert result == fake_plans

    mock_plan_repository.get_multiple_by_ids.assert_called_once_with(
        db,
        [1, 2, 3]
    )


# ============================================================
# COMPARE PLANS - LESS THAN 2
# ============================================================

def test_compare_plans_less_than_two():
    db = MagicMock()

    with pytest.raises(HTTPException) as exc_info:

        ServicePlanService.compare_plans(
            db=db,
            plan_ids=[1]
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == (
        "At least 2 plans are required"
    )


# ============================================================
# COMPARE PLANS - MORE THAN 5
# ============================================================

def test_compare_plans_more_than_five():
    db = MagicMock()

    with pytest.raises(HTTPException) as exc_info:

        ServicePlanService.compare_plans(
            db=db,
            plan_ids=[1, 2, 3, 4, 5, 6]
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == (
        "You can compare maximum 5 plans"
    )


# ============================================================
# COMPARE PLANS - PLAN NOT FOUND
# ============================================================

@patch("services.service_plan_service.ServicePlanRepository")
def test_compare_plans_plan_not_found(
    mock_plan_repository
):
    db = MagicMock()

    fake_plans = [
        MagicMock(id=1)
    ]

    mock_plan_repository.get_multiple_by_ids.return_value = (
        fake_plans
    )

    with pytest.raises(HTTPException) as exc_info:

        ServicePlanService.compare_plans(
            db=db,
            plan_ids=[1, 2]
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == (
        "One or more plans not found"
    )
