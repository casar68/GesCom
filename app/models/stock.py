import enum
from datetime import datetime
from decimal import Decimal

from sqlalchemy import String, Text, Numeric, Integer, DateTime, ForeignKey, Enum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class TypeMouvement(str, enum.Enum):
    ENTREE = "entree"
    SORTIE = "sortie"
    TRANSFERT = "transfert"
    INVENTAIRE = "inventaire"
    RETOUR = "retour"


class StatutInventaire(str, enum.Enum):
    EN_COURS = "en_cours"
    VALIDE = "valide"
    ANNULE = "annule"


class MouvementStock(Base):
    __tablename__ = "mouvements_stock"

    id: Mapped[int] = mapped_column(primary_key=True)
    numero: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    type_mouvement: Mapped[TypeMouvement] = mapped_column(Enum(TypeMouvement))
    date_mouvement: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    depot_source: Mapped[str | None] = mapped_column(String(100))
    depot_destination: Mapped[str | None] = mapped_column(String(100))
    reference_document: Mapped[str | None] = mapped_column(String(50))
    notes: Mapped[str | None] = mapped_column(Text)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    lignes: Mapped[list["LigneMouvementStock"]] = relationship(
        back_populates="mouvement", cascade="all, delete-orphan"
    )


class LigneMouvementStock(Base):
    __tablename__ = "lignes_mouvement_stock"

    id: Mapped[int] = mapped_column(primary_key=True)
    mouvement_id: Mapped[int] = mapped_column(ForeignKey("mouvements_stock.id", ondelete="CASCADE"), index=True)
    article_id: Mapped[int] = mapped_column(ForeignKey("articles.id"), index=True)
    quantite: Mapped[int] = mapped_column(Integer)
    prix_unitaire: Mapped[Decimal] = mapped_column(Numeric(12, 4), default=0)
    taille: Mapped[str | None] = mapped_column(String(20))
    couleur: Mapped[str | None] = mapped_column(String(50))
    emplacement: Mapped[str | None] = mapped_column(String(50))

    mouvement: Mapped["MouvementStock"] = relationship(back_populates="lignes")


class Inventaire(Base):
    __tablename__ = "inventaires"

    id: Mapped[int] = mapped_column(primary_key=True)
    numero: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    depot: Mapped[str] = mapped_column(String(100))
    date_inventaire: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    statut: Mapped[StatutInventaire] = mapped_column(Enum(StatutInventaire), default=StatutInventaire.EN_COURS)
    notes: Mapped[str | None] = mapped_column(Text)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    lignes: Mapped[list["LigneInventaire"]] = relationship(back_populates="inventaire", cascade="all, delete-orphan")


class LigneInventaire(Base):
    __tablename__ = "lignes_inventaire"

    id: Mapped[int] = mapped_column(primary_key=True)
    inventaire_id: Mapped[int] = mapped_column(ForeignKey("inventaires.id", ondelete="CASCADE"), index=True)
    article_id: Mapped[int] = mapped_column(ForeignKey("articles.id"), index=True)
    stock_theorique: Mapped[int] = mapped_column(Integer, default=0)
    stock_physique: Mapped[int] = mapped_column(Integer, default=0)
    ecart: Mapped[int] = mapped_column(Integer, default=0)
    taille: Mapped[str | None] = mapped_column(String(20))
    couleur: Mapped[str | None] = mapped_column(String(50))

    inventaire: Mapped["Inventaire"] = relationship(back_populates="lignes")
