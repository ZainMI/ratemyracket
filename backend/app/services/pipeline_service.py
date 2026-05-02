from backend.app.services.r2_storage import upload_directory_to_r2
from ml.pipeline import run_pipeline
from app.core.config import settings


def run_pipeline_background():
    result = run_pipeline()

    print("Pipeline finished:", result)

    upload_result = upload_directory_to_r2(
        local_dir=settings.ml_data_dir,
        prefix=settings.r2_prefix,
    )

    print("R2 upload:", upload_result)
