from typing import Literal
from pydantic import BaseModel, Field

class UserDTO(BaseModel):
    email: str = Field(..., max_length=255, description="이메일", unique=True)
    user: str = Field(..., max_length=255, description="닉네임", unique=True)
    google_or_kakao: Literal["google", "kakao"] = Field(..., description="소셜 계정 정보")
