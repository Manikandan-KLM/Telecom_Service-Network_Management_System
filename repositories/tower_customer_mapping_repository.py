from sqlalchemy.orm import Session

from models.tower_customer_mapping_model import (
    TowerCustomerMapping
)


class TowerCustomerMappingRepository:

    @staticmethod
    def create(
        db: Session,
        tower_id: int,
        customer_id: int
    ) -> TowerCustomerMapping:

        mapping = TowerCustomerMapping(
            tower_id=tower_id,
            customer_id=customer_id
        )

        db.add(mapping)
        db.flush()

        return mapping

    @staticmethod
    def get_customer_ids_by_towers(
        db: Session,
        tower_ids: list[int]
    ) -> list[int]:

        rows = (
            db.query(TowerCustomerMapping)
            .filter(
                TowerCustomerMapping.tower_id.in_(tower_ids)
            )
            .all()
        )

        return list(
            set(row.customer_id for row in rows)
        )