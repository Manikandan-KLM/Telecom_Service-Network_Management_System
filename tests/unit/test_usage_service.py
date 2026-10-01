import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone, date

from fastapi import HTTPException

from services.usage_service import UsageService


# ============================================================
# Helper Functions
# ============================================================

def create_subscription(
    subscription_id=1,
    customer_id=10,
    sim_id=20,
    plan_id=30,
    status="Active",
    start_date=None,
    end_date=None
):
    subscription = MagicMock()

    subscription.id = subscription_id
    subscription.customer_id = customer_id
    subscription.sim_id = sim_id
    subscription.plan_id = plan_id
    subscription.status = status

    subscription.start_date = (
        start_date
        or datetime(2026, 1, 1, tzinfo=timezone.utc)
    )

    subscription.end_date = (
        end_date
        or datetime(2026, 12, 31, tzinfo=timezone.utc)
    )

    return subscription


def create_plan(
    plan_id=30,
    data_limit=100.0,
    voice_limit=500.0,
    sms_limit=1000.0
):
    plan = MagicMock()

    plan.id = plan_id
    plan.data_limit = data_limit
    plan.voice_limit = voice_limit
    plan.sms_limit = sms_limit

    return plan


# ============================================================
# get_subscription()
# ============================================================

def test_get_subscription_success():

    db = MagicMock()

    subscription = create_subscription()

    with patch(
        "services.usage_service.SubscriptionRepository.get_by_id",
        return_value=subscription
    ) as mock_get:

        result = UsageService.get_subscription(
            db,
            1
        )

    assert result == subscription

    mock_get.assert_called_once_with(
        db,
        1
    )


def test_get_subscription_not_found():

    db = MagicMock()

    with patch(
        "services.usage_service.SubscriptionRepository.get_by_id",
        return_value=None
    ):

        with pytest.raises(HTTPException) as exc:

            UsageService.get_subscription(
                db,
                999
            )

    assert exc.value.status_code == 404
    assert exc.value.detail == "Subscription not found"


# ============================================================
# get_plan()
# ============================================================

def test_get_plan_success():

    db = MagicMock()

    plan = create_plan()

    with patch(
        "services.usage_service.ServicePlanRepository.get_by_id",
        return_value=plan
    ) as mock_get:

        result = UsageService.get_plan(
            db,
            30
        )

    assert result == plan

    mock_get.assert_called_once_with(
        db,
        30
    )


def test_get_plan_not_found():

    db = MagicMock()

    with patch(
        "services.usage_service.ServicePlanRepository.get_by_id",
        return_value=None
    ):

        with pytest.raises(HTTPException) as exc:

            UsageService.get_plan(
                db,
                999
            )

    assert exc.value.status_code == 404
    assert exc.value.detail == "Service plan not found"


# ============================================================
# validate_usage_type()
# ============================================================

@pytest.mark.parametrize(
    "usage_type",
    [
        "Data",
        "Voice",
        "SMS"
    ]
)
def test_validate_usage_type_success(usage_type):

    result = UsageService.validate_usage_type(
        usage_type
    )

    assert result is None


def test_validate_usage_type_invalid():

    with pytest.raises(HTTPException) as exc:

        UsageService.validate_usage_type(
            "Invalid"
        )

    assert exc.value.status_code == 400

    assert (
        exc.value.detail
        == "Invalid usage type. Allowed values: Data, Voice, SMS"
    )


# ============================================================
# validate_usage_amount()
# ============================================================

@pytest.mark.parametrize(
    "usage_type, usage_amount",
    [
        ("Data", 10),
        ("Voice", 20),
        ("SMS", 30)
    ]
)
def test_validate_usage_amount_success(
    usage_type,
    usage_amount
):

    plan = create_plan()

    result = UsageService.validate_usage_amount(
        usage_type,
        usage_amount,
        plan
    )

    assert result is None


def test_validate_usage_amount_zero():

    plan = create_plan()

    with pytest.raises(HTTPException) as exc:

        UsageService.validate_usage_amount(
            "Data",
            0,
            plan
        )

    assert exc.value.status_code == 400
    assert exc.value.detail == "Usage amount must be greater than zero"


def test_validate_usage_amount_negative():

    plan = create_plan()

    with pytest.raises(HTTPException) as exc:

        UsageService.validate_usage_amount(
            "Data",
            -10,
            plan
        )

    assert exc.value.status_code == 400
    assert exc.value.detail == "Usage amount must be greater than zero"


