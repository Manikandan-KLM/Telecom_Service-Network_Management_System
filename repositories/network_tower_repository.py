from sqlalchemy import or_
from sqlalchemy.orm import Session

from models.network_tower_model import NetworkTower


class NetworkTowerRepository:

    @staticmethod
    def get_by_id(
        db: Session,
        tower_id: int
    ) -> NetworkTower | None:

        return (
            db.query(NetworkTower)
            .filter(
                NetworkTower.id == tower_id
            )
            .first()
        )

    @staticmethod
    def get_by_number(
        db: Session,
        tower_number: str
    ) -> NetworkTower | None:

        return (
            db.query(NetworkTower)
            .filter(
                NetworkTower.tower_number == tower_number
            )
            .first()
        )

    @staticmethod
    def create(
        db: Session,
        tower: NetworkTower
    ) -> NetworkTower:

        db.add(tower)
        db.commit()
        db.refresh(tower)

        return tower

    @staticmethod
    def update(
        db: Session,
        tower: NetworkTower
    ) -> NetworkTower:

        db.commit()
        db.refresh(tower)

        return tower

    @staticmethod
    def search(
        db: Session,
        search: str | None = None,
        tower_type: str | None = None,
        tower_status: str | None = None
    ):

        query = db.query(NetworkTower)

        if search:

            search_value = f"%{search}%"

            query = query.filter(
                or_(
                    NetworkTower.tower_number.ilike(
                        search_value
                    ),
                    NetworkTower.tower_name.ilike(
                        search_value
                    )
                )
            )

        if tower_type:

            query = query.filter(
                NetworkTower.tower_type == tower_type
            )

        if tower_status:

            query = query.filter(
                NetworkTower.status == tower_status
            )

        return (
            query
            .order_by(NetworkTower.id.desc())
            .all()
        )

    @staticmethod
    def get_all(
        db: Session
    ):

        return (
            db.query(NetworkTower)
            .order_by(NetworkTower.id.desc())
            .all()
        )