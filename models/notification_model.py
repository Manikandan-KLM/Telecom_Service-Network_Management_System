from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text
)
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class Notification(Base):
    __tablename__ = "notifications"

    # =========================================================
    # PRIMARY KEY
    # =========================================================

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    # =========================================================
    # USER
    # =========================================================

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    # =========================================================
    # NOTIFICATION TYPE
    #
    # Ticket Assignment
    # SLA Breach
    # Network Outage
    # Service Restoration
    # Plan Expiry
    # Usage Threshold
    # SIM Suspension
    # Maintenance Schedule
    # =========================================================

    notification_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )

    # =========================================================
    # TITLE
    # =========================================================

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )

    # =========================================================
    # MESSAGE
    # =========================================================

    message: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    # =========================================================
    # RELATED ENTITY
    #
    # Example:
    # Ticket ID
    # Outage ID
    # Subscription ID
    # SIM ID
    # =========================================================

    entity_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        index=True
    )

    entity_id: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        index=True
    )

    # =========================================================
    # READ STATUS
    # =========================================================

    is_read: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        index=True
    )

    # =========================================================
    # CREATED DATE
    # =========================================================

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # =========================================================
    # READ DATE
    # =========================================================

    read_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )