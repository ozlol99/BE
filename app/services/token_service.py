import requests, os, dotenv
from fastapi import HTTPException, status, Depends, Response, Request
from jose import jwt
from datetime import datetime, timedelta
from app.models.refresh_token import RefreshTokenModel
from app.models.user import UserModel
from typing import Optional
from fastapi.security import OAuth2PasswordBearer

dotenv.load_dotenv()
SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = os.environ.get("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.environ.get("REFRESH_TOKEN_EXPIRE_DAYS"))
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

