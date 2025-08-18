# import pytest
# import httpx
# from httpx import ASGITransport
# from asgi import app
# from app.models.user import UserModel
# from app.models.refresh_token import RefreshTokenModel  # RefreshTokenModel 임포트
#
#
# @pytest.mark.asyncio
# async def test_kakao_login_user_exists(mocker):
#     """
#     DB에 유저가 이미 존재하는 경우를 테스트합니다.
#     - 200 OK와 함께 토큰 및 리디렉션 URL이 반환되는지 확인합니다.
#     """
#     # 1. 외부 API 호출 함수 모킹
#     mock_token_info = {
#         "access_token": "mock_access_token_1234567890",
#         "expires_in": 21599,
#         "token_type": "bearer",
#         "scope": "account_email profile_nickname",
#         "refresh_token": "mock_refresh_token_abcdefghij",
#         "refresh_token_expires_in": 5184000,
#     }
#     mocker.patch(
#         "app.apis.v1.kakao_auth_router.request_kakao_token",
#         return_value=mock_token_info,
#     )
#     mocker.patch(
#         "app.apis.v1.kakao_auth_router.get_kakao_profile",
#         return_value="testuser@example.com",
#     )
#
#     # 2. DB 쿼리 모킹 (유저가 존재한다고 가정)
#     mock_user = mocker.AsyncMock(spec=UserModel)
#     mock_user.id = 1
#     mock_user.email = "testuser@example.com"
#     mock_user._saved_in_db = True
#     # UserModel.get_or_none() 메서드를 비동기 모의 객체로 교체합니다.
#     mocker.patch.object(
#         UserModel,
#         "get_or_none",
#         new_callable=mocker.AsyncMock,
#         return_value=mock_user,
#     )
#
#     # 3. RefreshTokenModel의 필터링 및 삭제 모킹
#     # filter() 호출은 AsyncMock 객체를 반환하고, 그 객체에 delete() 메서드가 있다고 설정합니다.
#     mocker.patch.object(
#         RefreshTokenModel,
#         "filter",
#         return_value=mocker.AsyncMock(delete=mocker.AsyncMock(return_value=None)),
#     )
#
#     # 4. API 호출
#     async with httpx.AsyncClient(
#             transport=ASGITransport(app=app), base_url="http://test"
#     ) as client:
#         response = await client.get("/kakao-login", params={"code": "test_mock_code_123"})
#
#     # 5. 응답 검증
#     assert response.status_code == 200
#     response_json = response.json()
#     assert "access_token" in response_json
#     assert "redirect_url" in response_json
#
#
# @pytest.mark.asyncio
# async def test_kakao_login_user_not_exists(mocker):
#     """
#     DB에 유저가 존재하지 않는 경우를 테스트합니다.
#     - 307 Temporary Redirect 상태 코드를 반환하는지 확인합니다.
#     """
#     # 1. 외부 API 호출 함수 모킹
#     mock_token_info = {
#         "access_token": "mock_access_token_1234567890",
#         "expires_in": 21599,
#         "token_type": "bearer",
#         "scope": "account_email profile_nickname",
#         "refresh_token": "mock_refresh_token_abcdefghij",
#         "refresh_token_expires_in": 5184000,
#     }
#     mocker.patch(
#         "app.apis.v1.kakao_auth_router.request_kakao_token",
#         return_value=mock_token_info,
#     )
#     mocker.patch(
#         "app.apis.v1.kakao_auth_router.get_kakao_profile",
#         return_value="newuser@example.com",
#     )
#
#     # 2. DB 쿼리 모킹 (유저가 존재하지 않는다고 가정)
#     mocker.patch(
#         "app.models.user.UserModel.get_or_none",
#         return_value=None,
#     )
#
#     # 3. API 호출
#     async with httpx.AsyncClient(
#             transport=ASGITransport(app=app), base_url="http://test"
#     ) as client:
#         response = await client.get("/kakao-login", params={"code": "test_mock_code_123"})
#
#     # 4. 응답 검증
#     assert response.status_code == 307
#     assert response.headers["location"] == "http://test/user/register"