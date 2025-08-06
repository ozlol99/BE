from enum import Enum

from tortoise import fields, models


class Social(str, Enum):
    google = "google"
    kakao = "kakao"


class UserModel(models.Model):
    id = fields.IntField(pk=True, auto_create=True)
    email = fields.CharField(unique=True, max_length=255, description="이메일")
    user = fields.CharField(null=True, max_length=255, description="닉네임")
    riot_user = fields.CharField(
        unique=True, max_length=255, null=True, description="라이엇 계정"
    )
    google_or_kakao = fields.CharEnumField(
        Social, null=False, description="소셜 계정 정보"
    )
    likes = fields.IntField(description="좋아요")
    created_at = fields.DatetimeField(auto_now=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "user"

    def __str__(self):
        return self.email
