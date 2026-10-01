from sqlalchemy.orm import Session

from models.network_outage_model import NetworkOutage


class NetworkOutageRepository:

    @staticmethod
    def get_by_id(
        db: Session,
        outage_id: int
    ) -> NetworkOutage | None:

        return (
            db.query(NetworkOutage)
            .filter(NetworkOutage.id == outage_id)
            .first()
        )

    @staticmethod
    def get_by_code(
        db: Session,
        outage_code: str
    ) -> NetworkOutage | None:

        return (
            db.query(NetworkOutage)
            .filter(NetworkOutage.outage_code == outage_code)
            .first()
        )

    @staticmethod
    def create(
        db: Session,
        outage: NetworkOutage
    ) -> NetworkOutage:

        db.add(outage)
        db.commit()
        db.refresh(outage)

        return outage

    @staticmethod
    def update(
        db: Session,
        outage: NetworkOutage
    ) -> NetworkOutage:

        db.commit()
        db.refresh(outage)

        return outage

    @staticmethod
    def get_all(
        db: Session,
        severity: str | None = None,
        status: str | None = None,
        outage_type: str | None = None
    ):

        query = db.query(NetworkOutage)

        if severity:
            query = query.filter(
                NetworkOutage.severity == severity
            )

        if status:
            query = query.filter(
                NetworkOutage.status == status
            )

        if outage_type:
            query = query.filter(
                NetworkOutage.outage_type == outage_type
            )

        return query.order_by(
            NetworkOutage.created_at.desc()
        ).all()