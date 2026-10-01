from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class TechnicianServiceArea(Base):
    __tablename__ = "technician_service_areas"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    technician_id: Mapped[int] = mapped_column(
        ForeignKey("technicians.id"),
        nullable=False,
        index=True
    )

    area_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True
    )