from fastapi import APIRouter, HTTPException
from app.dtos.user_dto import UserDTO
from tortoise.exceptions import IntegrityError
from app.models.user import UserModel # 🚨 UserModel 모델을 import
router = APIRouter(prefix="/user", tags=["user"])


@router.post("/register", description="register")
async def regisetr_user(user_data: UserDTO, email, google_or_kakao):
    try:
        new_user = await UserModel.create(
            email=email,
            user=user_data.user, # 닉네임
            google_or_kakao=google_or_kakao,
            gender=user_data.gender, # 0 남자 1 여자
            birthday=user_data.birthday,
            likes=user_data.likes,
        )
        return {"message": "User registered successfully!", "user_id": new_user.id}
    except IntegrityError:
        raise HTTPException(
            status_code=400,
            detail="User with this email or username already exists."
        )