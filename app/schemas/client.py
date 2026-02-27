from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class ContactClientBase(BaseModel):
    nom: str
    prenom: str | None = None
    fonction: str | None = None
    telephone: str | None = None
    mobile: str | None = None
    email: str | None = None
    principal: bool = False


class ContactClientCreate(ContactClientBase):
    pass


class ContactClientRead(ContactClientBase):
    id: int
    client_id: int
    model_config = {"from_attributes": True}


class AdresseClientBase(BaseModel):
    type_adresse: str = "livraison"
    adresse: str
    complement: str | None = None
    code_postal: str
    ville: str
    pays: str = "France"
    par_defaut: bool = False


class AdresseClientCreate(AdresseClientBase):
    pass


class AdresseClientRead(AdresseClientBase):
    id: int
    client_id: int
    model_config = {"from_attributes": True}


class ClientBase(BaseModel):
    code_client: str
    raison_sociale: str
    type_client: str = "standard"
    siret: str | None = None
    tva_intra: str | None = None
    telephone: str | None = None
    fax: str | None = None
    email: str | None = None
    site_web: str | None = None
    adresse: str | None = None
    complement_adresse: str | None = None
    code_postal: str | None = None
    ville: str | None = None
    pays: str = "France"
    vrp_id: int | None = None
    concession_id: int | None = None
    encours_max: Decimal = Decimal("0")
    mode_reglement: str | None = None
    delai_reglement: int = 30
    notes: str | None = None
    actif: bool = True


class ClientCreate(ClientBase):
    contacts: list[ContactClientCreate] = []
    adresses: list[AdresseClientCreate] = []


class ClientUpdate(BaseModel):
    raison_sociale: str | None = None
    type_client: str | None = None
    siret: str | None = None
    tva_intra: str | None = None
    telephone: str | None = None
    fax: str | None = None
    email: str | None = None
    site_web: str | None = None
    adresse: str | None = None
    complement_adresse: str | None = None
    code_postal: str | None = None
    ville: str | None = None
    pays: str | None = None
    vrp_id: int | None = None
    concession_id: int | None = None
    encours_max: Decimal | None = None
    mode_reglement: str | None = None
    delai_reglement: int | None = None
    notes: str | None = None
    actif: bool | None = None


class ClientRead(ClientBase):
    id: int
    created_at: datetime
    updated_at: datetime
    contacts: list[ContactClientRead] = []
    adresses: list[AdresseClientRead] = []
    model_config = {"from_attributes": True}


class ClientList(BaseModel):
    id: int
    code_client: str
    raison_sociale: str
    type_client: str
    ville: str | None
    telephone: str | None
    email: str | None
    actif: bool
    model_config = {"from_attributes": True}
