from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserOut, UserUpdate
from app.auth import hash_password, get_current_user

router = APIRouter(tags=["Users"])



@router.post("/", response_model=UserOut)
async def create_user(
        data: UserCreate,
        db: AsyncSession = Depends(get_db),
):
    user = User(
        username=data.username,
        email=data.email,
        hashed_password=hash_password(data.password),
    )
    db.add(user)

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email already exists.",
        )

    await db.refresh(user)
    return user

@router.get("/", response_model=list[UserOut])
async def list_users(
        db: AsyncSession = Depends(get_db),
        _: User = Depends(get_current_user),
):
    result = await db.execute(select(User))
    return result.scalars().all()


@router.get("/{user_id}", response_model=UserOut)
async def get_user(
        user_id: int,
        db: AsyncSession = Depends(get_db),
        _: User = Depends(get_current_user),
):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(404, "User not found")
    return user


@router.put("/{user_id}", response_model=UserOut)
async def update_user(
        user_id: int,
        data: UserUpdate,
        db: AsyncSession = Depends(get_db),
        _: User = Depends(get_current_user),
):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(404, "User not found")

    if data.email is not None:
        user.email = data.email

    await db.commit()
    await db.refresh(user)
    return user


@router.delete("/{user_id}")
async def delete_user(
        user_id: int,
        db: AsyncSession = Depends(get_db),
        _: User = Depends(get_current_user),
):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(404, "User not found")

    await db.delete(user)
    await db.commit()

    return {"detail": "User deleted successfully"}
