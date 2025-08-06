import os
from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import RedirectResponse
from jose import jwt

from app.models.user import Social, UserModel
from app.services.google_login import get_google_user

router = APIRouter(prefix="/social-google", tags=["google-login"])

SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


@router.get("", description="구글 로그인창으로 넘기기")
def start_google_login():
    google_auth_url = "https://accounts.google.com/o/oauth2/v2/auth?response_type=code&scope=openid%20email&client_id=281980891262-7nagpvldql6sg5ejlvsecps9gvlsdcqj.apps.googleusercontent.com&redirect_uri=http://localhost:8000/social-google/callback"
    return RedirectResponse(url=google_auth_url)


@router.get("/callback")
async def google_oauth_callback(code: str):
    user_info = await get_google_user(code)
    user = await UserModel.get_or_none(email=user_info["email"])

    if user:
        if user.google_or_kakao != Social.google:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"This email is already registered with {user.google_or_kakao}",
            )
    else:
        user = await UserModel.create(
            email=user_info["email"],
            google_or_kakao=Social.google,
            likes=0,
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        "sub": user.email,
        "exp": datetime.now() + access_token_expires,
    }
    access_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return (
        {"access_token": access_token, "token_type": "bearer"},
        {"user_info": user_info},
        {"data": code},
    )
