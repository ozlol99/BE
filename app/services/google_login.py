import os
from typing import Any, Dict, cast

import requests
from fastapi import HTTPException, status
from jose import jwt

from app.models.user import Social, UserModel

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.environ.get("GOOGLE_REDIRECT_URI")



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
    return cast(Dict[str, Any], response.json())


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
    return cast(str, user_info["email"])


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
