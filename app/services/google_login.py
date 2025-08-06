import os
from datetime import datetime, timedelta
from typing import Any, Dict

import requests
from fastapi import HTTPException, status
from jose import JWTError, jwt

from app.models.refresh_token import RefreshTokenModel
from app.models.user import Social, UserModel

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.environ.get("GOOGLE_REDIRECT_URI")

SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7


def request_google_token(code: str) -> Dict[str, Any]:
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    response = requests.post(token_url, data=data)
    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to fetch token from Google: {response.json()}",
        )
    return response.json()


def get_google_profile(access_token: str) -> str:
    user_info_url = "https://www.googleapis.com/oauth2/v3/userinfo"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(user_info_url, headers=headers)
    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to fetch user info from Google: {response.json()}",
        )
    user_info = response.json()
    return user_info["email"]


async def get_or_create_google_user(email: str) -> UserModel:
    user = await UserModel.get_or_none(email=email)
    if user:
        if user.google_or_kakao != Social.google:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"This email is already registered with {user.google_or_kakao}",
            )
    else:
        user = await UserModel.create(
            email=email,
            google_or_kakao=Social.google,
            likes=0,
        )
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def create_refresh_token(user: UserModel):
    refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token_payload = {
        "sub": str(user.id),
        "exp": datetime.utcnow() + refresh_token_expires,
    }
    refresh_token = jwt.encode(
        refresh_token_payload, SECRET_KEY, algorithm=ALGORITHM
    )
    await RefreshTokenModel.create(user_id=user, token=refresh_token)
    return refresh_token
