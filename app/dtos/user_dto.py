from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class UserDTO(BaseModel):
    user: str = Field(..., max_length=255, description="닉네임")
    gender: Optional[bool] = Field(None, description="성별 (true: 남성, false: 여성)")
    birthday: Optional[datetime] = Field(None, description="생년월일")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserUpdate(BaseModel):
    user: str = Field(..., max_length=255, description="닉네임")
    gender: Optional[bool] = Field(None, description="성별 (true: 남성, false: 여성)")
    birthday: Optional[datetime] = Field(None, description="생년월일")


class RiotAccountResponse(BaseModel):
    id: int
    game_name: str
    tag_line: str

    class Config:
        from_attributes = True


class UserMeResponse(BaseModel):
    id: int
    email: str
    user: str
    google_or_kakao: str
    riot_accounts: List[RiotAccountResponse]