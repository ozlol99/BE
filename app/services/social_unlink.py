from fastapi import APIRouter, Depends, HTTPException, status
import httpx  # 비동기 HTTP 요청을 위한 라이브러리
from app.models.user import UserModel

router = APIRouter()


# 🚨 이 함수는 소셜 계정 연동 해제 로직을 담당합니다.
async def unlink_social_account(token_info, user: UserModel):
    # httpx 클라이언트를 사용해 비동기로 API 호출
    async with httpx.AsyncClient() as client:
        if user.google_or_kakao == "kakao":
            kakao_access_token = token_info  # DB에서 토큰을 가져오거나, 다른 방법으로 획득
            headers = {"Authorization": f"Bearer {kakao_access_token}"}
            response = await client.post("https://kapi.kakao.com/v1/user/unlink", headers=headers)
            if response.status_code != 200:
                print(f"카카오 계정 연동 해제 실패: {response.text}")
                # 실패하더라도 서비스 내부 계정은 삭제할지, 롤백할지 결정해야 함

        elif user.google_or_kakao == "google":
            google_access_token = "..."  # DB에서 토큰을 가져오거나, 다른 방법으로 획득
            response = await client.get(
                f"https://accounts.google.com/o/oauth2/revoke?token={google_access_token}"
            )
            if response.status_code != 200:
                print(f"구글 계정 연동 해제 실패: {response.text}")
