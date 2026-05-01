from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "RateMyRacket API"
    environment: str = "development"

    app_env: str = "development"
    api_host: str = "127.0.0.1"
    api_port: int = 8000

    frontend_url: str = "http://localhost:3000"
    database_url: str = "sqlite:///./racket_rating.db"

    auth_secret_key: str = "change-me"
    auth_algorithm: str = "HS256"

    ml_data_dir: str = "ml/data"
    model_dir: str = "ml/models/catboost/artifacts/predictor_package"
    inference_state_path: str = "ml/data/inference_state.pkl"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
