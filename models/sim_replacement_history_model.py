from datetime import datetime, timezone

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class SIMReplacementHistory(Base):
    __tablename__ = "sim_replacement_history"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    old_sim_id: Mapped[int] = mapped_column(
        ForeignKey("sim_cards.id"),
        nullable=False,
        index=True
    )

    new_sim_id: Mapped[int] = mapped_column(
        ForeignKey("sim_cards.id"),
        nullable=False,
        index=True
    )

    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id"),
        nullable=False,
        index=True
    )

    reason: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    remarks: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    replaced_by: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )

    replaced_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )