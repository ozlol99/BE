from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Annotated


class Settings(BaseSettings):
    db_host: str
    db_user: str
    db_password: str
    db_database: str
    db_port: int

    kakao_rest_api_key: str

    google_client_id: str
    google_client_secret: str
    google_redirect_uri: str

    secret_key: str
    algorithm: str

    access_token_expire_minutes: int
    refresh_token_expire_days: int

    riot_api_key: str
    riot_txt: str = Field(alias="riot.txt")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    base_url: str

settings = Settings()
