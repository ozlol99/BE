from fastapi import APIRouter, HTTPException, Depends
from tortoise.exceptions import IntegrityError
from app.dtos.user_dto import UserDTO, UserUpdate
from app.models.user import UserModel  # 🚨 UserModel 모델을 import
from app.services.social_unlink import unlink_social_account
from app.services.token_service import get_current_user
from app.services.social_auth_session import get_email_from_cookie, cookie, SessionData
router = APIRouter(prefix="/user", tags=["user"])

@router.post("/register", description="register")
async def register_user(
        user_data: UserDTO,
        session_data: SessionData = Depends(get_email_from_cookie)
):
    try:
        email = session_data.email
        google_or_kakao = session_data.google_or_kakao

        new_user = await UserModel.create(
            email=email,
            user=user_data.user,  # 닉네임
            riot_user="Cannot Insert Now",
            google_or_kakao=google_or_kakao,
            gender=user_data.gender,  # 1 남자 0 여자
            birthday=user_data.birthday,
            likes=0,
        )
        return cookie.delete_session()

    except IntegrityError:
        raise HTTPException(
            status_code=400, detail="User with this email or username already exists."
        )

@router.get("/me")
async def get_my_info(current_user: UserModel = Depends(get_current_user)):
    """
    현재 로그인한 사용자의 정보를 반환합니다.
    """
    return {
        "id": current_user.id,
        "email": current_user.email,
        "user": current_user.user,
        "google_or_kakao": current_user.google_or_kakao,
        "likes": current_user.likes,
    }

@router.patch("/me")
async def update_my_info(
        updated_info: UserUpdate,
        current_user: UserModel = Depends(get_current_user)
):
    # 받은 데이터로 유저 모델 업데이트
    if updated_info.user:
        current_user.user = updated_info.user
    if updated_info.email:
        # 이메일 중복 체크 등 필요한 유효성 검사 추가
        current_user.email = updated_info.email

    await current_user.save()

    return {"message": "사용자 정보가 성공적으로 업데이트되었습니다."}


@router.delete("/me")
async def delete_my_account(
        current_user: UserModel = Depends(get_current_user)
):
    await unlink_social_account(current_user)  # 🚨 계정 삭제 전에 소셜 계정 연동 해제 함수를 호출
    await current_user.delete() # 🚨 DB에서 사용자 데이터 삭제

    return {"message": "사용자 계정이 성공적으로 삭제되었습니다."}