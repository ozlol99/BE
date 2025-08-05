from fastapi import FastAPI


from app.apis.v1.kakao_auth_router import router as kakao_auth_router
from app.config.tortoise_config import initialize_tortoise

app = FastAPI()


app.include_router(kakao_auth_router)

initialize_tortoise(app)
