from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Text, Boolean
from sqlalchemy.orm import relationship

from app.database import Base  # ✅ use the same Base everywhere


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    sessions = relationship("TokenSession", back_populates="user")


class TokenSession(Base):
    __tablename__ = "token_sessions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    revoked = Column(Boolean, default=False)
    user = relationship("User", back_populates="sessions")


class Material(Base):
    __tablename__ = "materials"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    items = relationship("Item", back_populates="material")


class ProductType(Base):
    __tablename__ = "product_types"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    items = relationship("Item", back_populates="product_type")


class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    material_id = Column(Integer, ForeignKey("materials.id"), nullable=False)
    product_type_id = Column(Integer, ForeignKey("product_types.id"), nullable=False)
    width = Column(Float, nullable=False)
    height = Column(Float, nullable=False)
    pdf_path = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    material = relationship("Material", back_populates="items")
    product_type = relationship("ProductType", back_populates="items")
