from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.auth.schemas import LoginRequest, Token, UserCreate, UserRead
from app.auth.service import authenticate_user, create_access_token, create_user, get_user_by_email
from app.auth.dependencies import get_current_user, require_roles
from app.models.user import Role, User

router = APIRouter()


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(data: UserCreate, db: AsyncSession = Depends(get_db)):
    existing = await get_user_by_email(db, data.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email déjà utilisé")
    user = await create_user(db, data.email, data.nom, data.prenom, data.password, data.role)
    return user


@router.post("/login", response_model=Token)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, data.email, data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email ou mot de passe incorrect")
    token = create_access_token({"sub": str(user.id), "role": user.role.value})
    return Token(access_token=token)


@router.get("/me", response_model=UserRead)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/users", response_model=list[UserRead])
async def list_users(
    _admin: User = Depends(require_roles(Role.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    from sqlalchemy import select

    result = await db.execute(select(User).order_by(User.nom))
    return list(result.scalars().all())
