from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    DateTime,
    Integer,
    String
)
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class SLARule(Base):
    __tablename__ = "sla_rules"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    rule_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    ticket_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )

    priority: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        index=True
    )

    customer_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        index=True
    )

    response_time_minutes: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    resolution_time_minutes: Mapped[int] = mapped_column(
        Integer,
        nullable=False
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