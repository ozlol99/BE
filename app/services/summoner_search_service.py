import datetime
from typing import TYPE_CHECKING, Any, Dict, List

import httpx
import requests
from fastapi import HTTPException, status
from tortoise.exceptions import DoesNotExist

from app.config.settings import Settings
from app.models.search_summoner import RtSearchModel
from app.utils.timestamp import format_time_ago_v1

if TYPE_CHECKING:
    pass

settings = Settings()

ASIA_BASE_URL = "https://asia.api.riotgames.com"
KR_BASE_URL = "https://kr.api.riotgames.com"
RIOT_API_KEY = settings.riot_api_key


async def get_summoner_info(summoner_name: str, tag_line: str):
    if not RIOT_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API 키가 설정되지 않았습니다.",
        )
    headers = {"X-Riot-Token": RIOT_API_KEY}
    try:
        async with httpx.AsyncClient() as client:
            res1 = await client.get(
                f"{ASIA_BASE_URL}/riot/account/v1/accounts/by-riot-id/{summoner_name}/{tag_line}",
                headers=headers,
            )
            res1.raise_for_status()  # HTTP 오류 발생 시 예외 처리
            account_data = res1.json()
            puuid = account_data["puuid"]
        async with httpx.AsyncClient() as client:
            res2 = await client.get(
                f"{KR_BASE_URL}/lol/summoner/v4/summoners/by-puuid/{puuid}",
                headers=headers,
            )
            res2.raise_for_status()
            summoner_data = res2.json()
        # DB에 바로 저장, 바로 검색을 위해

        return {
            "summonerId": summoner_data.get("id"),
            "accountId": summoner_data.get("accountId"),
            "puuid": summoner_data.get("puuid"),
            "profileIconId": summoner_data.get("profileIconId"),
            "summonerLevel": summoner_data.get("summonerLevel"),
        }

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"'{summoner_name}#{tag_line}' 소환사를 찾을 수 없습니다.",
            )
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Riot API 호출 오류: {e.response.text}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"예상치 못한 서버 오류: {str(e)}",
        )


async def get_rank_info(summoner_id: str) -> Dict[str, Any]:
    url = f"{KR_BASE_URL}/lol/league/v4/entries/by-puuid/{summoner_id}?api_key={RIOT_API_KEY}"
    response = requests.get(url)
    if response.status_code != 200:
        print("Rank_data Return Error!")
        return {}  # 랭크 정보가 없는 경우 빈 딕셔너리 반환

    data = response.json()

    rank_data = {}
    for entry in data:
        queue_type = entry.get("queueType")
        if queue_type == "RANKED_SOLO_5x5":
            rank_data["solo_rank"] = {
                "tier": entry.get("tier"),
                "rank": entry.get("rank"),
                "league_points": entry.get("leaguePoints"),
                "wins": entry.get("wins"),
                "losses": entry.get("losses"),
                "win_rate": round(
                    entry.get("wins") / (entry.get("wins") + entry.get("losses")) * 100,
                    2,
                ),
            }
        elif queue_type == "RANKED_FLEX_SR":
            rank_data["flex_rank"] = {
                "tier": entry.get("tier"),
                "rank": entry.get("rank"),
                "league_points": entry.get("leaguePoints"),
                "wins": entry.get("wins"),
                "losses": entry.get("losses"),
                "win_rate": round(
                    entry.get("wins") / (entry.get("wins") + entry.get("losses")) * 100,
                    2,
                ),
            }
    return rank_data


QUEUE_TYPE_MAP = {
    400: "일반 게임",
    420: "솔로 랭크",
    430: "일반 게임",
    440: "자유 랭크",
    450: "칼바람 나락",
    900: "URF",
    1700: "아레낭",
}


