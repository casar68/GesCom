from datetime import datetime
from decimal import Decimal

from sqlalchemy import String, Text, Numeric, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Client(Base):
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(primary_key=True)
    code_client: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    raison_sociale: Mapped[str] = mapped_column(String(255), index=True)
    type_client: Mapped[str] = mapped_column(String(50), default="standard")
    siret: Mapped[str | None] = mapped_column(String(14))
    tva_intra: Mapped[str | None] = mapped_column(String(20))

    # Contact principal
    telephone: Mapped[str | None] = mapped_column(String(20))
    fax: Mapped[str | None] = mapped_column(String(20))
    email: Mapped[str | None] = mapped_column(String(255))
    site_web: Mapped[str | None] = mapped_column(String(255))

    # Adresse principale
    adresse: Mapped[str | None] = mapped_column(String(255))
    complement_adresse: Mapped[str | None] = mapped_column(String(255))
    code_postal: Mapped[str | None] = mapped_column(String(10))
    ville: Mapped[str | None] = mapped_column(String(100))
    pays: Mapped[str] = mapped_column(String(50), default="France")

    # Commercial
    vrp_id: Mapped[int | None] = mapped_column(ForeignKey("vrps.id"))
    concession_id: Mapped[int | None] = mapped_column(ForeignKey("concessions.id"))
    encours_max: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    mode_reglement: Mapped[str | None] = mapped_column(String(50))
    delai_reglement: Mapped[int] = mapped_column(default=30)

    notes: Mapped[str | None] = mapped_column(Text)
    actif: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relations
    contacts: Mapped[list["ContactClient"]] = relationship(back_populates="client", cascade="all, delete-orphan")
    adresses: Mapped[list["AdresseClient"]] = relationship(back_populates="client", cascade="all, delete-orphan")


class ContactClient(Base):
    __tablename__ = "contacts_client"

    id: Mapped[int] = mapped_column(primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id", ondelete="CASCADE"), index=True)
    nom: Mapped[str] = mapped_column(String(100))
    prenom: Mapped[str | None] = mapped_column(String(100))
    fonction: Mapped[str | None] = mapped_column(String(100))
    telephone: Mapped[str | None] = mapped_column(String(20))
    mobile: Mapped[str | None] = mapped_column(String(20))
    email: Mapped[str | None] = mapped_column(String(255))
    principal: Mapped[bool] = mapped_column(Boolean, default=False)

    client: Mapped["Client"] = relationship(back_populates="contacts")


class AdresseClient(Base):
    __tablename__ = "adresses_client"

    id: Mapped[int] = mapped_column(primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id", ondelete="CASCADE"), index=True)
    type_adresse: Mapped[str] = mapped_column(String(50), default="livraison")
    adresse: Mapped[str] = mapped_column(String(255))
    complement: Mapped[str | None] = mapped_column(String(255))
    code_postal: Mapped[str] = mapped_column(String(10))
    ville: Mapped[str] = mapped_column(String(100))
    pays: Mapped[str] = mapped_column(String(50), default="France")
    par_defaut: Mapped[bool] = mapped_column(Boolean, default=False)

    client: Mapped["Client"] = relationship(back_populates="adresses")
