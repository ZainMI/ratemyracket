import os
from fastapi import APIRouter, BackgroundTasks, Header, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from app.core.config import settings
from app.services.pipeline_service import run_pipeline_background
from app.services.r2_storage import download_r2_prefix, upload_directory_to_r2
from app.services.player_service import clear_player_service_cache
from app.services import match_service

router = APIRouter(prefix="/admin", tags=["admin"])


def verify_admin_secret(x_admin_secret: str | None):
    if not settings.admin_secret_key:
        raise HTTPException(
            status_code=500, detail="Admin secret is not configured."
        )

    if x_admin_secret != settings.admin_secret_key:
        raise HTTPException(status_code=403, detail="Forbidden")


class MatchCreate(BaseModel):
    match_date: str  # e.g. "2024-07-28"
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
            status_code=403, detail="Forbidden: Invalid password."
        )

    # Sync the latest data from R2 first so we append to the most up-to-date files
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
            failed_matches.append({"index": i, "error": str(e)})

    # Upload the updated files back to R2
    upload_result = upload_directory_to_r2(
        local_dir=settings.ml_data_dir,
        prefix=settings.r2_prefix,
    )

    # Automatically trigger the ML pipeline if any matches were successfully added
    pipeline_started = False
    if added_count > 0:
        background_tasks.add_task(run_pipeline_background)
        pipeline_started = True

    return {
        "status": "completed",
        "tournament_name": payload.tournament_name,
        "total_matches_in_payload": len(payload.matches),
        "matches_added": added_count,
        "failed_matches": failed_matches,
        "r2_upload": upload_result,
        "pipeline_started": pipeline_started,
    }
