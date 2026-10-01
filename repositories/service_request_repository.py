from sqlalchemy.orm import Session

from models.service_request_model import ServiceRequest


class ServiceRequestRepository:

    @staticmethod
    def create(
        db: Session,
        request: ServiceRequest
    ):

        db.add(request)
        db.commit()
        db.refresh(request)

        return request

    @staticmethod
    def get_by_id(
        db: Session,
        request_id: int
    ):

        return (
            db.query(ServiceRequest)
            .filter(
                ServiceRequest.id == request_id
            )
            .first()
        )

    @staticmethod
    def get_by_number(
        db: Session,
        request_number: str
    ):

        return (
            db.query(ServiceRequest)
            .filter(
                ServiceRequest.request_number
                == request_number
            )
            .first()
        )

    @staticmethod
    def update(
        db: Session,
        request: ServiceRequest
    ):

        db.commit()
        db.refresh(request)

        return request

    @staticmethod
    def get_by_customer(
        db: Session,
        customer_id: int
    ):

        return (
            db.query(ServiceRequest)
            .filter(
                ServiceRequest.customer_id
                == customer_id
            )
            .order_by(
                ServiceRequest.created_at.desc()
            )
            .all()
        )

    @staticmethod
    def get_all(
        db: Session,
        status: str | None = None,
        request_type: str | None = None,
        priority: str | None = None
    ):

        query = db.query(ServiceRequest)

        if status:
            query = query.filter(
                ServiceRequest.status == status
            )

        if request_type:
            query = query.filter(
                ServiceRequest.request_type
                == request_type
            )

        if priority:
            query = query.filter(
                ServiceRequest.priority
                == priority
            )

        return (
            query
            .order_by(
                ServiceRequest.created_at.desc()
            )
            .all()
        )

    @staticmethod
    def get_by_assigned_user(
        db: Session,
        user_id: int
    ):

        return (
            db.query(ServiceRequest)
            .filter(
                ServiceRequest.assigned_to
                == user_id
            )
            .order_by(
                ServiceRequest.created_at.desc()
            )
            .all()
        )