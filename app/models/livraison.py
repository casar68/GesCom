import enum
from datetime import datetime
from decimal import Decimal

from sqlalchemy import String, Text, Numeric, Integer, DateTime, ForeignKey, Enum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class StatutLivraison(str, enum.Enum):
    EN_PREPARATION = "en_preparation"
    PREPAREE = "preparee"
    EXPEDIEE = "expediee"
    LIVREE = "livree"
    RETOUR = "retour"
    ANNULEE = "annulee"


class BonLivraison(Base):
    __tablename__ = "bons_livraison"

    id: Mapped[int] = mapped_column(primary_key=True)
    numero: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    commande_id: Mapped[int | None] = mapped_column(ForeignKey("commandes.id"))
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), index=True)
    vrp_id: Mapped[int | None] = mapped_column(ForeignKey("vrps.id"))
    statut: Mapped[StatutLivraison] = mapped_column(Enum(StatutLivraison), default=StatutLivraison.EN_PREPARATION)
    transport_id: Mapped[int | None] = mapped_column(ForeignKey("transports.id"))

    date_bl: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    date_expedition: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    date_livraison: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    adresse_livraison: Mapped[str | None] = mapped_column(String(255))
    cp_livraison: Mapped[str | None] = mapped_column(String(10))
    ville_livraison: Mapped[str | None] = mapped_column(String(100))
    pays_livraison: Mapped[str] = mapped_column(String(50), default="France")

    poids_total: Mapped[Decimal] = mapped_column(Numeric(10, 3), default=0)
    nb_colis: Mapped[int] = mapped_column(Integer, default=0)
    notes: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    lignes: Mapped[list["LigneBonLivraison"]] = relationship(
        back_populates="bon_livraison", cascade="all, delete-orphan"
    )


class LigneBonLivraison(Base):
    __tablename__ = "lignes_bon_livraison"

    id: Mapped[int] = mapped_column(primary_key=True)
    bon_livraison_id: Mapped[int] = mapped_column(ForeignKey("bons_livraison.id", ondelete="CASCADE"), index=True)
    article_id: Mapped[int] = mapped_column(ForeignKey("articles.id"), index=True)
    ligne_numero: Mapped[int] = mapped_column(Integer)

    designation: Mapped[str] = mapped_column(String(255))
    quantite: Mapped[int] = mapped_column(Integer, default=1)
    taille: Mapped[str | None] = mapped_column(String(20))
    couleur: Mapped[str | None] = mapped_column(String(50))
    emplacement: Mapped[str | None] = mapped_column(String(50))

    bon_livraison: Mapped["BonLivraison"] = relationship(back_populates="lignes")
