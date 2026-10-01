from sqlalchemy.orm import Session

from models.outage_tower_model import OutageTower


class OutageTowerRepository:

    @staticmethod
    def create(
        db: Session,
        outage_id: int,
        tower_id: int
    ) -> OutageTower:

        mapping = OutageTower(
            outage_id=outage_id,
            tower_id=tower_id
        )

        db.add(mapping)
        db.flush()

        return mapping

    @staticmethod
    def get_tower_ids(
        db: Session,
        outage_id: int
    ) -> list[int]:

        rows = (
            db.query(OutageTower)
            .filter(
                OutageTower.outage_id == outage_id
            )
            .all()
        )

        return [row.tower_id for row in rows]