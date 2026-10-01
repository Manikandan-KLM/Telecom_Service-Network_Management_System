import pytest
from unittest.mock import MagicMock, patch

from fastapi import HTTPException

from services.customer_service import CustomerService


# ============================================================
# GENERATE CUSTOMER NUMBER
# ============================================================

def test_generate_customer_number_first_customer():
    db = MagicMock()

    db.query.return_value.order_by.return_value.first.return_value = None

    result = CustomerService.generate_customer_number(db)

    assert result == "CUST000001"


def test_generate_customer_number_next_customer():
    db = MagicMock()

    last_customer = MagicMock()
    last_customer.id = 5

    db.query.return_value.order_by.return_value.first.return_value = (
        last_customer
    )

    result = CustomerService.generate_customer_number(db)

    assert result == "CUST000006"


# ============================================================
# ADD HISTORY
# ============================================================

@patch("services.customer_service.CustomerHistoryRepository")
def test_add_history(
    mock_history_repository
):
    db = MagicMock()

    fake_history = MagicMock()

    mock_history_repository.create.return_value = fake_history

    result = CustomerService.add_history(
        db=db,
        customer_id=1,
        action="Customer Registered",
        description="Customer profile created",
        changed_by=10
    )

    assert result == fake_history

    mock_history_repository.create.assert_called_once()

    history_object = (
        mock_history_repository.create.call_args.args[1]
    )

    assert history_object.customer_id == 1
    assert history_object.action == "Customer Registered"
    assert history_object.description == "Customer profile created"
    assert history_object.changed_by == 10


# ============================================================
# CREATE CUSTOMER - SUCCESS
# ============================================================

@patch("services.customer_service.CustomerService.add_history")
@patch("services.customer_service.CustomerService.generate_customer_number")
@patch("services.customer_service.CustomerRepository")
def test_create_customer_success(
    mock_customer_repository,
    mock_generate_customer_number,
    mock_add_history
):
    db = MagicMock()

    mock_customer_repository.get_by_email.return_value = None
    mock_customer_repository.get_by_user_id.return_value = None

    mock_generate_customer_number.return_value = "CUST000001"

    fake_customer = MagicMock()
    fake_customer.id = 1

    mock_customer_repository.create.return_value = fake_customer

    result = CustomerService.create_customer(
        db=db,
        user_id=10,
        full_name="Test User",
        email="TEST@EXAMPLE.COM",
        phone="9876543210",
        address_line1="123 Main Street",
        address_line2="Near Bus Stand",
        city="Chennai",
        state="Tamil Nadu",
        postal_code="600001",
        country="India"
    )

    assert result == fake_customer

    mock_customer_repository.get_by_email.assert_called_once_with(
        db,
        "TEST@EXAMPLE.COM"
    )

    mock_customer_repository.get_by_user_id.assert_called_once_with(
        db,
        10
    )

    mock_generate_customer_number.assert_called_once_with(db)

    mock_customer_repository.create.assert_called_once()

    customer_object = (
        mock_customer_repository.create.call_args.args[1]
    )

    assert customer_object.user_id == 10
    assert customer_object.customer_number == "CUST000001"
    assert customer_object.full_name == "Test User"
    assert customer_object.email == "test@example.com"
    assert customer_object.phone == "9876543210"
    assert customer_object.address_line1 == "123 Main Street"
    assert customer_object.address_line2 == "Near Bus Stand"
    assert customer_object.city == "Chennai"
    assert customer_object.state == "Tamil Nadu"
    assert customer_object.postal_code == "600001"
    assert customer_object.country == "India"
    assert customer_object.kyc_status == "Pending"
    assert customer_object.is_active is True

    mock_add_history.assert_called_once_with(
        db=db,
        customer_id=1,
        action="Customer Registered",
        description="Customer profile created",
        changed_by=10
    )


# ============================================================
# CREATE CUSTOMER - DUPLICATE EMAIL
# ============================================================

