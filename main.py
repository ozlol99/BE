from fastapi import FastAPI

from app.apis.test import router as test_router
from app.apis.v1.kakao_auth_router import router as kakao_auth_router
from app.config.tortoise_config import initialize_tortoise

app = FastAPI()

app.include_router(test_router)
app.include_router(kakao_auth_router)

initialize_tortoise(app)
