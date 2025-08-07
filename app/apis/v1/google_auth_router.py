from fastapi import APIRouter, Response
from fastapi.responses import RedirectResponse

from app.services.google_login import (
    get_google_profile,
    get_or_create_google_user,
    request_google_token,
)
from app.services.token_service import(create_access_token, create_refresh_token)

router = APIRouter(prefix="/social-google", tags=["google-login"])
BASE_URL = "http://localhost:8000"

@router.get("/callback", description="Auth-Code")
async def google_auth(code: str, response: Response):
    token_info = request_google_token(code)
    email = get_google_profile(token_info["access_token"])
    user = await get_or_create_google_user(email)

    if user: # 아이디가 있으면 바로 메인페이지
        main_page_url = f"{BASE_URL}/user/{user.id}"
        return RedirectResponse(url=main_page_url)

    else: # 첫 로긴이면 회원가입하게끔
        redirection_url = f"{BASE_URL}/register?email={email}&google_or_kakao=kakao"
        return  RedirectResponse(redirection_url)

    # access_token = create_access_token(data={"sub": user.email})
    # refresh_token = await create_refresh_token(user)
    # response.set_cookie(key="refresh_token", value=refresh_token, httponly=True)