@patch("services.customer_service.CustomerRepository")
def test_create_customer_duplicate_email(
    mock_customer_repository
):
    db = MagicMock()

    existing_customer = MagicMock()

    mock_customer_repository.get_by_email.return_value = (
        existing_customer
    )

    with pytest.raises(HTTPException) as exc_info:

        CustomerService.create_customer(
            db=db,
            user_id=10,
            full_name="Test User",
            email="test@example.com",
            phone="9876543210",
            address_line1="123 Main Street",
            address_line2=None,
            city="Chennai",
            state="Tamil Nadu",
            postal_code="600001",
            country="India"
        )

    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == "Customer email already exists"

    mock_customer_repository.create.assert_not_called()


# ============================================================
# CREATE CUSTOMER - EXISTING USER PROFILE
# ============================================================

@patch("services.customer_service.CustomerRepository")
def test_create_customer_existing_profile(
    mock_customer_repository
):
    db = MagicMock()

    mock_customer_repository.get_by_email.return_value = None

    existing_customer = MagicMock()

    mock_customer_repository.get_by_user_id.return_value = (
        existing_customer
    )

    with pytest.raises(HTTPException) as exc_info:

        CustomerService.create_customer(
            db=db,
            user_id=10,
            full_name="Test User",
            email="test@example.com",
            phone="9876543210",
            address_line1="123 Main Street",
            address_line2=None,
            city="Chennai",
            state="Tamil Nadu",
            postal_code="600001",
            country="India"
        )

    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == "Customer profile already exists"

    mock_customer_repository.create.assert_not_called()


# ============================================================
# GET CUSTOMER - SUCCESS
# ============================================================

@patch("services.customer_service.CustomerRepository")
def test_get_customer_success(
    mock_customer_repository
):
    db = MagicMock()

    fake_customer = MagicMock()
    fake_customer.id = 1

    mock_customer_repository.get_by_id.return_value = (
        fake_customer
    )

    result = CustomerService.get_customer(
        db=db,
        customer_id=1
    )

    assert result == fake_customer

    mock_customer_repository.get_by_id.assert_called_once_with(
        db,
        1
    )


# ============================================================
# GET CUSTOMER - NOT FOUND
# ============================================================

