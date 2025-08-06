from fastapi import APIRouter
from fastapi.responses import RedirectResponse

from app.models.user import UserModel
from app.services.kakao_login import get_kakao_profile, request_kakao_token

router = APIRouter(prefix="/kakao-login", tags=["kakao-login"])

BASE_URL = "http://localhost:8000"

@router.get("", description="Auth-Code")
async def kakao_auth(code: str):
    token_info = request_kakao_token(code)
    email = get_kakao_profile(token_info["access_token"])
    user = await UserModel.get_or_none(email=email)

    if user: # 아이디가 있으면 바로 메인페이지
        main_page_url = f"{BASE_URL}/user/{user.id}"
        return RedirectResponse(url=main_page_url)

    else: # 첫 로긴이면 회원가입하게끔
        redirection_url = f"{BASE_URL}/register?email={email}&google_or_kakao=kakao"
        return RedirectResponse(redirection_url)

# https://kauth.kakao.com/oauth/authorize?response_type=code&client_id=a04159cc219d093bdcde9d55ea4b88fc&redirect_uri=http://127.0.0.1:8000/kakao-login

