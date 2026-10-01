from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class OutageTower(Base):
    __tablename__ = "outage_towers"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    outage_id: Mapped[int] = mapped_column(
        ForeignKey("network_outages.id"),
        nullable=False,
        index=True
    )

    tower_id: Mapped[int] = mapped_column(
        ForeignKey("network_towers.id"),
        nullable=False,
        index=True
    )