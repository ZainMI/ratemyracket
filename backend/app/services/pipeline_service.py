import os
import requests

from ml.pipeline import run_pipeline
from app.core.config import settings
from app.services.r2_storage import upload_directory_to_r2, download_r2_prefix


def notify_api_refresh():
    # Call the refresh function directly instead of an HTTP request.
    # This works reliably on Railway without needing API_PUBLIC_URL.
    from app.api.routes_admin import refresh_data

    try:
        return refresh_data(x_admin_secret=settings.admin_secret_key)
    except Exception as e:
        print(f"Failed to refresh API locally: {e}")
        return {"status": "error", "reason": str(e)}


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
