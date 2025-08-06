from fastapi import APIRouter, Response

from app.services.google_login import (
    create_access_token,
    create_refresh_token,
    get_google_profile,
    get_or_create_google_user,
    request_google_token,
)

router = APIRouter(prefix="/social-google", tags=["google-login"])


@router.get("/callback", description="Auth-Code")
async def google_auth(code: str, response: Response):
    token_info = request_google_token(code)
    email = get_google_profile(token_info["access_token"])
    user = await get_or_create_google_user(email)

    access_token = create_access_token(data={"sub": user.email})
    refresh_token = await create_refresh_token(user)

    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True)
    return {"access_token": access_token}
