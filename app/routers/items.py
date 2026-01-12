from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models import Item
from app.schemas import ItemCreate, ItemOut, ItemUpdate
from app.auth import get_current_user
from app.models import User

router = APIRouter(tags=["Items"])


@router.post("/", response_model=ItemOut)
async def create_item(
        data: ItemCreate,
        db: AsyncSession = Depends(get_db),
        _: User = Depends(get_current_user),
):
    item = Item(**data.dict())
    db.add(item)

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid material_id or product_type_id (foreign key constraint).",
        )

    await db.refresh(item)
    return item


@router.get("/", response_model=list[ItemOut])
async def list_items(
        db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Item))
    return result.scalars().all()


@router.get("/{item_id}", response_model=ItemOut)
async def get_item(
        item_id: int,
        db: AsyncSession = Depends(get_db),
):
    item = await db.get(Item, item_id)
    if not item:
        raise HTTPException(404, "Item not found")
    return item


@router.put("/{item_id}", response_model=ItemOut)
async def update_item(
        item_id: int,
        data: ItemUpdate,
        db: AsyncSession = Depends(get_db),
        _: User = Depends(get_current_user),
):
    item = await db.get(Item, item_id)
    if not item:
        raise HTTPException(404, "Item not found")

    if data.material_id is not None:
        item.material_id = data.material_id
    if data.product_type_id is not None:
        item.product_type_id = data.product_type_id
    if data.width is not None:
        item.width = data.width
    if data.height is not None:
        item.height = data.height

    await db.commit()
    await db.refresh(item)
    return item


@router.delete("/{item_id}")
async def delete_item(
        item_id: int,
        db: AsyncSession = Depends(get_db),
        _: User = Depends(get_current_user),
):
    item = await db.get(Item, item_id)
    if not item:
        raise HTTPException(404, "Item not found")

    await db.delete(item)
    await db.commit()

    return {"detail": "Item deleted successfully"}