def get_match_info(match_id: str, puuid: str) -> Dict[str, Any]:
    if not RIOT_API_KEY:
        raise ValueError("RIOT_API_KEY 환경 변수가 설정되지 않았습니다.")
    url = f"{ASIA_BASE_URL}/lol/match/v5/matches/{match_id}?api_key={RIOT_API_KEY}"
    response = requests.get(url)
    if response.status_code != 200:
        raise ValueError(
            f"Riot API 호출 중 오류 발생: 상태 코드 {response.status_code}"
        )
    match_data = response.json()
    info = match_data.get("info", {})
    metadata = match_data.get("metadata", {})
    participant = next(
        (p for p in info.get("participants", []) if p.get("puuid") == puuid), None
    )

    if not participant:
        raise ValueError(f"PUUID '{puuid}'을(를) 이 매치에서 찾을 수 없습니다.")

    kills = participant.get("kills", 0)
    deaths = participant.get("deaths", 0)
    assists = participant.get("assists", 0)
    kda = (kills + assists) / deaths if deaths > 0 else (kills + assists)
    perks = participant.get("perks", {}).get("styles", [])
    primary_rune_style = perks[0].get("style") if len(perks) > 0 else None
    sub_rune_style = perks[1].get("style") if len(perks) > 1 else None

    processed_data = {
        "match_id": metadata.get("matchId"),
        "summoner_name": participant.get("riotIdGameName"),  # 추가
        "rank_type": QUEUE_TYPE_MAP.get(info.get("queueId"), "알 수 없는 랭크"),
        "win": participant.get("win"),  # 👈 승패 정보 추가
        "game_end_timestamp": str(format_time_ago_v1(info.get("gameEndTimestamp"))),
        "play_duration": str(int(info.get("gameDuration") / 60)) + "분",
        "kda": {
            "kills": kills,
            "deaths": deaths,
            "assists": assists,
            "kda_ratio": round(kda, 2),
        },
        "runes": {
            "primary_style": primary_rune_style,
            "sub_style": sub_rune_style,
        },
        "spells": [participant.get("summoner1Id"), participant.get("summoner2Id")],
        "items": [participant.get(f"item{i}") for i in range(7)],
        "teammates_and_opponents": [
            {
                "summoner_name": p.get("riotIdGameName"),
                "champion": p.get("championName"),
                "team_id": p.get("teamId"),
            }
            for p in info.get("participants", [])
        ],
        "champion_name": participant.get("championName"),
    }
    if info.get("queueId") in [420, 430, 440]:
        processed_data["position"] = participant.get("role")
    return processed_data


async def get_recent_matches(
    puuid: str,
    queue_id,
    count_start,
    match_count,
) -> tuple[Dict[str, Any], List[Dict[str, Any]]]:
    if queue_id:
        matchlist_url = (
            f"{ASIA_BASE_URL}/lol/match/v5/matches/by-puuid/{puuid}/"
            f"ids?start={count_start}&count={match_count}&queue={queue_id}&api_key={RIOT_API_KEY}"
        )
    else:
        matchlist_url = (
            f"{ASIA_BASE_URL}/lol/match/v5/matches/by-puuid/{puuid}/"
            f"ids?start={count_start}&count={match_count}&api_key={RIOT_API_KEY}"
        )
        print(f"매치 ID {match_count}개 가져오는 중...")
    response = requests.get(matchlist_url)
    if response.status_code != 200:
        raise ValueError(f"매치 리스트 조회 오류: 상태 코드 {response.status_code}")

    match_ids = response.json()

    # 통계 계산을 위한 변수 초기화
    total_wins = 0
    total_games = len(match_ids)
    total_kills = 0
    total_deaths = 0
    total_assists = 0
    position_counts: dict = {}
    champion_counts: dict = {}  # 챔피언 플레이 횟수를 저장할 딕셔너리 추가
    all_processed_matches = []  # 모든 매치 데이터를 저장할 리스트

    print(f"매치 {total_games}개 상세 정보 조회 시작...")

    for match_id in match_ids:
        match_data = get_match_info(match_id, puuid)

        if match_data:
            all_processed_matches.append(match_data)  # 매치 데이터를 리스트에 추가

            # 승패 정보 집계
            if match_data["win"]:
                total_wins += 1

            # KDA 정보 집계
            total_kills += match_data["kda"]["kills"]
            total_deaths += match_data["kda"]["deaths"]
            total_assists += match_data["kda"]["assists"]

            # 포지션 정보 집계
            position = match_data.get("position")
            if position:
                position_counts[position] = position_counts.get(position, 0) + 1

            champion = match_data.get("champion_name")
            if champion:
                champion_counts[champion] = champion_counts.get(champion, 0) + 1

    win_rate = (total_wins / total_games) * 100 if total_games > 0 else 0
    sorted_champions = sorted(
        champion_counts.items(), key=lambda item: item[1], reverse=True
    )

    if total_deaths > 0:
        avg_kda = (total_kills + total_assists) / total_deaths
    else:
        avg_kda = total_kills + total_assists

    most_played_position = max(
        position_counts, key=lambda positions: position_counts[positions]
    )

    summary = {
        "총 매치 수": total_games,
        "승리 수": total_wins,
        "패배 수": total_games - total_wins,
        "승률": f"{win_rate:.2f}%",
        "평균 KDA": f"{total_kills}/{total_deaths}/{total_assists} ({avg_kda:.2f})",
        "주 포지션": f"{most_played_position} ({position_counts.get(most_played_position, 0)}회)",
        "포지션별 플레이 횟수": position_counts,
        "챔피언별 플레이 횟수": dict(sorted_champions),
    }

    return summary, all_processed_matches


