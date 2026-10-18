from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "RateMyRacket API"
    environment: str = "development"

    app_env: str = "development"
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    api_public_url: str = "http://127.0.0.1:8000"

    frontend_url: str = "http://localhost:3000"
    frontend_urls: str = ""

    auth_secret_key: str = "change-me"
    auth_algorithm: str = "HS256"

    ml_data_dir: str = "ml/data"
    model_dir: str = "ml/models/catboost/artifacts/predictor_package"
    inference_state_path: str = "ml/data/inference_state.pkl"

    # R2 configuration
    r2_access_key_id: str = ""
    r2_secret_access_key: str = ""
    r2_bucket: str = "data"
    r2_endpoint_url: str = ""
    r2_prefix: str = ""

    admin_secret_key: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()


def get_allowed_origins() -> list[str]:
    origins = set()

    if settings.frontend_url:
        origins.add(settings.frontend_url.strip())

    if settings.frontend_urls:
        for url in settings.frontend_urls.split(","):
            url = url.strip()
            if url:
                origins.add(url)

    if settings.app_env != "production":
        origins.add("http://localhost:3000")
        origins.add("http://127.0.0.1:3000")

    return sorted(origins)