def test_validate_data_quota_not_available():

    plan = create_plan(
        data_limit=0
    )

    with pytest.raises(HTTPException) as exc:

        UsageService.validate_usage_amount(
            "Data",
            10,
            plan
        )

    assert exc.value.status_code == 400

    assert (
        exc.value.detail
        == "Data quota is not available in this plan"
    )


def test_validate_voice_quota_not_available():

    plan = create_plan(
        voice_limit=0
    )

    with pytest.raises(HTTPException) as exc:

        UsageService.validate_usage_amount(
            "Voice",
            10,
            plan
        )

    assert exc.value.status_code == 400

    assert (
        exc.value.detail
        == "Voice quota is not available in this plan"
    )


def test_validate_sms_quota_not_available():

    plan = create_plan(
        sms_limit=0
    )

    with pytest.raises(HTTPException) as exc:

        UsageService.validate_usage_amount(
            "SMS",
            10,
            plan
        )

    assert exc.value.status_code == 400

    assert (
        exc.value.detail
        == "SMS quota is not available in this plan"
    )


# ============================================================
# create_usage()
# ============================================================

def test_create_usage_success():

    db = MagicMock()

    subscription = create_subscription()

    plan = create_plan()

    usage_date = datetime(
        2026,
        5,
        10,
        tzinfo=timezone.utc
    )

    created_usage = MagicMock()

    with patch(
        "services.usage_service.UsageService.get_subscription",
        return_value=subscription
    ), patch(
        "services.usage_service.UsageService.get_plan",
        return_value=plan
    ), patch(
        "services.usage_service.UsageRepository.create",
        return_value=created_usage
    ) as mock_create:

        result = UsageService.create_usage(
            db=db,
            subscription_id=1,
            usage_type="Data",
            usage_amount=25.0,
            usage_date=usage_date
        )

    assert result == created_usage

    mock_create.assert_called_once()

    usage_object = mock_create.call_args.args[1]

    assert usage_object.customer_id == 10
    assert usage_object.sim_id == 20
    assert usage_object.subscription_id == 1
    assert usage_object.usage_type == "Data"
    assert usage_object.usage_amount == 25.0
    assert usage_object.usage_date == usage_date


def test_create_usage_inactive_subscription():

    db = MagicMock()

    subscription = create_subscription(
        status="Suspended"
    )

    with patch(
        "services.usage_service.UsageService.get_subscription",
        return_value=subscription
    ):

        with pytest.raises(HTTPException) as exc:

            UsageService.create_usage(
                db=db,
                subscription_id=1,
                usage_type="Data",
                usage_amount=10,
                usage_date=None
            )

    assert exc.value.status_code == 400

    assert (
        exc.value.detail
        == "Usage can only be recorded for an Active subscription"
    )


def test_create_usage_usage_date_before_start():

    db = MagicMock()

    subscription = create_subscription()

    plan = create_plan()

    usage_date = datetime(
        2025,
        12,
        31,
        tzinfo=timezone.utc
    )

    with patch(
        "services.usage_service.UsageService.get_subscription",
        return_value=subscription
    ), patch(
        "services.usage_service.UsageService.get_plan",
        return_value=plan
    ):

        with pytest.raises(HTTPException) as exc:

            UsageService.create_usage(
                db=db,
                subscription_id=1,
                usage_type="Data",
                usage_amount=10,
                usage_date=usage_date
            )

    assert exc.value.status_code == 400

    assert (
        exc.value.detail
        == "Usage date cannot be before subscription start date"
    )


def test_create_usage_usage_date_after_end():

    db = MagicMock()

    subscription = create_subscription()

    plan = create_plan()

    usage_date = datetime(
        2027,
        1,
        1,
        tzinfo=timezone.utc
    )

    with patch(
        "services.usage_service.UsageService.get_subscription",
        return_value=subscription
    ), patch(
        "services.usage_service.UsageService.get_plan",
        return_value=plan
    ):

        with pytest.raises(HTTPException) as exc:

            UsageService.create_usage(
                db=db,
                subscription_id=1,
                usage_type="Data",
                usage_amount=10,
                usage_date=usage_date
            )

    assert exc.value.status_code == 400

    assert (
        exc.value.detail
        == "Usage date cannot be after subscription end date"
    )


