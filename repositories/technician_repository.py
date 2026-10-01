from sqlalchemy.orm import Session

from models.technician_model import Technician


class TechnicianRepository:

    @staticmethod
    def get_by_id(
        db: Session,
        technician_id: int
    ) -> Technician | None:

        return (
            db.query(Technician)
            .filter(
                Technician.id == technician_id
            )
            .first()
        )

    @staticmethod
    def get_by_code(
        db: Session,
        technician_code: str
    ) -> Technician | None:

        return (
            db.query(Technician)
            .filter(
                Technician.technician_code
                == technician_code
            )
            .first()
        )

    @staticmethod
    def get_by_user_id(
        db: Session,
        user_id: int
    ) -> Technician | None:

        return (
            db.query(Technician)
            .filter(
                Technician.user_id == user_id
            )
            .first()
        )

    @staticmethod
    def create(
        db: Session,
        technician: Technician
    ) -> Technician:

        db.add(technician)
        db.commit()
        db.refresh(technician)

        return technician

    @staticmethod
    def update(
        db: Session,
        technician: Technician
    ) -> Technician:

        db.commit()
        db.refresh(technician)

        return technician

    @staticmethod
    def get_all(
        db: Session,
        availability_status: str | None = None,
        service_area: str | None = None
    ):

        query = db.query(Technician)

        if availability_status:

            query = query.filter(
                Technician.availability_status
                == availability_status
            )

        if service_area:

            query = query.filter(
                Technician.service_area
                .ilike(f"%{service_area}%")
            )

        return query.order_by(
            Technician.created_at.desc()
        ).all()