# 'UNRANKED'를 포함하여 티어에 우선순위를 부여합니다.
TIER_ORDER = {
    "UNRANKED": -1,
    "IRON": 0,
    "BRONZE": 1,
    "SILVER": 2,
    "GOLD": 3,
    "PLATINUM": 4,
    "EMERALD": 5,
    "DIAMOND": 6,
    "MASTER": 7,
    "GRANDMASTER": 8,
    "CHALLENGER": 9,
}

RANK_ORDER = {"IV": 0, "III": 1, "II": 2, "I": 3}


def get_rank_value(tier, rank):
    """티어와 랭크를 기준으로 순위 값을 반환합니다."""
    tier_value = TIER_ORDER.get(tier, -1)
    rank_value = RANK_ORDER.get(rank, -1)
    return tier_value * 4 + rank_value


async def update_highest_rank(current_rank_info, puuid, summoner_name, tag_line):
    solo_rank_data = current_rank_info.get("solo_rank", {})
    flex_rank_data = current_rank_info.get("flex_rank", {})
    current_solo_tier = solo_rank_data.get("tier", "UNRANKED")
    current_solo_rank = solo_rank_data.get("rank", "IV")
    current_solo_lp = solo_rank_data.get("league_points", 0)
    current_flex_tier = flex_rank_data.get("tier", "UNRANKED")
    current_flex_rank = flex_rank_data.get("rank", "IV")
    current_flex_lp = flex_rank_data.get("league_points", 0)

    try:
        highest_rank_data = await RtSearchModel.get(puuid=puuid)
        current_solo_value = get_rank_value(current_solo_tier, current_solo_rank)
        highest_solo_value = get_rank_value(
            highest_rank_data.highest_solo_tier, highest_rank_data.highest_solo_rank
        )

        is_new_solo_rank_higher = False
        if current_solo_value > highest_solo_value:
            is_new_solo_rank_higher = True
        elif (
            current_solo_value == highest_solo_value
            and current_solo_lp > highest_rank_data.highest_solo_lp
        ):
            is_new_solo_rank_higher = True

        if is_new_solo_rank_higher:
            highest_rank_data.highest_solo_tier = current_solo_tier
            highest_rank_data.highest_solo_rank = current_solo_rank
            highest_rank_data.highest_solo_lp = current_solo_lp

        current_flex_value = get_rank_value(current_flex_tier, current_flex_rank)
        highest_flex_value = get_rank_value(
            highest_rank_data.highest_flex_tier, highest_rank_data.highest_flex_rank
        )

        is_new_flex_rank_higher = False
        if current_flex_value > highest_flex_value:
            is_new_flex_rank_higher = True
        elif (
            current_flex_value == highest_flex_value
            and current_flex_lp > highest_rank_data.highest_flex_lp
        ):
            is_new_flex_rank_higher = True
        if is_new_flex_rank_higher:
            highest_rank_data.highest_flex_tier = current_flex_tier
            highest_rank_data.highest_flex_rank = current_flex_rank
            highest_rank_data.highest_flex_lp = current_flex_lp
        await highest_rank_data.save()
        return highest_rank_data

    except DoesNotExist:
        new_rank_entry = await RtSearchModel.create(
            puuid=puuid,
            summoner_name=summoner_name,
            tag_line=tag_line,
            highest_solo_tier=current_solo_tier,
            highest_solo_rank=current_solo_rank,
            highest_solo_lp=current_solo_lp,
            highest_flex_tier=current_flex_tier,
            highest_flex_rank=current_flex_rank,
            highest_flex_lp=current_flex_lp,
            updated_at=datetime.datetime.now(),
        )
        return new_rank_entry
