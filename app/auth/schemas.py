from pydantic import BaseModel, EmailStr

from app.models.user import Role


class UserCreate(BaseModel):
    email: EmailStr
    nom: str
    prenom: str
    password: str
    role: Role = Role.LECTURE_SEULE


class UserRead(BaseModel):
    id: int
    email: str
    nom: str
    prenom: str
    role: Role
    is_active: bool

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    nom: str | None = None
    prenom: str | None = None
    role: Role | None = None
    is_active: bool | None = None


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: int | None = None
    role: Role | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
