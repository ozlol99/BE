from contextlib import asynccontextmanager
from fastapi import FastAPI
from tortoise import Tortoise

from app.apis.v1.google_auth_router import router as google_auth_router
from app.apis.v1.kakao_auth_router import router as kakao_auth_router
from app.apis.v1.user_router import router as user_router
from app.apis.v1.riot_routes import router as riot_router
from app.config.tortoise_config import TORTOISE_ORM


# lifespan 컨텍스트 매니저 정의
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await Tortoise.init(config=TORTOISE_ORM)
        # 개발 환경에서만 스키마 자동 생성을 사용합니다.
        await Tortoise.generate_schemas()
        print("Tortoise ORM initialized and schemas generated.")
    except Exception as e:
        print(f"Error initializing Tortoise: {e}")
        # 오류 발생 시 애플리케이션 종료를 위해 예외를 다시 발생시킵니다.
        raise

    yield

    print("Application shutdown...")
    await Tortoise.close_connections()


app = FastAPI(lifespan=lifespan)


app.include_router(kakao_auth_router)
app.include_router(google_auth_router)
app.include_router(user_router)
app.include_router(riot_router)


