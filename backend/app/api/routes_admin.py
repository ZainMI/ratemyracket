import os
import traceback
from fastapi import APIRouter, BackgroundTasks, Header, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from app.core.config import settings
from app.services.pipeline_service import run_pipeline_background
from app.services.r2_storage import download_r2_prefix, upload_directory_to_r2
from app.services.player_service import clear_player_service_cache
from app.services import match_service
from app.services import predictor_service

router = APIRouter(prefix="/admin", tags=["admin"])


def verify_admin_secret(x_admin_secret: str | None):
    if not settings.admin_secret_key:
        raise HTTPException(
            status_code=500,
            detail="Admin secret is not configured.",
        )

    if x_admin_secret != settings.admin_secret_key:
        raise HTTPException(status_code=403, detail="Forbidden")


class MatchCreate(BaseModel):
    match_date: str
    match_time: str = ""
    draw: str
    draw_id: Optional[float] = None
    round_name: str = ""
    p1_first_name: str
    p1_last_name: str
    p1_country: str
    p2_first_name: str
    p2_last_name: str
    p2_country: str
    tt_p1: Optional[int] = None
    tt_p2: Optional[int] = None
    bd_p1: Optional[int] = None
    bd_p2: Optional[int] = None
    sq_p1: Optional[int] = None
    sq_p2: Optional[int] = None
    tn_p1: Optional[int] = None
    tn_p2: Optional[int] = None
    winner_side: Optional[float] = None
    duration: str = ""
    location: str = ""
    status_message: str = ""
    h2h_url: str = ""
    team1_player_ids: str = ""
    team2_player_ids: str = ""
    team1_club_ids: str = ""
    team2_club_ids: str = ""


class BulkMatchesCreate(BaseModel):
    tournament_name: str
    matches: List[MatchCreate]


def process_bulk_matches_background(payload: BulkMatchesCreate):
    try:
        download_r2_prefix(
            local_dir=settings.ml_data_dir,
            prefix=settings.r2_prefix,
        )

        added_count = 0
        failed_matches = []

        for i, match_data in enumerate(payload.matches):
            try:
                match_service.add_match(
                    tournament_name=payload.tournament_name,
                    **match_data.model_dump(),
                )
                added_count += 1
            except Exception as e:
                failed_matches.append(
                    {
                        "index": i,
                        "error": str(e),
                    }
                )

        upload_directory_to_r2(
            local_dir=settings.ml_data_dir,
            prefix=settings.r2_prefix,
        )

        print(
            {
                "status": "bulk_match_background_complete",
                "tournament_name": payload.tournament_name,
                "added_count": added_count,
                "failed_matches": failed_matches,
            }
        )

    except Exception:
        print("Bulk match background job failed:")
        traceback.print_exc()


def process_delete_match_background(match_id: str):
    try:
        download_r2_prefix(
            local_dir=settings.ml_data_dir,
            prefix=settings.r2_prefix,
        )

        match_service.delete_match(match_id)

        upload_directory_to_r2(
            local_dir=settings.ml_data_dir,
            prefix=settings.r2_prefix,
        )

        print(
            {"status": "delete_match_background_complete", "match_id": match_id}
        )

    except Exception:
        print("Delete match background job failed:")
        traceback.print_exc()


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

    # Force reload the machine learning model and inference state into memory
    if hasattr(predictor_service, "reload_model"):
        predictor_service.reload_model()
    else:
        # Fallback: Clear standard global variables and reload
        predictor_service._predictor = None
        predictor_service._inference_state = None
        predictor_service.ensure_model_loaded()

    return {
        "status": "ok",
        "message": "Data refreshed from R2 and caches cleared.",
        "r2": r2_result,
    }


@router.post("/matches/bulk")
def add_bulk_matches(
    payload: BulkMatchesCreate,
    background_tasks: BackgroundTasks,
    x_admin_secret: str | None = Header(default=None),
    x_upload_password: str | None = Header(default=None),
):
    upload_pw = os.getenv("UPLOAD_PASSWORD")

    is_admin = bool(
        settings.admin_secret_key
        and x_admin_secret == settings.admin_secret_key
    )

    is_uploader = bool(upload_pw and x_upload_password == upload_pw)

    if not (is_admin or is_uploader):
        raise HTTPException(
            status_code=403,
            detail="Forbidden: Invalid password.",
        )

    background_tasks.add_task(
        process_bulk_matches_background,
        payload,
    )

    return {
        "status": "started",
        "tournament_name": payload.tournament_name,
        "total_matches_in_payload": len(payload.matches),
        "message": "Matches are being processed in the background.",
    }


@router.get("/matches/search")
def search_matches(
    player_name: str,
    x_admin_secret: str | None = Header(default=None),
    x_delete_password: str | None = Header(default=None),
):
    delete_pw = os.getenv("DELETE_PASSWORD")
    is_admin = bool(
        settings.admin_secret_key
        and x_admin_secret == settings.admin_secret_key
    )

    # Strip whitespace to prevent copy-paste errors
    is_deleter = bool(
        delete_pw
        and x_delete_password
        and x_delete_password.strip() == delete_pw.strip()
    )

    if not (is_admin or is_deleter):
        if not delete_pw:
            raise HTTPException(
                status_code=403,
                detail="Server Error: DELETE_PASSWORD env variable is missing.",
            )
        if not x_delete_password:
            raise HTTPException(
                status_code=403,
                detail="Forbidden: x-delete-password header was not received by the server.",
            )
        raise HTTPException(
            status_code=403, detail="Forbidden: Incorrect Delete Password."
        )

    return match_service.search_matches(player_name)


@router.delete("/matches/{match_id}")
def delete_match(
    match_id: str,
    background_tasks: BackgroundTasks,
    x_admin_secret: str | None = Header(default=None),
    x_delete_password: str | None = Header(default=None),
):
    delete_pw = os.getenv("DELETE_PASSWORD")
    is_admin = bool(
        settings.admin_secret_key
        and x_admin_secret == settings.admin_secret_key
    )

    is_deleter = bool(
        delete_pw
        and x_delete_password
        and x_delete_password.strip() == delete_pw.strip()
    )

    if not (is_admin or is_deleter):
        if not delete_pw:
            raise HTTPException(
                status_code=403,
                detail="Server Error: DELETE_PASSWORD env variable is missing.",
            )
        if not x_delete_password:
            raise HTTPException(
                status_code=403,
                detail="Forbidden: x-delete-password header was not received by the server.",
            )
        raise HTTPException(
            status_code=403, detail="Forbidden: Incorrect Delete Password."
        )

    background_tasks.add_task(process_delete_match_background, match_id)

    return {
        "status": "started",
        "message": f"Match {match_id} deletion started in the background.",
    }
