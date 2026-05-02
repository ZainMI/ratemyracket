from app.services.pipeline_service import run_pipeline_background

if __name__ == "__main__":
    result = run_pipeline_background()
    print(result)
