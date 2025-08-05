import os

from fastapi import APIRouter
from fastapi.responses import RedirectResponse

router = APIRouter(prefix="/kakao-auth", tags=["kakao-auth"])


@router.get("")
def kakao_auth():
    KAKAO_API_KEY = "a04159cc219d093bdcde9d55ea4b88fc"
    REDIRECT_URI = "https://127.0.0.1:8000/kakao-auth"
    KAKAO_AUTH_URL = f"https://kauth.kakao.com/oauth/authorize?response_type=code&client_id={KAKAO_API_KEY}&redirect_uri={REDIRECT_URI}"
    return RedirectResponse(url=KAKAO_AUTH_URL)

