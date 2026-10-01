from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class TowerCustomerMapping(Base):
    __tablename__ = "tower_customer_mappings"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    tower_id: Mapped[int] = mapped_column(
        ForeignKey("network_towers.id"),
        nullable=False,
        index=True
    )

    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id"),
        nullable=False,
        index=True
    )