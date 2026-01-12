from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models import ProductType
from app.schemas import ProductTypeCreate, ProductTypeOut, ProductTypeUpdate
from app.auth import get_current_user
from app.models import User

router = APIRouter(tags=["ProductTypes"])



@router.post("/", response_model=ProductTypeOut)
async def create_product_type(
    data: ProductTypeCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    pt = ProductType(**data.dict())
    db.add(pt)

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        # MySQL duplicate key = 1062; but IntegrityError is enough here
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Product type with this name already exists.",
        )

    await db.refresh(pt)
    return pt

@router.get("/", response_model=list[ProductTypeOut])
async def list_product_types(
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(ProductType))
    return result.scalars().all()


@router.get("/{product_type_id}", response_model=ProductTypeOut)
async def get_product_type(
    product_type_id: int,
    db: AsyncSession = Depends(get_db),
):
    pt = await db.get(ProductType, product_type_id)
    if not pt:
        raise HTTPException(404, "Product type not found")
    return pt

@router.put("/{product_type_id}", response_model=ProductTypeOut)
async def update_product_type(
    product_type_id: int,
    data: ProductTypeUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    pt = await db.get(ProductType, product_type_id)
    if not pt:
        raise HTTPException(404, "Product type not found")

    if data.name is not None:
        pt.name = data.name
    if data.description is not None:
        pt.description = data.description

    await db.commit()
    await db.refresh(pt)
    return pt



@router.delete("/{product_type_id}")
async def delete_product_type(
    product_type_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    pt = await db.get(ProductType, product_type_id)
    if not pt:
        raise HTTPException(404, "Product type not found")

    await db.delete(pt)
    await db.commit()

    return {"detail": "Product type deleted successfully"}