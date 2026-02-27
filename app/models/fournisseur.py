from datetime import datetime

from sqlalchemy import String, Text, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Fournisseur(Base):
    __tablename__ = "fournisseurs"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    raison_sociale: Mapped[str] = mapped_column(String(255))
    contact: Mapped[str | None] = mapped_column(String(100))
    telephone: Mapped[str | None] = mapped_column(String(20))
    email: Mapped[str | None] = mapped_column(String(255))
    adresse: Mapped[str | None] = mapped_column(String(255))
    code_postal: Mapped[str | None] = mapped_column(String(10))
    ville: Mapped[str | None] = mapped_column(String(100))
    pays: Mapped[str] = mapped_column(String(50), default="France")
    siret: Mapped[str | None] = mapped_column(String(14))
    notes: Mapped[str | None] = mapped_column(Text)
    actif: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class Revendeur(Base):
    __tablename__ = "revendeurs"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    raison_sociale: Mapped[str] = mapped_column(String(255))
    contact: Mapped[str | None] = mapped_column(String(100))
    telephone: Mapped[str | None] = mapped_column(String(20))
    email: Mapped[str | None] = mapped_column(String(255))
    adresse: Mapped[str | None] = mapped_column(String(255))
    code_postal: Mapped[str | None] = mapped_column(String(10))
    ville: Mapped[str | None] = mapped_column(String(100))
    pays: Mapped[str] = mapped_column(String(50), default="France")
    vrp_id: Mapped[int | None] = mapped_column(ForeignKey("vrps.id"))
    notes: Mapped[str | None] = mapped_column(Text)
    actif: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
