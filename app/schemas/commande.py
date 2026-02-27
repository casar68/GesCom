from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from app.models.commande import StatutCommande


class LigneCommandeBase(BaseModel):
    article_id: int
    designation: str
    quantite: int = 1
    prix_unitaire_ht: Decimal
    remise_pct: Decimal = Decimal("0")
    tva_pct: Decimal = Decimal("20.00")
    taille: str | None = None
    couleur: str | None = None


class LigneCommandeCreate(LigneCommandeBase):
    pass


class LigneCommandeRead(LigneCommandeBase):
    id: int
    commande_id: int
    ligne_numero: int
    quantite_livree: int
    montant_ht: Decimal
    model_config = {"from_attributes": True}


class CommandeBase(BaseModel):
    client_id: int
    vrp_id: int | None = None
    date_livraison_souhaitee: datetime | None = None
    reference_client: str | None = None
    notes: str | None = None
    adresse_livraison: str | None = None
    cp_livraison: str | None = None
    ville_livraison: str | None = None
    pays_livraison: str = "France"
    remise_globale_pct: Decimal = Decimal("0")


class CommandeCreate(CommandeBase):
    lignes: list[LigneCommandeCreate]


class CommandeUpdate(BaseModel):
    vrp_id: int | None = None
    date_livraison_souhaitee: datetime | None = None
    reference_client: str | None = None
    notes: str | None = None
    adresse_livraison: str | None = None
    cp_livraison: str | None = None
    ville_livraison: str | None = None
    remise_globale_pct: Decimal | None = None


class CommandeRead(CommandeBase):
    id: int
    numero: str
    statut: StatutCommande
    date_commande: datetime
    total_ht: Decimal
    total_tva: Decimal
    total_ttc: Decimal
    created_at: datetime
    updated_at: datetime
    lignes: list[LigneCommandeRead] = []
    model_config = {"from_attributes": True}


class CommandeList(BaseModel):
    id: int
    numero: str
    client_id: int
    statut: StatutCommande
    date_commande: datetime
    total_ttc: Decimal
    model_config = {"from_attributes": True}
