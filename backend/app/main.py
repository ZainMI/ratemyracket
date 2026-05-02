import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Routes
from app.api.routes_health import router as health_router
from app.api.routes_players import router as players_router
from app.api.routes_predict import router as predict_router
from app.api.routes_favorites import router as favorites_router
from app.api.routes_admin import router as admin_router

# Core / DB
from app.db.session import init_db

# ML
from app.services.predictor_service import ensure_model_loaded
from app.core.config import get_allowed_origins, settings
from app.services.r2_storage import download_r2_prefix

# -------------------------------------------------
# App init
# -------------------------------------------------
app = FastAPI(
    title="RacketRating API",
    description="Racketlon match prediction service",
    version="1.0.0",
)

# -------------------------------------------------
# Middleware (CORS for frontend)
# -------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------------------------------
# Startup logic
# -------------------------------------------------
@app.on_event("startup")
def startup():
    print("Starting API...")

    # Initialize database tables
    init_db()

    download_r2_prefix(
        local_dir=settings.ml_data_dir,
        prefix="",
    )

    # Load ML model into memory
    ensure_model_loaded()

    print("API ready.")


# -------------------------------------------------
# Root
# -------------------------------------------------
@app.get("/")
def root():
    return {
        "message": "RacketRating API",
        "status": "running",
    }


# -------------------------------------------------
# Register routes
# -------------------------------------------------
app.include_router(health_router)
app.include_router(players_router)
app.include_router(predict_router)
app.include_router(favorites_router)
app.include_router(admin_router)
