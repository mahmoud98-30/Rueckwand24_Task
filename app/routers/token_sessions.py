from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import TokenSession, User
from app.schemas import TokenSessionOut, TokenSessionUpdate
from app.auth import get_current_user

router = APIRouter(
    tags=["TokenSessions"],
)


@router.get("/", response_model=list[TokenSessionOut])
async def list_token_sessions(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # show sessions for current user only (safer)
    result = await db.execute(
        select(TokenSession).where(TokenSession.user_id == user.id)
    )
    return result.scalars().all()


@router.get("/{session_id}", response_model=TokenSessionOut)
async def get_token_session(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    session = await db.get(TokenSession, session_id)
    if not session or session.user_id != user.id:
        raise HTTPException(status_code=404, detail="Token session not found")
    return session


@router.put("/{session_id}", response_model=TokenSessionOut)
async def update_token_session(
    session_id: int,
    data: TokenSessionUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    session = await db.get(TokenSession, session_id)
    if not session or session.user_id != user.id:
        raise HTTPException(status_code=404, detail="Token session not found")

    if data.revoked is not None:
        session.revoked = data.revoked
    if data.expires_at is not None:
        session.expires_at = data.expires_at

    await db.commit()
    await db.refresh(session)
    return session


@router.delete("/{session_id}")
async def delete_token_session(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    session = await db.get(TokenSession, session_id)
    if not session or session.user_id != user.id:
        raise HTTPException(status_code=404, detail="Token session not found")

    await db.delete(session)
    await db.commit()
    return {"detail": "Token session deleted"}
