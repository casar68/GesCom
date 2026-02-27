import enum
from datetime import datetime
from decimal import Decimal

from sqlalchemy import String, Text, Numeric, Integer, DateTime, ForeignKey, Enum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class StatutCommande(str, enum.Enum):
    BROUILLON = "brouillon"
    VALIDEE = "validee"
    EN_PREPARATION = "en_preparation"
    PREPAREE = "preparee"
    EXPEDIEE = "expediee"
    LIVREE = "livree"
    FACTUREE = "facturee"
    ANNULEE = "annulee"


class Commande(Base):
    __tablename__ = "commandes"

    id: Mapped[int] = mapped_column(primary_key=True)
    numero: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), index=True)
    vrp_id: Mapped[int | None] = mapped_column(ForeignKey("vrps.id"))
    statut: Mapped[StatutCommande] = mapped_column(Enum(StatutCommande), default=StatutCommande.BROUILLON)

    date_commande: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    date_livraison_souhaitee: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    reference_client: Mapped[str | None] = mapped_column(String(50))
    notes: Mapped[str | None] = mapped_column(Text)

    # Adresse de livraison
    adresse_livraison: Mapped[str | None] = mapped_column(String(255))
    cp_livraison: Mapped[str | None] = mapped_column(String(10))
    ville_livraison: Mapped[str | None] = mapped_column(String(100))
    pays_livraison: Mapped[str] = mapped_column(String(50), default="France")

    # Totaux
    total_ht: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    total_tva: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    total_ttc: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    remise_globale_pct: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relations
    lignes: Mapped[list["LigneCommande"]] = relationship(back_populates="commande", cascade="all, delete-orphan")


class LigneCommande(Base):
    __tablename__ = "lignes_commande"

    id: Mapped[int] = mapped_column(primary_key=True)
    commande_id: Mapped[int] = mapped_column(ForeignKey("commandes.id", ondelete="CASCADE"), index=True)
    article_id: Mapped[int] = mapped_column(ForeignKey("articles.id"), index=True)
    ligne_numero: Mapped[int] = mapped_column(Integer)

    designation: Mapped[str] = mapped_column(String(255))
    quantite: Mapped[int] = mapped_column(Integer, default=1)
    quantite_livree: Mapped[int] = mapped_column(Integer, default=0)
    prix_unitaire_ht: Mapped[Decimal] = mapped_column(Numeric(12, 4))
    remise_pct: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0)
    tva_pct: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=20.00)
    montant_ht: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)

    taille: Mapped[str | None] = mapped_column(String(20))
    couleur: Mapped[str | None] = mapped_column(String(50))

    commande: Mapped["Commande"] = relationship(back_populates="lignes")
