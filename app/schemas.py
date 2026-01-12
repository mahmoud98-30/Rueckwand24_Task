from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import Optional


# ------------------- USER -------------------

class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: Optional[str] = None


class UserOut(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        orm_mode = True


class TokenOut(BaseModel):
    access_token: str
    token_type: str


# ------------------- TOKEN SESSION -------------------

class TokenSessionOut(BaseModel):
    id: int
    user_id: int
    token: str
    revoked: bool
    created_at: datetime
    expires_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class TokenSessionBase(BaseModel):
    token: str
    expires_at: Optional[datetime]


class TokenSessionCreate(TokenSessionBase):
    user_id: int


class TokenSessionUpdate(BaseModel):
    revoked: Optional[bool] = None
    expires_at: Optional[datetime] = None


# ------------------- MATERIAL -------------------

class MaterialBase(BaseModel):
    name: str
    description: Optional[str] = None


class MaterialCreate(MaterialBase):
    pass


class MaterialOut(MaterialBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


class MaterialUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


# ------------------- PRODUCT TYPE -------------------

class ProductTypeBase(BaseModel):
    name: str
    description: Optional[str] = None


class ProductTypeCreate(ProductTypeBase):
    pass


class ProductTypeOut(ProductTypeBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


class ProductTypeUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


# ------------------- ITEM -------------------

class ItemBase(BaseModel):
    material_id: int
    product_type_id: int
    width: float
    height: float


class ItemCreate(ItemBase):
    pass


class ItemUpdate(BaseModel):
    material_id: Optional[int] = None
    product_type_id: Optional[int] = None
    width: Optional[float] = None
    height: Optional[float] = None


class ItemOut(ItemBase):
    id: int
    pdf_path: Optional[str] = None
    created_at: datetime

    class Config:
        orm_mode = True
