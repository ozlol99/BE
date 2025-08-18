# import pytest
# from tortoise import Tortoise, run_async
# from tortoise.backends.base.config_generator import generate_config
# from typing import Any
#
# # Pytest가 자동으로 감지할 수 있도록 fixtures 폴더에 conftest.py 파일로 만드세요.
#
# # `settings`와 `TORTOISE_APP_MODELS`는 실제 경로에 맞게 임포트하세요.
# from app.config.settings import settings
# from app.config.tortoise_config import TORTOISE_APP_MODELS
#
#
# def get_test_db_config() -> dict[str, Any]:
#     """
#     테스트용 데이터베이스 연결 설정을 반환합니다.
#     """
#     tortoise_config = generate_config(
#         # 테스트용 DB는 실제 DB와 구분되도록 이름을 다르게 지정하는 것이 안전합니다.
#         db_url=f"mysql://{settings.db_user}:{settings.db_password}@{settings.db_host}:{settings.db_port}/{settings.db_database}_test",
#         # 연결 별칭을 'default'로 설정하는 게 좋습니다.
#         # Tortoise 모델의 기본값과 일치하여 충돌을 피할 수 있습니다.
#         connection_label="default",
#         testing=True,
#         app_modules={"models": TORTOISE_APP_MODELS},
#     )
#     # 필요한 경우 타임존 설정
#     tortoise_config["timezone"] = "Asia/Seoul"
#
#     return tortoise_config
#
#
# @pytest.fixture(scope="session", autouse=True)
# async def initialize_db():
#     """
#     테스트 세션 시작 시 Tortoise ORM을 초기화하고,
#     테스트 세션 종료 시 연결을 닫습니다.
#     """
#
#     await Tortoise.init(config=get_test_db_config())
#     # 모든 모델에 대한 스키마 생성
#     await Tortoise.generate_schemas()
#
#
#     yield
#
#
#     await Tortoise.close_connections()
#
#
# @pytest.fixture(scope="function", autouse=True)
# async def clear_database():
#     """
#     각 테스트 함수가 실행된 후 데이터베이스를 비웁니다.
#     """
#     yield
#     # 각 테스트가 끝난 후 모든 테이블을 비워 다음 테스트가 깨끗한 상태에서 시작하도록 합니다.
#     for app in Tortoise.apps.values():
#         for model in app.values():
#             await model.all().delete()