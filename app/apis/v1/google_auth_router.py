from fastapi import APIRouter, Response, status
from fastapi.responses import RedirectResponse

from app.models.refresh_token import RefreshTokenModel
from app.models.user import UserModel
from app.services.google_login import (
    get_google_profile,
    request_google_token,
)
from app.services.social_auth_session import set_cookie_by_email
from app.services.token_service import create_access_token, create_refresh_token

router = APIRouter(prefix="", tags=["google-login"])
BASE_URL = "http://localhost:8000"

@router.get("/google-login", description="Auth-Code")
async def google_auth(code: str, response: Response):
    token_info = request_google_token(code,detail_url="/google-login")
    email = get_google_profile(token_info["access_token"])
    user = await UserModel.get_or_none(email=email)

    if user:
        await RefreshTokenModel.filter(user=user).delete()
        access_token = create_access_token(data={"sub": user.email})
        refresh_token = await create_refresh_token(user)
        redirect_response = RedirectResponse(url=f"{BASE_URL}/user/{user.id}",
                                             status_code=status.HTTP_307_TEMPORARY_REDIRECT)
        redirect_response.set_cookie(key="access_token", value=access_token)
        redirect_response.set_cookie(key="refresh_token", value=refresh_token, httponly=True)
        return redirect_response

    else:
        redirect_response = RedirectResponse(
            url=f"{BASE_URL}/user/register", status_code=status.HTTP_307_TEMPORARY_REDIRECT)
        response_with_session = await set_cookie_by_email(email, "google", redirect_response)
        return response_with_session

# https://accounts.google.com/o/oauth2/v2/auth?281980891262-7nagpvldql6sg5ejlvsecps9gvlsdcqj.
# apps.googleusercontent.com&http://localhost:8000/google-login&https://www.googleapis.com/auth/userinfo.email
# https://www.googleapis.com/auth/userinfo.profile&response_type=code
