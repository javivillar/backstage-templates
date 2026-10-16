"""Tables of the ${{ values.name }}."""

import enum
from datetime import date, datetime

from refresquito_fastapi.db import Base
from sqlalchemy import Date, DateTime, Enum, String, func
from sqlalchemy.orm import Mapped, mapped_column


class ${{ values.entityTitle }}Status(enum.StrEnum):
    active = "active"
    pending = "pending"
    closed = "closed"


class ${{ values.entityTitle }}(Base):
    __tablename__ = "${{ values.entity }}"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True)
    category: Mapped[str] = mapped_column(String(40), index=True)
    status: Mapped[${{ values.entityTitle }}Status] = mapped_column(
        Enum(${{ values.entityTitle }}Status, name="${{ values.entity }}_status", native_enum=False, length=16), default=${{ values.entityTitle }}Status.active, index=True
    )
    start_date: Mapped[date | None] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    created_by: Mapped[str] = mapped_column(String(120))
