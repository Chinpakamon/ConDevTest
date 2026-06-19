import pydantic
import pydantic_settings


class Settings(pydantic_settings.BaseSettings):
    # Database
    database_url: pydantic.PostgresDsn

    model_config = pydantic.ConfigDict(
        env_file=".env", extra="ignore", env_file_encoding="utf-8"
    )


settings = Settings()