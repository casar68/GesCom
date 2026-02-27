from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class VRPBase(BaseModel):
    code_vrp: str
    nom: str
    prenom: str | None = None
    telephone: str | None = None
    mobile: str | None = None
    email: str | None = None
    secteur: str | None = None
    departements: str | None = None
    taux_commission: Decimal = Decimal("0")
    objectif_ca: Decimal = Decimal("0")
    user_id: int | None = None
    actif: bool = True


class VRPCreate(VRPBase):
    pass


class VRPUpdate(BaseModel):
    nom: str | None = None
    prenom: str | None = None
    telephone: str | None = None
    mobile: str | None = None
    email: str | None = None
    secteur: str | None = None
    departements: str | None = None
    taux_commission: Decimal | None = None
    objectif_ca: Decimal | None = None
    actif: bool | None = None


class VRPRead(VRPBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


class ConcessionBase(BaseModel):
    code: str
    nom: str
    vrp_id: int | None = None
    adresse: str | None = None
    code_postal: str | None = None
    ville: str | None = None
    telephone: str | None = None
    actif: bool = True


class ConcessionCreate(ConcessionBase):
    pass


class ConcessionRead(ConcessionBase):
    id: int
    model_config = {"from_attributes": True}


class SuiviClientBase(BaseModel):
    client_id: int
    vrp_id: int | None = None
    type_action: str
    description: str | None = None
    date_relance: datetime | None = None


class SuiviClientCreate(SuiviClientBase):
    pass


class SuiviClientRead(SuiviClientBase):
    id: int
    date_action: datetime
    fait: bool
    created_at: datetime
    model_config = {"from_attributes": True}
