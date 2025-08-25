from typing import Optional

from fastapi import APIRouter, Query

from app.dtos.riot_user_dto import RiotUser_Pydantic
from app.models.search_summoner import RtSearchModel
from app.services.summoner_search_service import (
    get_rank_info,
    get_recent_matches,
    get_summoner_info,
    update_highest_rank,
)

router = APIRouter(prefix="/riot", tags=["RIOT APIs"])


@router.get("/rtSearch")
async def rtSearch(
    summoner_name: Optional[str] = Query("", description="검색할 소환사명 일부"),
    tag_line: Optional[str] = Query("", description="검색할 태그라인"),
):
    filtering1 = RtSearchModel.filter(summoner_name__icontains=summoner_name)
    filtering2 = filtering1.filter(tag_line__icontains=tag_line)
    users = await filtering2
    pydantic_users = [RiotUser_Pydantic.from_orm(user) for user in users]
    return pydantic_users


@router.get("/summoner-info/{summoner_name}/{tag_line}")
async def search_summoner(
    summoner_name: str,
    tag_line: str,
    queue_id: Optional[int] = None,
    count_start: int = 0,  # 👈 쿼리 파라미터로 start를 받음
    match_count: int = 20,  # 👈 쿼리 파라미터로 count를 받음
):
    summoner_info = await get_summoner_info(summoner_name, tag_line)
    rank_info = await get_rank_info(summoner_info["puuid"])
    highest_rank = await update_highest_rank(
        rank_info, summoner_info["puuid"], summoner_name, tag_line
    )
    recent_matches_summary, recent_matches = await get_recent_matches(
        summoner_info["puuid"],
        queue_id,
        count_start,
        match_count,
    )

    return {
        "summoner_info": summoner_info,
        "rank_info": rank_info,
        "highest_rank": highest_rank,
        "match_summary": recent_matches_summary,
        "recent_matches": recent_matches,
    }
