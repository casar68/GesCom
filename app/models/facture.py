import enum
from datetime import datetime
from decimal import Decimal

from sqlalchemy import String, Text, Numeric, Integer, DateTime, ForeignKey, Enum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class StatutFacture(str, enum.Enum):
    BROUILLON = "brouillon"
    EMISE = "emise"
    ENVOYEE = "envoyee"
    PAYEE_PARTIELLEMENT = "payee_partiellement"
    PAYEE = "payee"
    EN_RETARD = "en_retard"
    ANNULEE = "annulee"
    AVOIR = "avoir"


class Facture(Base):
    __tablename__ = "factures"

    id: Mapped[int] = mapped_column(primary_key=True)
    numero: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), index=True)
    commande_id: Mapped[int | None] = mapped_column(ForeignKey("commandes.id"))
    vrp_id: Mapped[int | None] = mapped_column(ForeignKey("vrps.id"))
    statut: Mapped[StatutFacture] = mapped_column(Enum(StatutFacture), default=StatutFacture.BROUILLON)

    date_facture: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    date_echeance: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    mode_reglement: Mapped[str | None] = mapped_column(String(50))
    reference_client: Mapped[str | None] = mapped_column(String(50))
    notes: Mapped[str | None] = mapped_column(Text)

    # Adresse de facturation
    adresse_facturation: Mapped[str | None] = mapped_column(String(255))
    cp_facturation: Mapped[str | None] = mapped_column(String(10))
    ville_facturation: Mapped[str | None] = mapped_column(String(100))

    # Totaux
    total_ht: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    total_tva: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    total_ttc: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    montant_regle: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    remise_globale_pct: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    lignes: Mapped[list["LigneFacture"]] = relationship(back_populates="facture", cascade="all, delete-orphan")


class LigneFacture(Base):
    __tablename__ = "lignes_facture"

    id: Mapped[int] = mapped_column(primary_key=True)
    facture_id: Mapped[int] = mapped_column(ForeignKey("factures.id", ondelete="CASCADE"), index=True)
    article_id: Mapped[int] = mapped_column(ForeignKey("articles.id"), index=True)
    ligne_numero: Mapped[int] = mapped_column(Integer)

    designation: Mapped[str] = mapped_column(String(255))
    quantite: Mapped[int] = mapped_column(Integer, default=1)
    prix_unitaire_ht: Mapped[Decimal] = mapped_column(Numeric(12, 4))
    remise_pct: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0)
    tva_pct: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=20.00)
    montant_ht: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)

    taille: Mapped[str | None] = mapped_column(String(20))
    couleur: Mapped[str | None] = mapped_column(String(50))

    facture: Mapped["Facture"] = relationship(back_populates="lignes")
