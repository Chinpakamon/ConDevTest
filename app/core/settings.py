import pydantic
import pydantic_settings


class Settings(pydantic_settings.BaseSettings):
    database_url: str = "postgresql+psycopg://postgres:postgres@db/bookings"
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/1"
    booking_failure_probability: float = pydantic.Field(default=0.15, ge=0, le=1)
    rate_limit_per_minute: int = pydantic.Field(default=30, ge=1)
    debug: bool = False

    model_config = pydantic.ConfigDict(env_file=".env", extra="ignore", env_file_encoding="utf-8")


settings = Settings()
