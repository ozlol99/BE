from contextlib import asynccontextmanager

from fastapi import FastAPI
from tortoise import Tortoise

from app.apis.v1.kakao_auth_router import router as kakao_auth_router
from app.apis.v1.user_router import router as user_router
from app.config.tortoise_config import initialize_tortoise


# lifespan 컨텍스트 매니저 정의
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application startup...")
    # 🚨 DB 연결 초기화 및 스키마 생성
    await Tortoise.generate_schemas()  # 🚨 스키마 생성만 호출

    print("Database schemas generated!")

    yield

    # 🚨 애플리케이션 종료 시 DB 연결 해제 (선택 사항)
    print("Application shutdown...")
    await Tortoise.close_connections()


app = FastAPI(lifespan=lifespan)


app.include_router(kakao_auth_router)
app.include_router(user_router)

initialize_tortoise(app)
