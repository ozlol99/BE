import os

import httpx
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Query, status

from app.dtos.riot_user_dto import RiotUser_Pydantic
from app.models.rtSearch import RtSearchModel

load_dotenv()
RIOT_API_KEY = os.getenv("RIOT_API_KEY")

router = APIRouter(prefix="/riot", tags=["RIOT APIs"])
ASIA_BASE_URL = "https://asia.api.riotgames.com"
KR_BASE_URL = "https://kr.api.riotgames.com"

@router.get("/rtSearch")
async def rtSearch(summoner_name: str = Query(..., description="검색할 소환사명 일부")):
    users = await RtSearchModel.filter(summoner_name__icontains=summoner_name)
    pydantic_users = [RiotUser_Pydantic.from_orm(user) for user in users]
    return pydantic_users

@router.get("/summoner-info/{game_name}/{tag_line}")
async def search_summoner(game_name: str, tag_line: str):
  # Riot ID(닉네임 + 태그)를 사용하여 소환사 정보를 조회합니다.
    if not RIOT_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API 키가 설정되지 않았습니다."
        )
    headers = {"X-Riot-Token": RIOT_API_KEY}
    try:
        async with httpx.AsyncClient() as client:
            res1 = await client.get(
                f"{ASIA_BASE_URL}/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}",
                headers=headers
            )
            res1.raise_for_status()  # HTTP 오류 발생 시 예외 처리
            account_data = res1.json()
            puuid = account_data['puuid']
        async with httpx.AsyncClient() as client:
            res2 = await client.get(
                f"{KR_BASE_URL}/lol/summoner/v4/summoners/by-puuid/{puuid}",
                headers=headers
            )
            res2.raise_for_status()
            summoner_data = res2.json()
        await RtSearchModel.get_or_create(
            puuid=puuid,
            defaults={
                "summoner_name": game_name,
                "tag_line": tag_line,
            }
        )

        return {
            "summonerId": summoner_data.get('id'),
            "accountId": summoner_data.get('accountId'),
            "puuid": summoner_data.get('puuid'),
            "summonerLevel": summoner_data.get('summonerLevel')
        }

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"'{game_name}#{tag_line}' 소환사를 찾을 수 없습니다."
            )
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Riot API 호출 오류: {e.response.text}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"예상치 못한 서버 오류: {str(e)}"
        )
