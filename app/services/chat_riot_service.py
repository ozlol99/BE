from typing import Any, Dict

import httpx
from fastapi import HTTPException, status

from app.config.settings import Settings

settings = Settings()

# Re-using the base URL and API key logic from the existing service
KR_BASE_URL = "https://kr.api.riotgames.com"
RIOT_API_KEY = settings.riot_api_key



async def get_summoner_rank_info(puuid: str) -> Dict[str, Any]:
    """
    Fetches summoner's rank information (solo and flex) by their PUUID.
    This logic is adapted from summoner_search_service.
    """
    if not RIOT_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="RIOT_API_KEY is not set.",
        )

    url = f"{KR_BASE_URL}/lol/league/v4/entries/by-puuid/{puuid}"
    headers = {"X-Riot-Token": RIOT_API_KEY}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()

        rank_data = {}
        for entry in data:
            queue_type = entry.get("queueType")
            if queue_type == "RANKED_SOLO_5x5":
                rank_data["solo_rank"] = {
                    "tier": entry.get("tier", "UNRANKED"),
                    "rank": entry.get("rank", ""),
                }

        # We can add flex rank or other info if needed later
        return rank_data

    except httpx.HTTPStatusError:
        # Log the error or handle it as needed
        return {}  # Return empty dict if summoner is not found or other error
    except Exception as e:
        # Log the error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}",
        )


def get_tier_icon_url(tier: str) -> str:
    """
    Returns the URL for a tier icon.
    (This is a placeholder, we might need a better way to get these URLs)
    """
    if not tier or tier == "UNRANKED":
        return "/static/tiers/unranked.png"
    return f"/static/tiers/{tier.lower()}.png"
