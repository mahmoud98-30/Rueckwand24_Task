from fastapi import FastAPI
from fastapi.security import HTTPBearer
from contextlib import asynccontextmanager
import uvicorn

from app.database import engine, Base
from app.routers import auth, users, materials, product_types, items, token_sessions
import app.models

security = HTTPBearer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # shutdown
    await engine.dispose()

app = FastAPI(
    title="Backend Test Task API",
    description="FastAPI + MySQL with JWT Authentication",
    version="1.0.0",
    lifespan=lifespan,
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(materials.router, prefix="/api/materials", tags=["Materials"])
app.include_router(product_types.router, prefix="/api/product-types", tags=["Product Types"])
app.include_router(items.router, prefix="/api/items", tags=["Items"])
app.include_router(token_sessions.router,prefix="/api/token-sessions", tags=["TokenSessions"]
)

@app.get("/")
async def root():
    return {
        "message": "Backend Test Task API",
        "docs": "/docs",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)