@patch("services.customer_service.CustomerRepository")
def test_get_customer_not_found(
    mock_customer_repository
):
    db = MagicMock()

    mock_customer_repository.get_by_id.return_value = None

    with pytest.raises(HTTPException) as exc_info:

        CustomerService.get_customer(
            db=db,
            customer_id=999
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Customer not found"


# ============================================================
# UPDATE PROFILE - FULL UPDATE
# ============================================================

@patch("services.customer_service.CustomerService.add_history")
@patch("services.customer_service.CustomerRepository")
def test_update_profile_success(
    mock_customer_repository,
    mock_add_history
):
    db = MagicMock()

    fake_customer = MagicMock()
    fake_customer.id = 1
    fake_customer.full_name = "Old Name"
    fake_customer.phone = "1111111111"

    mock_customer_repository.get_by_id.return_value = (
        fake_customer
    )

    mock_customer_repository.update.return_value = fake_customer

    result = CustomerService.update_profile(
        db=db,
        customer_id=1,
        full_name="New Name",
        phone="9999999999",
        changed_by=10
    )

    assert result == fake_customer

    assert fake_customer.full_name == "New Name"
    assert fake_customer.phone == "9999999999"

    mock_customer_repository.update.assert_called_once_with(
        db,
        fake_customer
    )

    mock_add_history.assert_called_once_with(
        db=db,
        customer_id=1,
        action="Profile Updated",
        description="Customer profile information updated",
        changed_by=10
    )


# ============================================================
# UPDATE PROFILE - NO CHANGES
# ============================================================

@patch("services.customer_service.CustomerService.add_history")
@patch("services.customer_service.CustomerRepository")
def test_update_profile_no_changes(
    mock_customer_repository,
    mock_add_history
):
    db = MagicMock()

    fake_customer = MagicMock()
    fake_customer.id = 1

    mock_customer_repository.get_by_id.return_value = (
        fake_customer
    )

    result = CustomerService.update_profile(
        db=db,
        customer_id=1,
        full_name=None,
        phone=None,
        changed_by=10
    )

    assert result == fake_customer

    mock_customer_repository.update.assert_not_called()

    mock_add_history.assert_not_called()


# ============================================================
# UPDATE PROFILE - CUSTOMER NOT FOUND
# ============================================================

@patch("services.customer_service.CustomerRepository")
def test_update_profile_customer_not_found(
    mock_customer_repository
):
    db = MagicMock()

    mock_customer_repository.get_by_id.return_value = None

    with pytest.raises(HTTPException) as exc_info:

        CustomerService.update_profile(
            db=db,
            customer_id=999,
            full_name="New Name",
            phone=None,
            changed_by=10
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Customer not found"


# ============================================================
# UPDATE CONTACT
# ============================================================

@patch("services.customer_service.CustomerService.add_history")
@patch("services.customer_service.CustomerRepository")
def test_update_contact_success(
    mock_customer_repository,
    mock_add_history
):
    db = MagicMock()

    fake_customer = MagicMock()
    fake_customer.id = 1
    fake_customer.phone = "1111111111"

    mock_customer_repository.get_by_id.return_value = (
        fake_customer
    )

    mock_customer_repository.update.return_value = fake_customer

    result = CustomerService.update_contact(
        db=db,
        customer_id=1,
        phone="9999999999",
        changed_by=10
    )

    assert result == fake_customer
    assert fake_customer.phone == "9999999999"

    mock_customer_repository.update.assert_called_once_with(
        db,
        fake_customer
    )

    mock_add_history.assert_called_once_with(
        db=db,
        customer_id=1,
        action="Contact Updated",
        description="Customer phone number updated",
        changed_by=10
    )


# ============================================================
# UPDATE ADDRESS
# ============================================================

@patch("services.customer_service.CustomerService.add_history")
@patch("services.customer_service.CustomerRepository")
def test_update_address_success(
    mock_customer_repository,
    mock_add_history
):
    db = MagicMock()

    fake_customer = MagicMock()
    fake_customer.id = 1

    mock_customer_repository.get_by_id.return_value = (
        fake_customer
    )

    mock_customer_repository.update.return_value = fake_customer

    result = CustomerService.update_address(
        db=db,
        customer_id=1,
        address_line1="456 New Street",
        address_line2="Apartment 2",
        city="Coimbatore",
        state="Tamil Nadu",
        postal_code="641001",
        country="India",
        changed_by=10
    )

    assert result == fake_customer

    assert fake_customer.address_line1 == "456 New Street"
    assert fake_customer.address_line2 == "Apartment 2"
    assert fake_customer.city == "Coimbatore"
    assert fake_customer.state == "Tamil Nadu"
    assert fake_customer.postal_code == "641001"
    assert fake_customer.country == "India"

    mock_customer_repository.update.assert_called_once_with(
        db,
        fake_customer
    )

    mock_add_history.assert_called_once_with(
        db=db,
        customer_id=1,
        action="Address Updated",
        description="Customer address updated",
        changed_by=10
    )


# ============================================================
# UPDATE KYC STATUS - SUCCESS
# ============================================================

@patch("services.customer_service.CustomerService.add_history")
@patch("services.customer_service.CustomerRepository")
def test_update_kyc_status_success(
    mock_customer_repository,
    mock_add_history
):
    db = MagicMock()

    fake_customer = MagicMock()
    fake_customer.id = 1
    fake_customer.kyc_status = "Pending"

    mock_customer_repository.get_by_id.return_value = (
        fake_customer
    )

    mock_customer_repository.update.return_value = fake_customer

    result = CustomerService.update_kyc_status(
        db=db,
        customer_id=1,
        kyc_status="Verified",
        changed_by=10
    )

    assert result == fake_customer
    assert fake_customer.kyc_status == "Verified"

    mock_customer_repository.update.assert_called_once_with(
        db,
        fake_customer
    )

    mock_add_history.assert_called_once_with(
        db=db,
        customer_id=1,
        action="KYC Status Updated",
        description="KYC status changed to Verified",
        changed_by=10
    )


# ============================================================
# UPDATE KYC STATUS - INVALID STATUS
# ============================================================

def test_update_kyc_status_invalid():
    db = MagicMock()

    with pytest.raises(HTTPException) as exc_info:

        CustomerService.update_kyc_status(
            db=db,
            customer_id=1,
            kyc_status="Invalid",
            changed_by=10
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Invalid KYC status"


# ============================================================
# UPDATE STATUS - ACTIVATE
# ============================================================

@patch("services.customer_service.CustomerService.add_history")
@patch("services.customer_service.CustomerRepository")
def test_update_status_activate(
    mock_customer_repository,
    mock_add_history
):
    db = MagicMock()

    fake_customer = MagicMock()
    fake_customer.id = 1
    fake_customer.is_active = False

    mock_customer_repository.get_by_id.return_value = (
        fake_customer
    )

    mock_customer_repository.update.return_value = fake_customer

    result = CustomerService.update_status(
        db=db,
        customer_id=1,
        is_active=True,
        changed_by=10
    )

    assert result == fake_customer
    assert fake_customer.is_active is True

    mock_add_history.assert_called_once_with(
        db=db,
        customer_id=1,
        action="Customer Activated",
        description="Customer account activated",
        changed_by=10
    )


# ============================================================
# UPDATE STATUS - DEACTIVATE
# ============================================================

@patch("services.customer_service.CustomerService.add_history")
@patch("services.customer_service.CustomerRepository")
def test_update_status_deactivate(
    mock_customer_repository,
    mock_add_history
):
    db = MagicMock()

    fake_customer = MagicMock()
    fake_customer.id = 1
    fake_customer.is_active = True

    mock_customer_repository.get_by_id.return_value = (
        fake_customer
    )

    mock_customer_repository.update.return_value = fake_customer

    result = CustomerService.update_status(
        db=db,
        customer_id=1,
        is_active=False,
        changed_by=10
    )

    assert result == fake_customer
    assert fake_customer.is_active is False

    mock_add_history.assert_called_once_with(
        db=db,
        customer_id=1,
        action="Customer Deactivated",
        description="Customer account deactivated",
        changed_by=10
    )


# ============================================================
# GET HISTORY
# ============================================================

@patch("services.customer_service.CustomerHistoryRepository")
@patch("services.customer_service.CustomerRepository")
def test_get_history_success(
    mock_customer_repository,
    mock_history_repository
):
    db = MagicMock()

    fake_customer = MagicMock()
    fake_customer.id = 1

    fake_history = [
        MagicMock(),
        MagicMock()
    ]

    mock_customer_repository.get_by_id.return_value = (
        fake_customer
    )

    mock_history_repository.get_by_customer_id.return_value = (
        fake_history
    )

    result = CustomerService.get_history(
        db=db,
        customer_id=1
    )

    assert result == fake_history

    mock_customer_repository.get_by_id.assert_called_once_with(
        db,
        1
    )

    mock_history_repository.get_by_customer_id.assert_called_once_with(
        db,
        1
    )


# ============================================================
# GET HISTORY - CUSTOMER NOT FOUND
# ============================================================

@patch("services.customer_service.CustomerRepository")
def test_get_history_customer_not_found(
    mock_customer_repository
):
    db = MagicMock()

    mock_customer_repository.get_by_id.return_value = None

    with pytest.raises(HTTPException) as exc_info:

        CustomerService.get_history(
            db=db,
            customer_id=999
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Customer not found"

