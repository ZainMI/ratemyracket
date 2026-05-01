from fastapi import APIRouter, BackgroundTasks

from app.services.pipeline_service import run_pipeline_background

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/pipeline/run")
def run_pipeline(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_pipeline_background)
    return {"status": "started", "message": "Pipeline started in background."}
