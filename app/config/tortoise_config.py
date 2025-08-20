from fastapi import FastAPI
from tortoise import Tortoise
from tortoise.contrib.fastapi import register_tortoise

from app.config.settings import Settings

settings = Settings()


# TortoiseORM DB URL
DATABASE_URL = (
    f"mysql://{settings.db_user}:{settings.db_password}@"
    f"{settings.db_host}:{settings.db_port}/{settings.db_database}"
)


TORTOISE_APP_MODELS: list[str] = [
    "aerich.models",
    "app.models.user",
    "app.models.token_blacklist",
    "app.models.refresh_token",
    "app.models.search_summoner",
    "app.models.chat_room",
    "app.models.hash_tag",
    "app.models.riot_account",
    "app.models.chat_room_participant",
]

TORTOISE_ORM = {
    "connections": {
        "default": DATABASE_URL,
    },
    "apps": {
        "models": {
            "models": TORTOISE_APP_MODELS,
            "default_connection": "default",
        }
    },
}


def initialize_tortoise(app: FastAPI) -> None:
    Tortoise.init_models(TORTOISE_APP_MODELS, "models")
    register_tortoise(
        app,
        config=TORTOISE_ORM,
        generate_schemas=True,
    )
