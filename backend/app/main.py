import os
from contextlib import asynccontextmanager
from pathlib import Path

# Load .env from backend root before any imports that read env vars
_env = Path(__file__).resolve().parents[1] / ".env"
if _env.exists():
    from dotenv import load_dotenv
    load_dotenv(_env, override=False)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.auth import router as auth_router
from app.routes.companies import router as companies_router
from app.routes.catalog import router as catalog_router
from app.routes.marketplace import router as marketplace_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.core.db import SessionLocal, init_db
    from app.core.seed import run_seed
    init_db()
    
    # Executa seed apenas se explicitamente solicitado ou em dev
    if os.getenv("SEED_ON_STARTUP", "true").lower() == "true":
        db = SessionLocal()
        try:
            run_seed(db)
        finally:
            db.close()
    yield


_debug = os.getenv("DEBUG", "true").lower() == "true"

app = FastAPI(
    title="App de Moda - Polo do Agreste PE", 
    version="0.5.0", 
    lifespan=lifespan,
    docs_url="/docs" if _debug else None,
    redoc_url="/redoc" if _debug else None,
)

_raw_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:3001")
_origins = [o.strip() for o in _raw_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "PUT", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)

app.include_router(auth_router, prefix="/api")
app.include_router(companies_router, prefix="/api")
app.include_router(catalog_router, prefix="/api")
app.include_router(marketplace_router, prefix="/api")


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "version": "0.5.0"}
