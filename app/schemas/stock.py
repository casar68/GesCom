from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from app.models.stock import TypeMouvement, StatutInventaire


class LigneMouvementStockBase(BaseModel):
    article_id: int
    quantite: int
    prix_unitaire: Decimal = Decimal("0")
    taille: str | None = None
    couleur: str | None = None
    emplacement: str | None = None


class LigneMouvementStockCreate(LigneMouvementStockBase):
    pass


class LigneMouvementStockRead(LigneMouvementStockBase):
    id: int
    mouvement_id: int
    model_config = {"from_attributes": True}


class MouvementStockBase(BaseModel):
    type_mouvement: TypeMouvement
    depot_source: str | None = None
    depot_destination: str | None = None
    reference_document: str | None = None
    notes: str | None = None


class MouvementStockCreate(MouvementStockBase):
    lignes: list[LigneMouvementStockCreate]


class MouvementStockRead(MouvementStockBase):
    id: int
    numero: str
    date_mouvement: datetime
    user_id: int | None
    created_at: datetime
    lignes: list[LigneMouvementStockRead] = []
    model_config = {"from_attributes": True}


class LigneInventaireBase(BaseModel):
    article_id: int
    stock_theorique: int = 0
    stock_physique: int = 0
    taille: str | None = None
    couleur: str | None = None


class LigneInventaireCreate(LigneInventaireBase):
    pass


class LigneInventaireRead(LigneInventaireBase):
    id: int
    inventaire_id: int
    ecart: int
    model_config = {"from_attributes": True}


class InventaireBase(BaseModel):
    depot: str
    notes: str | None = None


class InventaireCreate(InventaireBase):
    lignes: list[LigneInventaireCreate] = []


class InventaireRead(InventaireBase):
    id: int
    numero: str
    date_inventaire: datetime
    statut: StatutInventaire
    user_id: int | None
    created_at: datetime
    lignes: list[LigneInventaireRead] = []
    model_config = {"from_attributes": True}
