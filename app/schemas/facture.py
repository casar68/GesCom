from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from app.models.facture import StatutFacture


class LigneFactureBase(BaseModel):
    article_id: int
    designation: str
    quantite: int = 1
    prix_unitaire_ht: Decimal
    remise_pct: Decimal = Decimal("0")
    tva_pct: Decimal = Decimal("20.00")
    taille: str | None = None
    couleur: str | None = None


class LigneFactureCreate(LigneFactureBase):
    pass


class LigneFactureRead(LigneFactureBase):
    id: int
    facture_id: int
    ligne_numero: int
    montant_ht: Decimal
    model_config = {"from_attributes": True}


class FactureBase(BaseModel):
    client_id: int
    commande_id: int | None = None
    vrp_id: int | None = None
    date_echeance: datetime | None = None
    mode_reglement: str | None = None
    reference_client: str | None = None
    notes: str | None = None
    adresse_facturation: str | None = None
    cp_facturation: str | None = None
    ville_facturation: str | None = None
    remise_globale_pct: Decimal = Decimal("0")


class FactureCreate(FactureBase):
    lignes: list[LigneFactureCreate]


class FactureFromCommande(BaseModel):
    commande_id: int
    mode_reglement: str | None = None
    date_echeance: datetime | None = None


class FactureUpdate(BaseModel):
    date_echeance: datetime | None = None
    mode_reglement: str | None = None
    notes: str | None = None
    remise_globale_pct: Decimal | None = None


class PaiementCreate(BaseModel):
    montant: Decimal
    mode_reglement: str | None = None


class FactureRead(FactureBase):
    id: int
    numero: str
    statut: StatutFacture
    date_facture: datetime
    total_ht: Decimal
    total_tva: Decimal
    total_ttc: Decimal
    montant_regle: Decimal
    created_at: datetime
    updated_at: datetime
    lignes: list[LigneFactureRead] = []
    model_config = {"from_attributes": True}


class FactureList(BaseModel):
    id: int
    numero: str
    client_id: int
    statut: StatutFacture
    date_facture: datetime
    total_ttc: Decimal
    montant_regle: Decimal
    model_config = {"from_attributes": True}
