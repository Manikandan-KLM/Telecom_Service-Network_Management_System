from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String
)
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class TicketSLA(Base):
    __tablename__ = "ticket_slas"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    ticket_id: Mapped[int] = mapped_column(
        ForeignKey("support_tickets.id"),
        unique=True,
        nullable=False,
        index=True
    )

    sla_rule_id: Mapped[int] = mapped_column(
        ForeignKey("sla_rules.id"),
        nullable=False,
        index=True
    )

    sla_start_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

    sla_deadline: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True
    )

    resolution_time_minutes: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    actual_resolution_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    sla_breached: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        index=True
    )

    escalation_status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="Normal",
        index=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow
    )