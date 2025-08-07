from fastapi import APIRouter, Response, status
from fastapi.responses import RedirectResponse
from app.models.user import UserModel
from app.services.kakao_login import (get_kakao_profile, request_kakao_token)
from app.services.token_service import(create_access_token, create_refresh_token)
from app.services.social_auth_session import set_cookie_by_email

router = APIRouter(prefix="/kakao-login", tags=["kakao-login"])

BASE_URL = "http://localhost:8000"

@router.get("", description="Auth-Code")
async def kakao_auth(code: str, response: Response):
    token_info = request_kakao_token(code)
    email = get_kakao_profile(token_info["access_token"])
    user = await UserModel.get_or_none(email=email)
    response_with_session = await set_cookie_by_email(email,"kakao", response)

    if user: # 아이디가 있으면 바로 메인페이지
        response_with_session.headers['Location'] = f"{BASE_URL}/user/{user.id}"
        response_with_session.status_code = status.HTTP_307_TEMPORARY_REDIRECT
        return response_with_session

    else: # 첫 로긴이면 회원가입하게끔
        response_with_session.headers['Location'] = f"{BASE_URL}/register"
        response_with_session.status_code = status.HTTP_307_TEMPORARY_REDIRECT
        return  response_with_session

# https://kauth.kakao.com/oauth/authorize?response_type=code&client_id=a04159cc219d093bdcde9d55ea4b88fc&redirect_uri=http://127.0.0.1:8000/kakao-login

