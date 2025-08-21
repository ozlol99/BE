from fastapi import APIRouter, Response, status
from fastapi.responses import JSONResponse, RedirectResponse

from app.config.settings import Settings
from app.models.refresh_token import RefreshTokenModel
from app.models.user import UserModel
from app.services.google_login import (
    get_google_profile,
    request_google_token,
)
from app.services.social_auth_session import set_cookie_by_email
from app.services.token_service import create_access_token, create_refresh_token

router = APIRouter(prefix="", tags=["google-login"])
settings = Settings()
BASE_URL = settings.base_url
MAIN_URL = settings.main_url

# https://accounts.google.com/o/oauth2/v2/auth?response_type=&scope=openid%20email&client_id=281980891262-7nagpvldql6sg5ejlvsecps9gvlsdcqj.apps.googleusercontent.com&redirect_uri=http://localhost:8000/google-login


@router.get("/google-login", description="Auth-Code")
async def google_auth(code: str, response: Response):
    token_info = request_google_token(code, detail_url="/google-login")
    email = get_google_profile(token_info["access_token"])
    user = await UserModel.get_or_none(email=email)

    if user:
        await RefreshTokenModel.filter(user=user).delete()
        access_token = create_access_token(data={"sub": user.email})
        refresh_token = await create_refresh_token(user)
        response_data = {
            "access_token": access_token,
            "token_type": "bearer",
            "redirect_url": f"{MAIN_URL}",
        }
        response_with_redirection = JSONResponse(
            content=response_data,
            status_code=status.HTTP_200_OK,  # 리디렉션 상태 코드가 아님
        )
        response_with_redirection.set_cookie(
            key="refresh_token", value=refresh_token, httponly=True
        )
        # print(token_info)
        return response_with_redirection

    else:
        redirect_response = RedirectResponse(
            url=f"{MAIN_URL}/add-info",
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
        )
        response_with_session = await set_cookie_by_email(
            email, "google", redirect_response
        )
        return response_with_session
