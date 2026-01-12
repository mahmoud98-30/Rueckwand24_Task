from fastapi import APIRouter, Depends, HTTPException ,status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models import Material
from app.schemas import MaterialCreate, MaterialOut, MaterialUpdate
from app.auth import get_current_user
from app.models import User

router = APIRouter(tags=["Materials"])


@router.post("/", response_model=MaterialOut)
async def create_material(
        data: MaterialCreate,
        db: AsyncSession = Depends(get_db),
        _: User = Depends(get_current_user),
):
    material = Material(**data.dict())
    db.add(material)

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Material with this name already exists.",
        )

    await db.refresh(material)
    return material

@router.get("/", response_model=list[MaterialOut])
async def list_materials(
        db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Material))
    return result.scalars().all()


@router.get("/{material_id}", response_model=MaterialOut)
async def get_material(
        material_id: int,
        db: AsyncSession = Depends(get_db),
):
    material = await db.get(Material, material_id)
    if not material:
        raise HTTPException(404, "Material not found")
    return material


@router.put("/{material_id}", response_model=MaterialOut)
async def update_material(
        material_id: int,
        data: MaterialUpdate,
        db: AsyncSession = Depends(get_db),
        _: User = Depends(get_current_user),
):
    material = await db.get(Material, material_id)
    if not material:
        raise HTTPException(404, "Material not found")

    if data.name is not None:
        material.name = data.name
    if data.description is not None:
        material.description = data.description

    await db.commit()
    await db.refresh(material)
    return material


@router.delete("/{material_id}")
async def delete_material(
        material_id: int,
        db: AsyncSession = Depends(get_db),
        _: User = Depends(get_current_user),
):
    material = await db.get(Material, material_id)
    if not material:
        raise HTTPException(404, "Material not found")

    await db.delete(material)
    await db.commit()

    return {"detail": "Material deleted successfully"}
