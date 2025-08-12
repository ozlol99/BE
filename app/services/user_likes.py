from fastapi import HTTPException, status
from typing import Dict
from tortoise.exceptions import IntegrityError, DoesNotExist

from app.models.user import UserModel, UserLikeModel



async def add_like(from_user_id: int, to_user_id: int) -> Dict[str, str]:
    if from_user_id == to_user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="자기 자신에게는 좋아요를 누를 수 없습니다."
        )

    try:
        # 좋아요를 누르는 사용자와 받는 사용자가 존재하는지 확인
        from_user = await UserModel.get(id=from_user_id)
        to_user = await UserModel.get(id=to_user_id)

        # 이미 좋아요를 눌렀는지 확인
        existing_like = await UserLikeModel.filter(from_user=from_user, to_user=to_user).first()
        if existing_like:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="이미 좋아요를 누른 사용자입니다."
            )

        # 새로운 좋아요 기록 생성 및 저장
        await UserLikeModel.create(from_user=from_user, to_user=to_user)

        return {"message": "좋아요가 성공적으로 추가되었습니다."}

    except DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="좋아요를 누르거나 받는 사용자를 찾을 수 없습니다."
        )
    except IntegrityError:
        # unique_together 제약 조건에 의해 발생할 수 있는 오류 처리
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 좋아요를 누른 사용자입니다."
        )
