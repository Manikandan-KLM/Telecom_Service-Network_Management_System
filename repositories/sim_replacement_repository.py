from sqlalchemy.orm import Session

from models.sim_replacement_history_model import (
    SIMReplacementHistory
)


class SIMReplacementRepository:

    @staticmethod
    def create(
        db: Session,
        history: SIMReplacementHistory
    ) -> SIMReplacementHistory:

        db.add(history)
        db.commit()
        db.refresh(history)

        return history

    @staticmethod
    def get_by_customer_id(
        db: Session,
        customer_id: int
    ):

        return (
            db.query(SIMReplacementHistory)
            .filter(
                SIMReplacementHistory.customer_id
                == customer_id
            )
            .order_by(
                SIMReplacementHistory.replaced_at.desc()
            )
            .all()
        )

    @staticmethod
    def get_by_sim_id(
        db: Session,
        sim_id: int
    ):

        return (
            db.query(SIMReplacementHistory)
            .filter(
                (
                    SIMReplacementHistory.old_sim_id
                    == sim_id
                )
                |
                (
                    SIMReplacementHistory.new_sim_id
                    == sim_id
                )
            )
            .order_by(
                SIMReplacementHistory.replaced_at.desc()
            )
            .all()
        )