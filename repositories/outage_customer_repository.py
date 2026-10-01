from sqlalchemy.orm import Session

from models.outage_customer_model import OutageCustomer


class OutageCustomerRepository:

    @staticmethod
    def create(
        db: Session,
        outage_id: int,
        customer_id: int
    ) -> OutageCustomer:

        mapping = OutageCustomer(
            outage_id=outage_id,
            customer_id=customer_id
        )

        db.add(mapping)
        db.flush()

        return mapping

    @staticmethod
    def get_customer_ids(
        db: Session,
        outage_id: int
    ) -> list[int]:

        rows = (
            db.query(OutageCustomer)
            .filter(
                OutageCustomer.outage_id == outage_id
            )
            .all()
        )

        return [row.customer_id for row in rows]