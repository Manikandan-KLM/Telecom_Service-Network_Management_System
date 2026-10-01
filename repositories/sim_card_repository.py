from sqlalchemy import or_
from sqlalchemy.orm import Session

from models.sim_card_model import SIMCard


class SIMCardRepository:

    @staticmethod
    def get_by_id(
        db: Session,
        sim_id: int
    ) -> SIMCard | None:

        return (
            db.query(SIMCard)
            .filter(SIMCard.id == sim_id)
            .first()
        )

    @staticmethod
    def get_by_sim_number(
        db: Session,
        sim_number: str
    ) -> SIMCard | None:

        return (
            db.query(SIMCard)
            .filter(
                SIMCard.sim_number == sim_number
            )
            .first()
        )

    @staticmethod
    def create(
        db: Session,
        sim: SIMCard
    ) -> SIMCard:

        db.add(sim)
        db.commit()
        db.refresh(sim)

        return sim

    @staticmethod
    def update(
        db: Session,
        sim: SIMCard
    ) -> SIMCard:

        db.commit()
        db.refresh(sim)

        return sim

    @staticmethod
    def search(
        db: Session,
        search: str | None = None,
        sim_type: str | None = None,
        status: str | None = None,
        customer_id: int | None = None,
        plan_id: int | None = None
    ):

        query = db.query(SIMCard)

        if search:

            search_value = f"%{search}%"

            query = query.filter(
                or_(
                    SIMCard.sim_number.ilike(search_value)
                )
            )

        if sim_type:
            query = query.filter(
                SIMCard.sim_type == sim_type
            )

        if status:
            query = query.filter(
                SIMCard.status == status
            )

        if customer_id:
            query = query.filter(
                SIMCard.customer_id == customer_id
            )

        if plan_id:
            query = query.filter(
                SIMCard.plan_id == plan_id
            )

        return (
            query
            .order_by(SIMCard.id.desc())
            .all()
        )