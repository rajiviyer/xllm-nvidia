from pydantic_settings import BaseSettings, SettingsConfigDict
import os


class Settings(BaseSettings):
    DB_URL: str
    LLM_ENDPOINT: str
    LLM_MODEL: str
    LLM_TEMPERATURE: float
    LLM_TOP_P: float

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(__file__), ".env"),
        env_file_encoding="utf-8",
    )


settings = Settings()
DB_URL = settings.DB_URL
LLM_ENDPOINT = settings.LLM_ENDPOINT
LLM_MODEL = settings.LLM_MODEL
LLM_TEMPERATURE = settings.LLM_TEMPERATURE
LLM_TOP_P = settings.LLM_TOP_P
