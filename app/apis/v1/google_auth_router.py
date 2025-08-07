from fastapi import APIRouter, Response, status
from fastapi.responses import RedirectResponse
from app.services.google_login import (
    get_google_profile,
    get_or_create_google_user,
    request_google_token,
)
from app.services.token_service import(create_access_token, create_refresh_token)
from app.services.social_auth_session import set_cookie_by_email

router = APIRouter(prefix="/google-login", tags=["google-login"])
BASE_URL = "http://localhost:8000"

@router.get("", description="Auth-Code")
async def google_auth(code: str, response: Response):
    token_info = request_google_token(code)
    email = get_google_profile(token_info["access_token"])
    user = await get_or_create_google_user(email)
    response_with_session = await set_cookie_by_email(email,"google", response)

    if user: # 아이디가 있으면 바로 메인페이지
        response_with_session.headers['Location'] = f"{BASE_URL}/user/{user.id}"
        response_with_session.status_code = status.HTTP_307_TEMPORARY_REDIRECT
        return response_with_session

    else: # 첫 로긴이면 회원가입하게끔
        response_with_session.headers['Location'] = f"{BASE_URL}/register"
        response_with_session.status_code = status.HTTP_307_TEMPORARY_REDIRECT
        return  response_with_session

    # access_token = create_access_token(data={"sub": user.email})
    # refresh_token = await create_refresh_token(user)
    # response.set_cookie(key="refresh_token", value=refresh_token, httponly=True)


#https://accounts.google.com/o/oauth2/v2/auth?281980891262-7nagpvldql6sg5ejlvsecps9gvlsdcqj.apps.googleusercontent.com&http://localhost:8000/google-login&https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile&response_type=code
