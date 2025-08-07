import requests, os
from fastapi import HTTPException, status, Depends
from jose import jwt
from datetime import datetime, timedelta
from app.models.refresh_token import RefreshTokenModel
from app.models.user import UserModel
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
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    # 토큰이 유효하지 않거나 누락되면 OAuth2PasswordBearer가 자동으로 HTTPException을 발생시킵니다.
    try:
        # 🚨 이 부분에 토큰을 디코딩하고 유효성을 검사하는 코드가 들어갑니다.
        # 예: jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

        # 토큰 디코딩 후 페이로드(payload)에서 이메일 추출
        email = "decoded_email@example.com" # 🚨 실제 JWT 디코딩 로직으로 교체 필요

        if not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="유효하지 않은 토큰입니다.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return email # 유효한 사용자 이메일 반환
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 토큰입니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )