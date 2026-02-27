from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class ArticleTailleBase(BaseModel):
    taille: str
    stock: int = 0


class ArticleTailleCreate(ArticleTailleBase):
    pass


class ArticleTailleRead(ArticleTailleBase):
    id: int
    article_id: int
    model_config = {"from_attributes": True}


class ArticleCouleurBase(BaseModel):
    couleur: str
    code_hex: str | None = None
    stock: int = 0


class ArticleCouleurCreate(ArticleCouleurBase):
    pass


class ArticleCouleurRead(ArticleCouleurBase):
    id: int
    article_id: int
    model_config = {"from_attributes": True}


class ArticleDepotBase(BaseModel):
    depot: str
    stock: int = 0
    emplacement: str | None = None


class ArticleDepotCreate(ArticleDepotBase):
    pass


class ArticleDepotRead(ArticleDepotBase):
    id: int
    article_id: int
    model_config = {"from_attributes": True}


class ArticleTarifBase(BaseModel):
    nom_tarif: str
    prix_ht: Decimal
    remise_pct: Decimal = Decimal("0")
    date_debut: datetime | None = None
    date_fin: datetime | None = None


class ArticleTarifCreate(ArticleTarifBase):
    pass


class ArticleTarifRead(ArticleTarifBase):
    id: int
    article_id: int
    model_config = {"from_attributes": True}


class ArticleBase(BaseModel):
    reference: str
    designation: str
    description: str | None = None
    famille: str | None = None
    sous_famille: str | None = None
    gamme: str | None = None
    marque: str | None = None
    fournisseur_id: int | None = None
    prix_achat_ht: Decimal = Decimal("0")
    prix_vente_ht: Decimal = Decimal("0")
    tva: Decimal = Decimal("20.00")
    stock_actuel: int = 0
    stock_minimum: int = 0
    stock_maximum: int | None = None
    code_barre: str | None = None
    poids: Decimal | None = None
    unite: str = "pièce"
    photo_url: str | None = None
    ebusiness: bool = False
    actif: bool = True


class ArticleCreate(ArticleBase):
    tailles: list[ArticleTailleCreate] = []
    couleurs: list[ArticleCouleurCreate] = []


class ArticleUpdate(BaseModel):
    designation: str | None = None
    description: str | None = None
    famille: str | None = None
    sous_famille: str | None = None
    gamme: str | None = None
    marque: str | None = None
    fournisseur_id: int | None = None
    prix_achat_ht: Decimal | None = None
    prix_vente_ht: Decimal | None = None
    tva: Decimal | None = None
    stock_minimum: int | None = None
    stock_maximum: int | None = None
    code_barre: str | None = None
    poids: Decimal | None = None
    unite: str | None = None
    photo_url: str | None = None
    ebusiness: bool | None = None
    actif: bool | None = None


class ArticleRead(ArticleBase):
    id: int
    created_at: datetime
    updated_at: datetime
    tailles: list[ArticleTailleRead] = []
    couleurs: list[ArticleCouleurRead] = []
    depots: list[ArticleDepotRead] = []
    tarifs: list[ArticleTarifRead] = []
    model_config = {"from_attributes": True}


class ArticleList(BaseModel):
    id: int
    reference: str
    designation: str
    famille: str | None
    gamme: str | None
    marque: str | None
    prix_vente_ht: Decimal
    stock_actuel: int
    actif: bool
    model_config = {"from_attributes": True}
