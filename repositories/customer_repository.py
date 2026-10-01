from sqlalchemy import or_
from sqlalchemy.orm import Session

from models.customer_model import Customer


class CustomerRepository:

    @staticmethod
    def get_by_id(
        db: Session,
        customer_id: int
    ) -> Customer | None:

        return (
            db.query(Customer)
            .filter(Customer.id == customer_id)
            .first()
        )

    @staticmethod
    def get_by_user_id(
        db: Session,
        user_id: int
    ) -> Customer | None:

        return (
            db.query(Customer)
            .filter(Customer.user_id == user_id)
            .first()
        )

    @staticmethod
    def get_by_email(
        db: Session,
        email: str
    ) -> Customer | None:

        return (
            db.query(Customer)
            .filter(Customer.email == email.lower())
            .first()
        )

    @staticmethod
    def get_by_customer_number(
        db: Session,
        customer_number: str
    ) -> Customer | None:

        return (
            db.query(Customer)
            .filter(
                Customer.customer_number == customer_number
            )
            .first()
        )

    @staticmethod
    def create(
        db: Session,
        customer: Customer
    ) -> Customer:

        db.add(customer)
        db.commit()
        db.refresh(customer)

        return customer

    @staticmethod
    def update(
        db: Session,
        customer: Customer
    ) -> Customer:

        db.commit()
        db.refresh(customer)

        return customer

    @staticmethod
    def search(
        db: Session,
        search: str | None = None,
        kyc_status: str | None = None,
        is_active: bool | None = None,
        city: str | None = None
    ):

        query = db.query(Customer)

        if search:
            search_value = f"%{search}%"

            query = query.filter(
                or_(
                    Customer.customer_number.ilike(
                        search_value
                    ),
                    Customer.full_name.ilike(
                        search_value
                    ),
                    Customer.email.ilike(
                        search_value
                    ),
                    Customer.phone.ilike(
                        search_value
                    )
                )
            )

        if kyc_status:
            query = query.filter(
                Customer.kyc_status == kyc_status
            )

        if is_active is not None:
            query = query.filter(
                Customer.is_active == is_active
            )

        if city:
            query = query.filter(
                Customer.city.ilike(city)
            )

        return query.order_by(
            Customer.id.desc()
        ).all()