from typing import Any, Dict, cast

import requests
from fastapi import HTTPException, status

from app.config.settings import Settings

settings = Settings()
GOOGLE_CLIENT_ID = settings.google_client_id
GOOGLE_CLIENT_SECRET = settings.google_client_secret
GOOGLE_REDIRECT_URI = settings.base_url


def request_google_token(code: str, detail_url) -> Dict[str, Any]:
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": f"{GOOGLE_REDIRECT_URI}{detail_url}",
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
    try:
        response = requests.get(user_info_url, headers=headers)
        response.raise_for_status()
        user_info = response.json()
        print(f"user_info: {user_info}")
        return user_info["email"]
    except requests.exceptions.RequestException as e:
        print(f"API 호출 중 오류 발생: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
        )
