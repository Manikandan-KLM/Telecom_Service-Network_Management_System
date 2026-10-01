from datetime import datetime, timezone

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text
)

from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class NetworkEquipment(Base):
    __tablename__ = "network_equipment"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    equipment_code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )

    equipment_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True
    )

    equipment_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )

    manufacturer: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    model_number: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    tower_id: Mapped[int | None] = mapped_column(
        ForeignKey("network_towers.id"),
        nullable=True,
        index=True
    )

    installation_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

    maintenance_schedule: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    health_status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="Healthy",
        index=True
    )

    cpu_usage: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0
    )

    memory_usage: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0
    )

    network_status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="Online",
        index=True
    )

    last_heartbeat: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    downtime_minutes: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )