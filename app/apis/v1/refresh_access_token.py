from fastapi import APIRouter, Cookie, HTTPException, status, Response
from app.models.refresh_token import RefreshTokenModel
from app.services.jwt_service import create_access_token, decode_jwt
from app.config.settings import SECRET_KEY, ALGORITHM
import jwt

router = APIRouter()


@router.post("/refresh-token", description="액세스 토큰 갱신")
async def refresh_access_token(
        response: Response,
        refresh_token: str = Cookie(None)
):
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="리프레시 토큰이 쿠키에 없습니다."
        )
    try:
        payload = decode_jwt(refresh_token, SECRET_KEY, ALGORITHM)
        user_id = payload.get("sub")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="유효하지 않은 토큰 페이로드입니다."
            )
        db_token = await RefreshTokenModel.get_or_none(token=refresh_token, user_id=user_id)
        if not db_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="데이터베이스에 존재하지 않는 토큰입니다."
            )
        user = await db_token.user
        new_access_token = create_access_token(data={"sub": user.email})

        # 4. (선택 사항) 토큰 회전 (Token Rotation)
        #   - 기존 토큰을 삭제하고 새로운 리프레시 토큰을 발급하여 보안 강화

        return {"access_token": new_access_token, "message": "새로운 액세스 토큰이 발급되었습니다."}

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="리프레시 토큰이 만료되었습니다. 다시 로그인해주세요."
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 리프레시 토큰입니다."
        )