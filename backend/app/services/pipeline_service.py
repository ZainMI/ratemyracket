import requests

from ml.pipeline import run_pipeline
from app.core.config import settings
from app.services.r2_storage import upload_directory_to_r2, download_r2_prefix


def notify_api_refresh():
    try:
        response = requests.post(
            f"{settings.api_public_url.rstrip('/')}/admin/refresh-data",
            headers={
                "x-admin-secret": settings.admin_secret_key,
            },
            timeout=60,
        )

        response.raise_for_status()
        return response.json()

    except Exception as e:
        print(f"Failed to refresh API: {e}")
        return {
            "status": "error",
            "reason": str(e),
        }


def run_pipeline_background():
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
