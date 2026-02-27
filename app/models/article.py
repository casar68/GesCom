from datetime import datetime
from decimal import Decimal

from sqlalchemy import String, Text, Numeric, Integer, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Article(Base):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(primary_key=True)
    reference: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    designation: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    famille: Mapped[str | None] = mapped_column(String(100), index=True)
    sous_famille: Mapped[str | None] = mapped_column(String(100))
    gamme: Mapped[str | None] = mapped_column(String(100), index=True)
    marque: Mapped[str | None] = mapped_column(String(100))
    fournisseur_id: Mapped[int | None] = mapped_column(ForeignKey("fournisseurs.id"))

    # Prix
    prix_achat_ht: Mapped[Decimal] = mapped_column(Numeric(12, 4), default=0)
    prix_vente_ht: Mapped[Decimal] = mapped_column(Numeric(12, 4), default=0)
    tva: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=20.00)

    # Stock
    stock_actuel: Mapped[int] = mapped_column(Integer, default=0)
    stock_minimum: Mapped[int] = mapped_column(Integer, default=0)
    stock_maximum: Mapped[int | None] = mapped_column(Integer)

    # Métadonnées
    code_barre: Mapped[str | None] = mapped_column(String(50))
    poids: Mapped[Decimal | None] = mapped_column(Numeric(10, 3))
    unite: Mapped[str] = mapped_column(String(20), default="pièce")
    photo_url: Mapped[str | None] = mapped_column(String(500))
    ebusiness: Mapped[bool] = mapped_column(Boolean, default=False)
    actif: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relations
    tailles: Mapped[list["ArticleTaille"]] = relationship(back_populates="article", cascade="all, delete-orphan")
    couleurs: Mapped[list["ArticleCouleur"]] = relationship(back_populates="article", cascade="all, delete-orphan")
    depots: Mapped[list["ArticleDepot"]] = relationship(back_populates="article", cascade="all, delete-orphan")
    tarifs: Mapped[list["ArticleTarif"]] = relationship(back_populates="article", cascade="all, delete-orphan")


class ArticleTaille(Base):
    __tablename__ = "article_tailles"

    id: Mapped[int] = mapped_column(primary_key=True)
    article_id: Mapped[int] = mapped_column(ForeignKey("articles.id", ondelete="CASCADE"), index=True)
    taille: Mapped[str] = mapped_column(String(20))
    stock: Mapped[int] = mapped_column(Integer, default=0)

    article: Mapped["Article"] = relationship(back_populates="tailles")


class ArticleCouleur(Base):
    __tablename__ = "article_couleurs"

    id: Mapped[int] = mapped_column(primary_key=True)
    article_id: Mapped[int] = mapped_column(ForeignKey("articles.id", ondelete="CASCADE"), index=True)
    couleur: Mapped[str] = mapped_column(String(50))
    code_hex: Mapped[str | None] = mapped_column(String(7))
    stock: Mapped[int] = mapped_column(Integer, default=0)

    article: Mapped["Article"] = relationship(back_populates="couleurs")


class ArticleDepot(Base):
    __tablename__ = "article_depots"

    id: Mapped[int] = mapped_column(primary_key=True)
    article_id: Mapped[int] = mapped_column(ForeignKey("articles.id", ondelete="CASCADE"), index=True)
    depot: Mapped[str] = mapped_column(String(100))
    stock: Mapped[int] = mapped_column(Integer, default=0)
    emplacement: Mapped[str | None] = mapped_column(String(50))

    article: Mapped["Article"] = relationship(back_populates="depots")


class ArticleTarif(Base):
    __tablename__ = "article_tarifs"

    id: Mapped[int] = mapped_column(primary_key=True)
    article_id: Mapped[int] = mapped_column(ForeignKey("articles.id", ondelete="CASCADE"), index=True)
    nom_tarif: Mapped[str] = mapped_column(String(100))
    prix_ht: Mapped[Decimal] = mapped_column(Numeric(12, 4))
    remise_pct: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0)
    date_debut: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    date_fin: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    article: Mapped["Article"] = relationship(back_populates="tarifs")
