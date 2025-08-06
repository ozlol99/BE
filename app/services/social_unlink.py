from fastapi import APIRouter, Depends, HTTPException, status
import httpx  # 비동기 HTTP 요청을 위한 라이브러리
from app.models.user import UserModel
from app.dependencies import get_authenticated_user

router = APIRouter()


# 🚨 이 함수는 소셜 계정 연동 해제 로직을 담당합니다.
async def unlink_social_account(user: UserModel):
    # httpx 클라이언트를 사용해 비동기로 API 호출
    async with httpx.AsyncClient() as client:
        # 카카오 계정인 경우
        if user.google_or_kakao == "kakao":
            # 카카오 액세스 토큰이 필요
            kakao_access_token = "..."  # DB에서 토큰을 가져오거나, 다른 방법으로 획득
            headers = {"Authorization": f"Bearer {kakao_access_token}"}

            # 카카오 연결 끊기 API 호출
            response = await client.post("https://kapi.kakao.com/v1/user/unlink", headers=headers)

            if response.status_code != 200:
                print(f"카카오 계정 연동 해제 실패: {response.text}")
                # 실패하더라도 서비스 내부 계정은 삭제할지, 롤백할지 결정해야 함

        # 구글 계정인 경우
        elif user.google_or_kakao == "google":
            # 구글 액세스 토큰이 필요
            google_access_token = "..."  # DB에서 토큰을 가져오거나, 다른 방법으로 획득

            # 구글 연결 끊기 API 호출
            response = await client.get(
                f"https://accounts.google.com/o/oauth2/revoke?token={google_access_token}"
            )
            if response.status_code != 200:
                print(f"구글 계정 연동 해제 실패: {response.text}")


@router.delete("/me")
async def delete_my_account(
        current_user: UserModel = Depends(get_authenticated_user)
):
    """
    현재 로그인한 사용자의 계정과 연동된 소셜 계정을 함께 삭제합니다.
    """
    # 🚨 계정 삭제 전에 소셜 계정 연동 해제 함수를 호출
    await unlink_social_account(current_user)

    # 🚨 DB에서 사용자 데이터 삭제
    await current_user.delete()

    return {"message": "사용자 계정이 성공적으로 삭제되었습니다."}