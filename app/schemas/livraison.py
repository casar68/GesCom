from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from app.models.livraison import StatutLivraison


class LigneBonLivraisonBase(BaseModel):
    article_id: int
    designation: str
    quantite: int = 1
    taille: str | None = None
    couleur: str | None = None
    emplacement: str | None = None


class LigneBonLivraisonCreate(LigneBonLivraisonBase):
    pass


class LigneBonLivraisonRead(LigneBonLivraisonBase):
    id: int
    bon_livraison_id: int
    ligne_numero: int
    model_config = {"from_attributes": True}


class BonLivraisonBase(BaseModel):
    client_id: int
    commande_id: int | None = None
    vrp_id: int | None = None
    transport_id: int | None = None
    adresse_livraison: str | None = None
    cp_livraison: str | None = None
    ville_livraison: str | None = None
    pays_livraison: str = "France"
    poids_total: Decimal = Decimal("0")
    nb_colis: int = 0
    notes: str | None = None


class BonLivraisonCreate(BonLivraisonBase):
    lignes: list[LigneBonLivraisonCreate]


class BonLivraisonFromCommande(BaseModel):
    commande_id: int
    transport_id: int | None = None


class BonLivraisonRead(BonLivraisonBase):
    id: int
    numero: str
    statut: StatutLivraison
    date_bl: datetime
    date_expedition: datetime | None
    date_livraison: datetime | None
    created_at: datetime
    lignes: list[LigneBonLivraisonRead] = []
    model_config = {"from_attributes": True}


class BonLivraisonList(BaseModel):
    id: int
    numero: str
    client_id: int
    commande_id: int | None
    statut: StatutLivraison
    date_bl: datetime
    nb_colis: int
    model_config = {"from_attributes": True}
