from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    AZURE_INFERENCE_ENDPOINT: str
    AZURE_INFERENCE_CREDENTIAL: str
    DB_URL: str
    

    model_config = SettingsConfigDict(env_file='./app/.env', env_file_encoding='utf-8')

settings = Settings()
DB_URL = settings.DB_URL