import os
import requests

from ml.pipeline import run_pipeline
from app.core.config import settings
from app.services.r2_storage import upload_directory_to_r2, download_r2_prefix


def notify_api_refresh():
    api_url = os.getenv("API_PUBLIC_URL", "").rstrip("/")

    if not api_url:
        print("API_PUBLIC_URL not configured; skipping API refresh.")
        return {
            "status": "skipped",
            "reason": "API_PUBLIC_URL not configured.",
        }

    if not settings.admin_secret_key:
        print("ADMIN_SECRET_KEY not configured; skipping API refresh.")
        return {
            "status": "skipped",
            "reason": "ADMIN_SECRET_KEY not configured.",
        }

    url = f"{api_url}/admin/refresh-data"

    response = requests.post(
        url,
        headers={"x-admin-secret": settings.admin_secret_key},
        timeout=120,
    )

    response.raise_for_status()
    return response.json()


def run_pipeline_background():
    # 1. Sync latest data from R2 first to ensure added_data.csv is up to date
    download_result = download_r2_prefix(
        local_dir=settings.ml_data_dir,
        prefix=settings.r2_prefix,
    )
    print("R2 download finished:", download_result)

    result = run_pipeline(
        full_backfill=False,
        retrain=True,
    )

    print("Pipeline finished:", result)

    upload_result = upload_directory_to_r2(
        local_dir=settings.ml_data_dir,
        prefix=settings.r2_prefix,
    )

    print("R2 upload finished:", upload_result)

    refresh_result = notify_api_refresh()

    print("API refresh finished:", refresh_result)

    return {
        "r2_download": download_result,
        "pipeline": result,
        "r2_upload": upload_result,
        "api_refresh": refresh_result,
    }
