from datetime import datetime, timedelta
from typing import Optional

from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import User, TokenSession

import os

# ================= CONFIG =================

SECRET_KEY = os.getenv("JWT_SECRET",)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ================= PASSWORD =================

def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

# ================= JWT =================

def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
) -> tuple[str, datetime]:
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt, expire

# ================= AUTH CORE =================

async def authenticate_user(
    db: AsyncSession,
    username: str,
    password: str,
) -> Optional[User]:
    result = await db.execute(
        select(User).where(User.username == username)
    )
    user = result.scalar_one_or_none()

    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    if not user.is_active:
        return None

    return user


async def create_token_session(
    db: AsyncSession,
    user: User,
) -> str:
    token, expires_at = create_access_token({"sub": str(user.id)})

    session = TokenSession(
        user_id=user.id,
        token=token,
        expires_at=expires_at,
        revoked=False,
    )

    db.add(session)
    await db.commit()

    return token

# ================= DEPENDENCY =================

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Check token session (VERY IMPORTANT)
    result = await db.execute(
        select(TokenSession).where(
            TokenSession.token == token,
            TokenSession.revoked == False,
            TokenSession.expires_at > datetime.utcnow(),
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise credentials_exception

    result = await db.execute(
        select(User).where(User.id == int(user_id))
    )
    user = result.scalar_one_or_none()
    if not user:
        raise credentials_exception

    return user

# ================= LOGOUT =================

async def revoke_token(
    token: str,
    db: AsyncSession,
) -> None:
    result = await db.execute(
        select(TokenSession).where(TokenSession.token == token)
    )
    session = result.scalar_one_or_none()
    if session:
        session.revoked = True
        await db.commit()
