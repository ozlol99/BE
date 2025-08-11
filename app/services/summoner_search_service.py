import os

import httpx
from fastapi import HTTPException, status

from app.models.search_summoner import RtSearchModel

ASIA_BASE_URL = "https://asia.api.riotgames.com"
KR_BASE_URL = "https://kr.api.riotgames.com"
RIOT_API_KEY = os.getenv("RIOT_API_KEY")

async def get_summoner_info(game_name: str, tag_line: str):
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
