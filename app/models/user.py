from enum import Enum

from tortoise import fields, models


class Social(str, Enum):
    google = "google"
    kakao = "kakao"


class UserModel(models.Model):
    id = fields.IntField(pk=True, auto_create=True)
    email = fields.CharField(unique=True, max_length=255, description="이메일")
    user = fields.CharField(null=True, max_length=255, description="닉네임")
    gender = fields.IntField(null=True, description="성별 (null 가능)")
    birthday = fields.DateField(null=True, description="생년월일 (null 가능)")
    riot_user = fields.CharField(
        unique=True, max_length=255, null=True, description="라이엇 계정"
    )
    google_or_kakao = fields.CharEnumField(
        Social, null=False, description="소셜 계정 정보"
    )
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "user"

    def __str__(self):
        return self.email


# UserLikeModel: 유저 간의 좋아요 관계를 기록하는 테이블
class UserLikeModel(models.Model):
    id = fields.IntField(pk=True, auto_create=True)
    # from_user: 좋아요를 누른 사용자 (외래 키)
    from_user = fields.ForeignKeyField(  # type: ignore
        "models.UserModel",
        related_name="sent_likes",
        on_delete=fields.CASCADE,
        description="좋아요를 누른 사용자",
    )
    # to_user: 좋아요를 받은 사용자 (외래 키)
    to_user = fields.ForeignKeyField(  # type: ignore
        "models.UserModel",
        related_name="received_likes",
        on_delete=fields.CASCADE,
        description="좋아요를 받은 사용자",
    )
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "user_likes"
        unique_together = ("from_user", "to_user")  # 동일 유저가 한 번만 좋아요 가능

    def __str__(self):
        return f"{self.from_user.user} -> {self.to_user.user}"
