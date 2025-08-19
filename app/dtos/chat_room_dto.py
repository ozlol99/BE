from typing import List, Optional

from pydantic import BaseModel, Field

from app.models.chat_room import Queue


class ChatRoomCreateDTO(BaseModel):
    name: str = Field(..., description="채팅방 이름")
    max_members: int = Field(..., description="최대 인원수")
    queue_type: Queue = Field(..., description="큐 타입")
    hashtags: Optional[List[str]] = Field(
        None, max_length=3, description="해시태그 목록 (최대 3개)"
    )
