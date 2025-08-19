from fastapi import APIRouter, Response, status
from fastapi.responses import JSONResponse, RedirectResponse

from app.config.settings import Settings
from app.models.refresh_token import RefreshTokenModel
from app.models.user import UserModel
from app.services.kakao_login import get_kakao_profile, request_kakao_token
from app.services.social_auth_session import set_cookie_by_email
from app.services.token_service import create_access_token, create_refresh_token

router = APIRouter(prefix="", tags=["kakao-user"])
settings = Settings()
BASE_URL = settings.base_url
MAIN_PAGE = "https://lol99.kro.kr/"

@router.get("/kakao-login", description="Auth-Code")
async def kakao_auth(code: str, response: Response):
    token_info = request_kakao_token(code, "/kakao-login")
    email = get_kakao_profile(token_info["access_token"])
    user = await UserModel.get_or_none(email=email)

    if user:
        await RefreshTokenModel.filter(user=user).delete()
        access_token = create_access_token(data={"sub": user.email})
        refresh_token = await create_refresh_token(user)
        response_data = {
            "access_token": access_token,
            "token_type": "bearer",
            "redirect_url": f"{MAIN_PAGE}",
        }
        response_with_redirection = JSONResponse(
            content=response_data,
            status_code=status.HTTP_200_OK,  # 리디렉션 상태 코드가 아님
        )
        response_with_redirection.set_cookie(
            key="refresh_token", value=refresh_token, httponly=True
        )
        return response_with_redirection

    else:
        redirect_response = RedirectResponse(
            url=f"{BASE_URL}/user/register",
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
        )
        response_with_session = await set_cookie_by_email(
            email, "kakao", redirect_response
        )
        return response_with_session


# https://kauth.kakao.com/oauth/authorize?response_type=code&client_id=a04159cc219d093bdcde9d55ea4b88fc&redirect_uri=http://localhost:8000/kakao-login
