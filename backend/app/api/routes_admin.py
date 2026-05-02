from fastapi import APIRouter, BackgroundTasks, Header, HTTPException

from app.core.config import settings
from app.services.pipeline_service import run_pipeline_background
from app.services.r2_storage import download_r2_prefix
from app.services.player_service import clear_player_service_cache

router = APIRouter(prefix="/admin", tags=["admin"])


def verify_admin_secret(x_admin_secret: str | None):
    if not settings.admin_secret_key:
        raise HTTPException(
            status_code=500, detail="Admin secret is not configured."
        )

    if x_admin_secret != settings.admin_secret_key:
        raise HTTPException(status_code=403, detail="Forbidden")


@router.post("/pipeline/run")
def run_pipeline(
    background_tasks: BackgroundTasks,
    x_admin_secret: str | None = Header(default=None),
):
    verify_admin_secret(x_admin_secret)
    background_tasks.add_task(run_pipeline_background)

    return {
        "status": "started",
        "message": "Pipeline started in background.",
    }


@router.post("/refresh-data")
def refresh_data(x_admin_secret: str | None = Header(default=None)):
    verify_admin_secret(x_admin_secret)

    r2_result = download_r2_prefix(
        local_dir=settings.ml_data_dir,
        prefix=settings.r2_prefix,
    )

    clear_player_service_cache()

    return {
        "status": "ok",
        "message": "Data refreshed from R2 and caches cleared.",
        "r2": r2_result,
    }