def test_create_usage_invalid_usage_type():

    db = MagicMock()

    subscription = create_subscription()

    plan = create_plan()

    usage_date = datetime(
        2026,
        5,
        10,
        tzinfo=timezone.utc
    )

    with patch(
        "services.usage_service.UsageService.get_subscription",
        return_value=subscription
    ), patch(
        "services.usage_service.UsageService.get_plan",
        return_value=plan
    ):

        with pytest.raises(HTTPException) as exc:

            UsageService.create_usage(
                db=db,
                subscription_id=1,
                usage_type="Internet",
                usage_amount=10,
                usage_date=usage_date
            )

    assert exc.value.status_code == 400

    assert (
        exc.value.detail
        == "Invalid usage type. Allowed values: Data, Voice, SMS"
    )


# ============================================================
# get_subscription_usage()
# ============================================================

def test_get_subscription_usage_success():

    db = MagicMock()

    subscription = create_subscription()

    usage_records = [
        MagicMock(),
        MagicMock()
    ]

    with patch(
        "services.usage_service.UsageService.get_subscription",
        return_value=subscription
    ), patch(
        "services.usage_service.UsageRepository.get_by_subscription",
        return_value=usage_records
    ) as mock_get:

        result = UsageService.get_subscription_usage(
            db,
            1
        )

    assert result == usage_records

    mock_get.assert_called_once_with(
        db,
        1
    )


def test_get_subscription_usage_subscription_not_found():

    db = MagicMock()

    with patch(
        "services.usage_service.UsageService.get_subscription",
        side_effect=HTTPException(
            status_code=404,
            detail="Subscription not found"
        )
    ):

        with pytest.raises(HTTPException) as exc:

            UsageService.get_subscription_usage(
                db,
                999
            )

    assert exc.value.status_code == 404
    assert exc.value.detail == "Subscription not found"


# ============================================================
# get_sim_usage()
# ============================================================

def test_get_sim_usage_success():

    db = MagicMock()

    usage_records = [
        MagicMock(),
        MagicMock()
    ]

    with patch(
        "services.usage_service.UsageRepository.get_by_sim",
        return_value=usage_records
    ) as mock_get:

        result = UsageService.get_sim_usage(
            db,
            20
        )

    assert result == usage_records

    mock_get.assert_called_once_with(
        db,
        20
    )


# ============================================================
# get_customer_usage()
# ============================================================

def test_get_customer_usage_success():

    db = MagicMock()

    usage_records = [
        MagicMock(),
        MagicMock()
    ]

    with patch(
        "services.usage_service.UsageRepository.get_by_customer",
        return_value=usage_records
    ) as mock_get:

        result = UsageService.get_customer_usage(
            db,
            10
        )

    assert result == usage_records

    mock_get.assert_called_once_with(
        db,
        10
    )


# ============================================================
# get_usage_summary()
# ============================================================

def test_get_usage_summary_success():

    db = MagicMock()

    subscription = create_subscription()

    plan = create_plan(
        data_limit=100,
        voice_limit=500,
        sms_limit=1000
    )

    usage1 = MagicMock()
    usage1.usage_type = "Data"
    usage1.usage_amount = 25

    usage2 = MagicMock()
    usage2.usage_type = "Voice"
    usage2.usage_amount = 100

    usage3 = MagicMock()
    usage3.usage_type = "SMS"
    usage3.usage_amount = 200

    usage_records = [
        usage1,
        usage2,
        usage3
    ]

    with patch(
        "services.usage_service.UsageService.get_subscription",
        return_value=subscription
    ), patch(
        "services.usage_service.UsageService.get_plan",
        return_value=plan
    ), patch(
        "services.usage_service.UsageRepository.get_by_subscription",
        return_value=usage_records
    ):

        result = UsageService.get_usage_summary(
            db,
            1
        )

    assert result["customer_id"] == 10
    assert result["sim_id"] == 20
    assert result["subscription_id"] == 1

    assert result["data_used"] == 25
    assert result["voice_used"] == 100
    assert result["sms_used"] == 200

    assert result["data_quota"] == 100
    assert result["voice_quota"] == 500
    assert result["sms_quota"] == 1000

    assert result["data_percentage"] == 25.0
    assert result["voice_percentage"] == 20.0
    assert result["sms_percentage"] == 20.0

    assert result["data_remaining"] == 75
    assert result["voice_remaining"] == 400
    assert result["sms_remaining"] == 800


def test_get_usage_summary_quota_exceeded():

    db = MagicMock()

    subscription = create_subscription()

    plan = create_plan(
        data_limit=100,
        voice_limit=100,
        sms_limit=100
    )

    usage = MagicMock()

    usage.usage_type = "Data"
    usage.usage_amount = 150

    with patch(
        "services.usage_service.UsageService.get_subscription",
        return_value=subscription
    ), patch(
        "services.usage_service.UsageService.get_plan",
        return_value=plan
    ), patch(
        "services.usage_service.UsageRepository.get_by_subscription",
        return_value=[usage]
    ):

        result = UsageService.get_usage_summary(
            db,
            1
        )

    assert result["data_used"] == 150
    assert result["data_remaining"] == 0
    assert result["data_percentage"] == 150.0


