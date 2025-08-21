from datetime import datetime
from typing import Optional

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
