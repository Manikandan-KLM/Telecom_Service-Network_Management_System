from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class TechnicianSkill(Base):
    __tablename__ = "technician_skills"

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

    skill_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True
    )

    skill_level: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="Intermediate"
    )