def test_get_usage_summary_zero_quota():

    db = MagicMock()

    subscription = create_subscription()

    plan = create_plan(
        data_limit=0,
        voice_limit=0,
        sms_limit=0
    )

    with patch(
        "services.usage_service.UsageService.get_subscription",
        return_value=subscription
    ), patch(
        "services.usage_service.UsageService.get_plan",
        return_value=plan
    ), patch(
        "services.usage_service.UsageRepository.get_by_subscription",
        return_value=[]
    ):

        result = UsageService.get_usage_summary(
            db,
            1
        )

    assert result["data_percentage"] == 0
    assert result["voice_percentage"] == 0
    assert result["sms_percentage"] == 0

    assert result["data_remaining"] == 0
    assert result["voice_remaining"] == 0
    assert result["sms_remaining"] == 0


# ============================================================
# get_daily_usage()
# ============================================================

def test_get_daily_usage_success():

    db = MagicMock()

    usage_records = [
        MagicMock(),
        MagicMock()
    ]

    date_value = date(
        2026,
        5,
        15
    )

    with patch(
        "services.usage_service.UsageRepository.get_between_dates",
        return_value=usage_records
    ) as mock_get:

        result = UsageService.get_daily_usage(
            db,
            1,
            date_value
        )

    assert result == usage_records

    kwargs = mock_get.call_args.kwargs

    assert kwargs["db"] == db
    assert kwargs["subscription_id"] == 1

    assert kwargs["start_date"] == datetime(
        2026,
        5,
        15,
        tzinfo=timezone.utc
    )

    assert kwargs["end_date"] == datetime(
        2026,
        5,
        16,
        tzinfo=timezone.utc
    )


# ============================================================
# get_monthly_usage()
# ============================================================

def test_get_monthly_usage_success():

    db = MagicMock()

    usage_records = [
        MagicMock(),
        MagicMock()
    ]

    with patch(
        "services.usage_service.UsageRepository.get_between_dates",
        return_value=usage_records
    ) as mock_get:

        result = UsageService.get_monthly_usage(
            db,
            subscription_id=1,
            year=2026,
            month=5
        )

    assert result == usage_records

    kwargs = mock_get.call_args.kwargs

    assert kwargs["db"] == db
    assert kwargs["subscription_id"] == 1

    assert kwargs["start_date"] == datetime(
        2026,
        5,
        1,
        tzinfo=timezone.utc
    )

    assert kwargs["end_date"] == datetime(
        2026,
        6,
        1,
        tzinfo=timezone.utc
    )


def test_get_monthly_usage_january():

    db = MagicMock()

    with patch(
        "services.usage_service.UsageRepository.get_between_dates",
        return_value=[]
    ) as mock_get:

        result = UsageService.get_monthly_usage(
            db,
            subscription_id=1,
            year=2026,
            month=1
        )

    assert result == []

    kwargs = mock_get.call_args.kwargs

    assert kwargs["start_date"] == datetime(
        2026,
        1,
        1,
        tzinfo=timezone.utc
    )

    assert kwargs["end_date"] == datetime(
        2026,
        2,
        1,
        tzinfo=timezone.utc
    )


def test_get_monthly_usage_december():

    db = MagicMock()

    with patch(
        "services.usage_service.UsageRepository.get_between_dates",
        return_value=[]
    ) as mock_get:

        result = UsageService.get_monthly_usage(
            db,
            subscription_id=1,
            year=2026,
            month=12
        )

    assert result == []

    kwargs = mock_get.call_args.kwargs

    assert kwargs["start_date"] == datetime(
        2026,
        12,
        1,
        tzinfo=timezone.utc
    )

    assert kwargs["end_date"] == datetime(
        2027,
        1,
        1,
        tzinfo=timezone.utc
    )


@pytest.mark.parametrize(
    "month",
    [
        0,
        13,
        -1,
        20
    ]
)
def test_get_monthly_usage_invalid_month(month):

    db = MagicMock()

    with pytest.raises(HTTPException) as exc:

        UsageService.get_monthly_usage(
            db,
            subscription_id=1,
            year=2026,
            month=month
        )

    assert exc.value.status_code == 400

    assert (
        exc.value.detail
        == "Month must be between 1 and 12"
    )