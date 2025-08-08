import requests, os
from fastapi import HTTPException, status, Depends, Response, Request
from jose import jwt
from datetime import datetime, timedelta
from app.models.refresh_token import RefreshTokenModel
from app.models.user import UserModel
from typing import Optional
from fastapi.security import OAuth2PasswordBearer

SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

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
    refresh_token = jwt.encode(refresh_token_payload, SECRET_KEY, algorithm=ALGORITHM)
    await RefreshTokenModel.create(user=user, token=refresh_token)
    return refresh_token


# 토큰을 가져올 URL 지정. 이 URL은 실제 토큰을 발급하는 엔드포인트는 아닙니다.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)


async def get_current_user(
        request: Request,
        token: Optional[str] = Depends(oauth2_scheme)
) -> UserModel:

    access_token_from_cookie = request.cookies.get("access_token")
    token_to_verify = access_token_from_cookie if access_token_from_cookie else token

    if not token_to_verify:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="토큰이 제공되지 않았습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = verify_access_token(token_to_verify)
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="유효하지 않거나 만료된 토큰입니다.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        user_email: str = payload.get("sub")
        if user_email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="토큰에 사용자 정보가 없습니다.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        current_user = await UserModel.get_or_none(email=user_email)
        if current_user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="사용자가 존재하지 않습니다.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return current_user
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 토큰입니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )

def verify_access_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

async def verify_refresh_token(token: str) -> Optional[UserModel]:
    user = await UserModel.get_or_none(refresh_token=token)
    return user

async def refresh_access_token_and_get_user(
        refresh_token: str
):
    try:
        db_refresh_token = await RefreshTokenModel.get_or_none(token=refresh_token)
        if not db_refresh_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="유효하지 않은 Refresh Token입니다."
            )

        user = await db_refresh_token.user

        new_access_token = create_access_token(data={"sub": user.email})
        response.set_cookie(key="access_token", value=new_access_token, httponly=False)

        return {"access_token": new_access_token, "user_email": user.email}

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh Token 처리 중 오류가 발생했습니다."
        )



