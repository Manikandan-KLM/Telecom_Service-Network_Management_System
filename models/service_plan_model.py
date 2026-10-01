from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    Integer,
    String,
    Text,
)

from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class ServicePlan(Base):

    __tablename__ = "service_plans"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    plan_code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )

    plan_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True
    )

    plan_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        index=True
    )

    data_limit: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0
    )

    voice_limit: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0
    )

    sms_limit: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0
    )

    validity_days: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    price: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        index=True
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