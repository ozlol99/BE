from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class UserDTO(BaseModel):
    email: str = Field(..., max_length=255, description="이메일")
    user: str = Field(..., max_length=255, description="닉네임")
    google_or_kakao: Literal["google", "kakao"] = Field(
        ..., description="소셜 계정 정보"
    )
    gender: Optional[bool] = Field(None, description="성별 (true: 남성, false: 여성)")
    birthday: Optional[datetime] = Field(None, description="생년월일")
