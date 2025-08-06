import os
from typing import Any, Dict

import httpx
from fastapi import HTTPException, status
from jose import JWTError, jwt

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.environ.get("GOOGLE_REDIRECT_URI")


async def get_google_user(code: str) -> Dict[str, Any]:
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(token_url, data=data)
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to fetch token from Google: {response.json()}",
            )
        token_data = response.json()
        id_token = token_data.get("id_token")
        if not id_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="id_token not found in response from Google",
            )
        try:
            # Get Google's public keys
            async with httpx.AsyncClient() as client:
                jwks_response = await client.get(
                    "https://www.googleapis.com/oauth2/v3/certs"
                )
                jwks = jwks_response.json()

            header = jwt.get_unverified_header(id_token)
            key = [k for k in jwks["keys"] if k["kid"] == header["kid"]][0]

            user_info: Dict[str, Any] = jwt.decode(
                id_token,
                key=key,
                algorithms=["RS256"],
                audience=GOOGLE_CLIENT_ID,
                issuer="https://accounts.google.com",
                access_token=token_data.get("access_token"),
            )
        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid token: {e}",
            )
        return user_info
