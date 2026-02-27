from datetime import datetime
from decimal import Decimal

from sqlalchemy import String, Text, Numeric, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class VRP(Base):
    __tablename__ = "vrps"

    id: Mapped[int] = mapped_column(primary_key=True)
    code_vrp: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    nom: Mapped[str] = mapped_column(String(100))
    prenom: Mapped[str | None] = mapped_column(String(100))
    telephone: Mapped[str | None] = mapped_column(String(20))
    mobile: Mapped[str | None] = mapped_column(String(20))
    email: Mapped[str | None] = mapped_column(String(255))

    # Zone géographique
    secteur: Mapped[str | None] = mapped_column(String(100))
    departements: Mapped[str | None] = mapped_column(String(255))

    # Commercial
    taux_commission: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0)
    objectif_ca: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))

    actif: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    concessions: Mapped[list["Concession"]] = relationship(back_populates="vrp")


class Concession(Base):
    __tablename__ = "concessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    nom: Mapped[str] = mapped_column(String(255))
    vrp_id: Mapped[int | None] = mapped_column(ForeignKey("vrps.id"))
    adresse: Mapped[str | None] = mapped_column(String(255))
    code_postal: Mapped[str | None] = mapped_column(String(10))
    ville: Mapped[str | None] = mapped_column(String(100))
    telephone: Mapped[str | None] = mapped_column(String(20))
    actif: Mapped[bool] = mapped_column(Boolean, default=True)

    vrp: Mapped["VRP | None"] = relationship(back_populates="concessions")


class SuiviClient(Base):
    __tablename__ = "suivis_client"

    id: Mapped[int] = mapped_column(primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), index=True)
    vrp_id: Mapped[int | None] = mapped_column(ForeignKey("vrps.id"))
    date_action: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    type_action: Mapped[str] = mapped_column(String(50))
    description: Mapped[str | None] = mapped_column(Text)
    date_relance: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    fait: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Intervention(Base):
    __tablename__ = "interventions"

    id: Mapped[int] = mapped_column(primary_key=True)
    numero: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), index=True)
    date_intervention: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    type_intervention: Mapped[str] = mapped_column(String(50))
    description: Mapped[str | None] = mapped_column(Text)
    duree_minutes: Mapped[int | None] = mapped_column()
    cout: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    facture_id: Mapped[int | None] = mapped_column(ForeignKey("factures.id"))

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
