from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    jwt_secret_key: str = "dev-secret-change-me"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60
    database_mode: str = "sqlite"
    database_path: str = "habit_tracker.db"
    # By default environment variables are case insensitive
    model_config = SettingsConfigDict(
        env_prefix="habit_tracker_",
        env_file=".env",
        env_file_encoding="utf-8",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
