from fastapi import APIRouter, Response, status
from fastapi.responses import RedirectResponse
from app.models.user import UserModel
from app.models.refresh_token import RefreshTokenModel
from app.services.kakao_login import (get_kakao_profile, request_kakao_token)
from app.services.token_service import(create_access_token, create_refresh_token)
from app.services.social_auth_session import set_cookie_by_email

router = APIRouter(prefix="", tags=["kakao-user"])
BASE_URL = "http://localhost:8000"

@router.get("/kakao-login", description="Auth-Code")
async def kakao_auth(code: str, response: Response):
    token_info = request_kakao_token(code, "/kakao-login")
    email = get_kakao_profile(token_info["access_token"])
    user = await UserModel.get_or_none(email=email)

    if user: # 아이디가 있으면 바로 메인페이지
        await RefreshTokenModel.filter(user=user).delete()
        access_token = create_access_token(data={"sub": user.email})
        refresh_token = await create_refresh_token(user)
        redirect_response = RedirectResponse(url=f"{BASE_URL}/user/{user.id}",
                                             status_code=status.HTTP_307_TEMPORARY_REDIRECT)
        redirect_response.set_cookie(key="access_token", value=access_token)
        redirect_response.set_cookie(key="refresh_token", value=refresh_token, httponly=True)
        return redirect_response

    else:  # 첫 로그인이라면 회원가입
        redirect_response = RedirectResponse(url=f"{BASE_URL}/user/register", status_code=status.HTTP_307_TEMPORARY_REDIRECT)
        response_with_session = await set_cookie_by_email(email, "kakao", redirect_response)
        return response_with_session

# https://kauth.kakao.com/oauth/authorize?response_type=code&client_id=a04159cc219d093bdcde9d55ea4b88fc&redirect_uri=http://127.0.0.1:8000/kakao-login
