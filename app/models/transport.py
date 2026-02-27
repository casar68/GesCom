from datetime import datetime
from decimal import Decimal

from sqlalchemy import String, Numeric, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Transport(Base):
    __tablename__ = "transports"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    nom: Mapped[str] = mapped_column(String(255))
    telephone: Mapped[str | None] = mapped_column(String(20))
    email: Mapped[str | None] = mapped_column(String(255))
    tarif_base: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    tarif_kg: Mapped[Decimal] = mapped_column(Numeric(10, 4), default=0)
    delai_moyen_jours: Mapped[int | None] = mapped_column()
    actif: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
