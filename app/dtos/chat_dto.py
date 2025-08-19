from typing import Annotated, List, Optional

from pydantic import BaseModel, Field

from app.models.chat_room import Queue
from app.models.position import PositionEnum

Hashtags = Annotated[list[str], Field(max_items=3)]


class HashtagResponse(BaseModel):
    id: int
    name: str


class ChatRoomCreate(BaseModel):
    name: str = Field(..., max_length=100)
    max_members: int = Field(..., ge=2, le=5)
    queue_type: Queue
    hashtags: Hashtags | None = None


class ChatRoomUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    hashtags: Hashtags | None = None


class JoinRoomRequest(BaseModel):
    riot_account_id: int
    position: PositionEnum


class ParticipantRiotAccountResponse(BaseModel):
    game_name: str
    tag_line: str


class ParticipantResponse(BaseModel):
    user_id: int
    nickname: str
    position: str
    riot_account: ParticipantRiotAccountResponse
    tier_icon_url: str


class ChatRoomDetailResponse(BaseModel):
    id: int
    name: str
    owner_id: int
    max_members: int
    current_members: int
    queue_type: str
    hashtags: List[HashtagResponse]
    participants: List[ParticipantResponse]


class ChatRoomCardResponse(BaseModel):
    id: int
    name: str
    current_members: int
    max_members: int
    queue_type: str
    hashtags: List[HashtagResponse]
    owner_nickname: str
    created_ago: str
