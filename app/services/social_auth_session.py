from uuid import UUID, uuid4
from pydantic import BaseModel
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi_sessions.backends.implementations import InMemoryBackend
from fastapi_sessions.frontends.implementations import SessionCookie, CookieParameters


# 1. 세션에 저장할 데이터 모델 정의
class SessionData(BaseModel):
    email: str
    google_or_kakao: str

# 2. 세션 백엔드(저장소) 생성
backend = InMemoryBackend[UUID, SessionData]()

# 3. 세션 프론트엔드(쿠키) 설정
cookie_params = CookieParameters()
cookie = SessionCookie(
    cookie_name="pre-signup-session",
    identifier="pre_signup_verifier",
    auto_error=True,
    secret_key="your-super-secret-key",  # 반드시 안전한 비밀 키 사용
    cookie_params=cookie_params,
)

async def get_email_from_cookie(request: Request) -> SessionData:
    """클라이언트 쿠키에서 세션 ID를 읽어 세션 데이터를 반환합니다."""
    session_id = cookie.get_session_id(request)
    if not session_id:
        raise HTTPException(status_code=401, detail="세션 쿠키가 존재하지 않습니다.")

    data = await backend.read(session_id)
    if data is None:
        raise HTTPException(status_code=401, detail="유효하지 않은 세션입니다.")
    return data


async def set_cookie_by_email(email:str):
    social_email = email
    session_id = uuid4()
    session_data = SessionData(email=social_email)
    await backend.create(session_id, session_data)

    return cookie.set_session(session_id)


