from uuid import UUID, uuid4
from pydantic import BaseModel
from fastapi import FastAPI, Depends, HTTPException, Request,Response
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
async def set_cookie_by_email(email:str, google_or_kakao:str, response: Response) -> SessionData:
    social_email = email
    session_id = uuid4()
    session_data = SessionData(email=social_email, google_or_kakao=google_or_kakao)
    await backend.create(session_id, session_data)
    print("backend added")
    cookie.attach_to_response(response, session_id)
    return response

async def get_data_from_cookie(session_id: UUID = Depends(cookie)) -> SessionData:
    session_data = await backend.read(session_id)
    if session_data is None:
        raise HTTPException(status_code=401, detail="유효하지 않은 세션입니다.")

    return session_data




