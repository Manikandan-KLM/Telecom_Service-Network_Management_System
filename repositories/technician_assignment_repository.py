from sqlalchemy.orm import Session

from models.technician_assignment_model import (
    TechnicianAssignment
)


class TechnicianAssignmentRepository:

    @staticmethod
    def get_by_id(
        db: Session,
        assignment_id: int
    ) -> TechnicianAssignment | None:

        return (
            db.query(TechnicianAssignment)
            .filter(
                TechnicianAssignment.id
                == assignment_id
            )
            .first()
        )

    @staticmethod
    def create(
        db: Session,
        assignment: TechnicianAssignment
    ) -> TechnicianAssignment:

        db.add(assignment)
        db.commit()
        db.refresh(assignment)

        return assignment

    @staticmethod
    def update(
        db: Session,
        assignment: TechnicianAssignment
    ) -> TechnicianAssignment:

        db.commit()
        db.refresh(assignment)

        return assignment

    @staticmethod
    def get_by_technician(
        db: Session,
        technician_id: int
    ):

        return (
            db.query(TechnicianAssignment)
            .filter(
                TechnicianAssignment.technician_id
                == technician_id
            )
            .order_by(
                TechnicianAssignment.assigned_at.desc()
            )
            .all()
        )

    @staticmethod
    def count_by_status(
        db: Session,
        technician_id: int,
        status: str
    ) -> int:

        return (
            db.query(TechnicianAssignment)
            .filter(
                TechnicianAssignment.technician_id
                == technician_id,
                TechnicianAssignment.status
                == status
            )
            .count()
        )

    @staticmethod
    def get_all(
        db: Session
    ):

        return (
            db.query(TechnicianAssignment)
            .order_by(
                TechnicianAssignment.assigned_at.desc()
            )
            .all()
        )