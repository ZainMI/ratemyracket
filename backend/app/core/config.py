from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "RacketRating API"
    environment: str = "development"

    frontend_url: str = "http://localhost:3000"

    database_url: str = "sqlite:///./racket_rating.db"

    auth_secret_key: str = "change-me"
    auth_algorithm: str = "HS256"

    class Config:
        env_file = ".env"


settings = Settings()
