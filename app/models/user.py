import enum
from datetime import datetime

from sqlalchemy import String, Boolean, DateTime, Enum, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Role(str, enum.Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    COMMERCIAL = "commercial"
    MAGASINIER = "magasinier"
    COMPTABLE = "comptable"
    LECTURE_SEULE = "lecture_seule"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    nom: Mapped[str] = mapped_column(String(100))
    prenom: Mapped[str] = mapped_column(String(100))
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[Role] = mapped_column(Enum(Role), default=Role.LECTURE_SEULE)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
