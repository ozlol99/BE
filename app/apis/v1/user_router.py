from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from tortoise.exceptions import DoesNotExist, IntegrityError

from app.dtos.user_dto import (
    RiotAccountResponse,
    UserDTO,
    UserMeResponse,
    UserUpdate,
)
from app.models.refresh_token import RefreshTokenModel
from app.models.riot_account import RiotAccount
from app.models.user import UserModel
from app.services import summoner_search_service
from app.services.google_login import request_google_token
from app.services.kakao_login import request_kakao_token
from app.services.social_auth_session import SessionData, cookie, get_data_from_cookie
from app.services.social_unlink import unlink_social_account
from app.services.token_service import (
    create_access_token,
    create_refresh_token,
    get_current_user,
    refresh_access_token,
)
from app.services.user_likes import add_like

router = APIRouter(prefix="/user", tags=["user"])


# DTOs for Riot Account Management
class RiotAccountCreate(BaseModel):
    game_name: str
    tag_line: str


@router.post("/register", description="register")
async def register_user(
    user_data: UserDTO, session_data: SessionData = Depends(get_data_from_cookie)
):
    try:
        email = session_data.email
        google_or_kakao = session_data.google_or_kakao
        new_user = await UserModel.create(
            email=email,
            user=user_data.user,  # 닉네임
            google_or_kakao=google_or_kakao,
            gender=user_data.gender,  # 1 남자 0 여자
            birthday=user_data.birthday,
        )
        access_token = create_access_token(data={"sub": new_user.email})
        refresh_token = await create_refresh_token(new_user)
        response = JSONResponse(
            content={"access_token": access_token, "token_type": "bearer"},
            status_code=status.HTTP_201_CREATED,
        )
        response.set_cookie(key="refresh_token", value=refresh_token, httponly=True)
        cookie.delete_from_response(response)
        return response

    except IntegrityError:
        raise HTTPException(status_code=400, detail="Wrong Request")


@router.get("/me", response_model=UserMeResponse)
async def get_my_info(current_user: UserModel = Depends(get_current_user)):
    riot_accounts = await current_user.riot_accounts
    return UserMeResponse(
        id=current_user.id,
        email=current_user.email,
        birthday=current_user.birthday,
        gender=current_user.gender,
        user=current_user.user,
        google_or_kakao=current_user.google_or_kakao,
        riot_accounts=[
            RiotAccountResponse.model_validate(acc) for acc in riot_accounts
        ],
    )


@router.patch("/me")
async def update_my_info(
    updated_info: UserUpdate, current_user: UserModel = Depends(get_current_user)
):
    now = datetime.utcnow()
    update_data = updated_info.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="수정할 정보를 입력해주세요.",
        )

    if current_user.updated_at and (
        now - current_user.updated_at < timedelta(hours=24)
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="24시간 후에 다시 시도해주세요.",
        )

    for key, value in update_data.items():
        setattr(current_user, key, value)

    current_user.updated_at = now
    await current_user.save()
    return {"message": "사용자 정보가 성공적으로 업데이트되었습니다."}


@router.delete("/logout")
async def logout_my_account(
    response: Response = Response(), current_user: UserModel = Depends(get_current_user)
):
    # 현재 사용자의 활성 리프레시 토큰을 찾아 무효화
    refresh_token = await RefreshTokenModel.get_or_none(
        user=current_user, revoked=False
    )
    if refresh_token:
        refresh_token.revoked = True
        await refresh_token.save()

    # 클라이언트 측에서 액세스 토큰 쿠키 삭제 (기존 로직)
    response.delete_cookie(key="access_token")

    return {"message": "모든 세션이 종료되었습니다. 로그아웃되었습니다."}


@router.get("/delete")
async def delete_my_account(
    code: str, current_user: UserModel = Depends(get_current_user)
):
    # User가 주소 클릭 (카카오로 연동했는지 구글로 연동했는지 확인해야함)
    # 구글 auth-code 얻는 주소
    # https://kauth.kakao.com/oauth/authorize?response_type=code&client_id=a04159cc219d093bdcde9d55ea4b88fc&redirect_uri=http://127.0.0.1:8000/user/delete
    if current_user.google_or_kakao == "kakao":
        token_info = request_kakao_token(code, "/user/delete")
        await unlink_social_account(token_info["access_token"], current_user)
        await RefreshTokenModel.filter(user=current_user).delete()
        await current_user.delete()  # 🚨 DB에서 사용자 데이터 삭제
        return {"message": "사용자 계정이 성공적으로 삭제되었습니다."}
    else:
        # https://accounts.google.com/o/oauth2/v2/auth?response_type=code&scope=openid%20email&client_id=281980891262-7nagpvldql6sg5ejlvsecps9gvlsdcqj.apps.googleusercontent.com&redirect_uri=http://localhost:8000/user/delete
        token_info = request_google_token(code, "/user/delete")
        # 🚨 계정 삭제 전에 소셜 계정 연동 해제 함수를 호출
        await unlink_social_account(token_info["access_token"], current_user)
        await RefreshTokenModel.filter(user=current_user).delete()
        await current_user.delete()  # 🚨 DB에서 사용자 데이터 삭제
        return {"message": "사용자 계정이 성공적으로 삭제되었습니다."}


@router.post("/like/{from_user_id}/{to_user_id}", status_code=status.HTTP_201_CREATED)
async def handle_like(from_user_id: int, to_user_id: int):
    return await add_like(from_user_id, to_user_id)


# Riot Account Management Endpoints
@router.post(
    "/riot-accounts",
    status_code=status.HTTP_201_CREATED,
    response_model=RiotAccountResponse,
)
async def link_riot_account(
    account_data: RiotAccountCreate,
    current_user: UserModel = Depends(get_current_user),
):
    """Links a Riot account to the current user's profile."""
    try:
        # 1. Validate if the Riot account exists using the search service
        await summoner_search_service.get_summoner_info(
            account_data.game_name, account_data.tag_line
        )

        # 2. Create and link the Riot account
        new_account = await RiotAccount.create(
            user=current_user,
            game_name=account_data.game_name,
            tag_line=account_data.tag_line,
        )
        return new_account

    except HTTPException as e:
        # Re-raise exceptions from the search service (e.g., 404 Not Found)
        raise e
    except IntegrityError:
        # This happens if the game_name#tag_line is already linked in the DB
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This Riot account is already linked.",
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while linking the account.",
        )


@router.get("/riot-accounts", response_model=List[RiotAccountResponse])
async def get_linked_riot_accounts(current_user: UserModel = Depends(get_current_user)):
    """Gets a list of Riot accounts linked to the current user."""
    accounts = await RiotAccount.filter(user=current_user)
    return [RiotAccountResponse.model_validate(acc) for acc in accounts]


@router.delete("/riot-accounts/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unlink_riot_account(
    account_id: int, current_user: UserModel = Depends(get_current_user)
):
    """Unlinks a Riot account from the current user's profile."""
    try:
        account_to_delete = await RiotAccount.get(id=account_id, user=current_user)
        await account_to_delete.delete()
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Riot account not found or you don't have permission to unlink it.",
        )


@router.post(
    "/token/refresh",
    summary="액세스 토큰 갱신",
    description="리프레시 토큰을 사용 하여 새로운 액세스 토큰을 발급합니다.",
)
async def refresh_access_token_router(
    response: Response, refresh_token: str = Depends(cookie)
):
    return_value = await refresh_access_token(refresh_token)
    return return_value
