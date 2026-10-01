from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.customer_model import Customer
from models.customer_history_model import CustomerHistory

from repositories.customer_repository import (
    CustomerRepository
)

from repositories.customer_history_repository import (
    CustomerHistoryRepository
)


class CustomerService:

    @staticmethod
    def generate_customer_number(
        db: Session
    ) -> str:

        last_customer = (
            db.query(Customer)
            .order_by(Customer.id.desc())
            .first()
        )

        if not last_customer:
            number = 1
        else:
            number = last_customer.id + 1

        return f"CUST{number:06d}"

    @staticmethod
    def add_history(
        db: Session,
        customer_id: int,
        action: str,
        description: str,
        changed_by: int | None
    ):

        history = CustomerHistory(
            customer_id=customer_id,
            action=action,
            description=description,
            changed_by=changed_by
        )

        return CustomerHistoryRepository.create(
            db,
            history
        )

    @staticmethod
    def create_customer(
        db: Session,
        user_id: int,
        full_name: str,
        email: str,
        phone: str,
        address_line1: str,
        address_line2: str | None,
        city: str,
        state: str,
        postal_code: str,
        country: str
    ):

        existing_email = CustomerRepository.get_by_email(
            db,
            email
        )

        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Customer email already exists"
            )

        existing_customer = (
            CustomerRepository.get_by_user_id(
                db,
                user_id
            )
        )

        if existing_customer:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Customer profile already exists"
            )

        customer_number = (
            CustomerService.generate_customer_number(db)
        )

        customer = Customer(
            user_id=user_id,
            customer_number=customer_number,
            full_name=full_name,
            email=email.lower(),
            phone=phone,
            address_line1=address_line1,
            address_line2=address_line2,
            city=city,
            state=state,
            postal_code=postal_code,
            country=country,
            kyc_status="Pending",
            is_active=True
        )

        customer = CustomerRepository.create(
            db,
            customer
        )

        CustomerService.add_history(
            db=db,
            customer_id=customer.id,
            action="Customer Registered",
            description="Customer profile created",
            changed_by=user_id
        )

        return customer

    @staticmethod
    def get_customer(
        db: Session,
        customer_id: int
    ):

        customer = CustomerRepository.get_by_id(
            db,
            customer_id
        )

        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )

        return customer

    @staticmethod
    def update_profile(
        db: Session,
        customer_id: int,
        full_name: str | None,
        phone: str | None,
        changed_by: int
    ):

        customer = CustomerService.get_customer(
            db,
            customer_id
        )

        changed = False

        if full_name is not None:
            customer.full_name = full_name
            changed = True

        if phone is not None:
            customer.phone = phone
            changed = True

        if changed:
            customer = CustomerRepository.update(
                db,
                customer
            )

            CustomerService.add_history(
                db=db,
                customer_id=customer.id,
                action="Profile Updated",
                description="Customer profile information updated",
                changed_by=changed_by
            )

        return customer

    @staticmethod
    def update_contact(
        db: Session,
        customer_id: int,
        phone: str,
        changed_by: int
    ):

        customer = CustomerService.get_customer(
            db,
            customer_id
        )

        customer.phone = phone

        customer = CustomerRepository.update(
            db,
            customer
        )

        CustomerService.add_history(
            db=db,
            customer_id=customer.id,
            action="Contact Updated",
            description="Customer phone number updated",
            changed_by=changed_by
        )

        return customer

    @staticmethod
    def update_address(
        db: Session,
        customer_id: int,
        address_line1: str,
        address_line2: str | None,
        city: str,
        state: str,
        postal_code: str,
        country: str,
        changed_by: int
    ):

        customer = CustomerService.get_customer(
            db,
            customer_id
        )

        customer.address_line1 = address_line1
        customer.address_line2 = address_line2
        customer.city = city
        customer.state = state
        customer.postal_code = postal_code
        customer.country = country

        customer = CustomerRepository.update(
            db,
            customer
        )

        CustomerService.add_history(
            db=db,
            customer_id=customer.id,
            action="Address Updated",
            description="Customer address updated",
            changed_by=changed_by
        )

        return customer

    @staticmethod
    def update_kyc_status(
        db: Session,
        customer_id: int,
        kyc_status: str,
        changed_by: int
    ):

        allowed_statuses = {
            "Pending",
            "Verified",
            "Rejected"
        }

        if kyc_status not in allowed_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid KYC status"
            )

        customer = CustomerService.get_customer(
            db,
            customer_id
        )

        customer.kyc_status = kyc_status

        customer = CustomerRepository.update(
            db,
            customer
        )

        CustomerService.add_history(
            db=db,
            customer_id=customer.id,
            action="KYC Status Updated",
            description=f"KYC status changed to {kyc_status}",
            changed_by=changed_by
        )

        return customer

    @staticmethod
    def update_status(
        db: Session,
        customer_id: int,
        is_active: bool,
        changed_by: int
    ):

        customer = CustomerService.get_customer(
            db,
            customer_id
        )

        customer.is_active = is_active

        customer = CustomerRepository.update(
            db,
            customer
        )

        action = (
            "Customer Activated"
            if is_active
            else "Customer Deactivated"
        )

        description = (
            "Customer account activated"
            if is_active
            else "Customer account deactivated"
        )

        CustomerService.add_history(
            db=db,
            customer_id=customer.id,
            action=action,
            description=description,
            changed_by=changed_by
        )

        return customer

    @staticmethod
    def get_history(
        db: Session,
        customer_id: int
    ):

        CustomerService.get_customer(
            db,
            customer_id
        )

        return CustomerHistoryRepository.get_by_customer_id(
            db,
            customer_id
        )