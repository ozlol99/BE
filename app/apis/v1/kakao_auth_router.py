from fastapi import APIRouter
from fastapi.responses import RedirectResponse

from app.services.kakao_login import get_kakao_profile, request_kakao_token

router = APIRouter(prefix="/kakao-login", tags=["kakao-login"])


@router.get("/kakao", description="카카오 로그인 시작")
def start_kakao_login():
    kakao_auth_url = "https://kauth.kakao.com/oauth/authorize?response_type=code&client_id=a04159cc219d093bdcde9d55ea4b88fc&redirect_uri=http://127.0.0.1:8000/kakao-login"
    return RedirectResponse(url=kakao_auth_url)


@router.get("", description="Auth-Code")
def kakao_auth(code: str):
    token_info = request_kakao_token(code)
    profile = get_kakao_profile(token_info["access_token"])

    return {
        "message": "카카오 토큰 발급 완료",
        "token_info": token_info,
        "user_info": profile,
    }


# https://kauth.kakao.com/oauth/authorize?response_type=code&client_id=a04159cc219d093bdcde9d55ea4b88fc&redirect_uri=http://127.0.0.1:8000/kakao-login
