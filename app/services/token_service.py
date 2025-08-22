from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt

from app.config.settings import Settings
from app.models.refresh_token import RefreshTokenModel
from app.models.user import UserModel

settings = Settings()

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = int(settings.access_token_expire_minutes)  # type: ignore
REFRESH_TOKEN_EXPIRE_DAYS = int(settings.refresh_token_expire_days)  # type: ignore
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)


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


async def get_current_user(
    request: Request, access_token_from_header: Optional[str] = Depends(oauth2_scheme)
) -> UserModel:
    access_token_from_cookie = request.cookies.get("access_token")
    token_to_verify = (
        access_token_from_cookie
        if access_token_from_cookie
        else access_token_from_header
    )

    if not token_to_verify:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="토큰이 제공되지 않았습니다.",
            headers={"Authorization": "Bearer"},
        )
    try:
        payload = verify_access_token(token_to_verify)
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="유효하지 않거나 만료된 토큰입니다.",
                headers={"Authorization": "Bearer"},
            )
        user_email: str = payload["sub"]
        if user_email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="토큰에 사용자 정보가 없습니다.",
                headers={"Authorization": "Bearer"},
            )
        current_user = await UserModel.get_or_none(email=user_email)
        if current_user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="사용자가 존재하지 않습니다.",
                headers={"Authorization": "Bearer"},
            )
        return current_user
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 토큰입니다.",
            headers={"Authorization": "Bearer"},
        )


def verify_access_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload  # type: ignore
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


async def refresh_access_token(refresh_token: str):
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="리프레시 토큰이 제공되지 않았습니다.",
        )

    try:
        # 리프레시 토큰 디코딩 및 유효성 검사
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="유효하지 않은 리프레시 토큰입니다.",
            )

        # DB에서 리프레시 토큰 조회
        db_refresh_token = await RefreshTokenModel.get_or_none(
            token=refresh_token, user_id=user_id
        )

        if not db_refresh_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="리프레시 토큰을 찾을 수 없습니다.",
            )

        # 리프레시 토큰이 이미 무효화되었는지 확인
        if db_refresh_token.revoked:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="무효화된 리프레시 토큰입니다.",
            )

        # 사용자 조회
        user = await UserModel.get_or_none(id=user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="사용자를 찾을 수 없습니다.",
            )

        # 새로운 액세스 토큰 발급
        new_access_token = create_access_token(data={"sub": user.email})

        # 새로운 액세스 토큰 반환
        return {"access_token": new_access_token, "token_type": "bearer"}

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="만료된 리프레시 토큰입니다.",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 리프레시 토큰입니다.",
        )
