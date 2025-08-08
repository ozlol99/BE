from __future__ import annotations

from typing import TYPE_CHECKING

from tortoise import fields, models

if TYPE_CHECKING:
    from app.models.user import UserModel

class RefreshTokenModel(models.Model):
    id = fields.IntField(pk=True)
    user: fields.ForeignKeyRelation[UserModel] = fields.ForeignKeyField(
        "models.UserModel", related_name="refresh_tokens", source_field="user_id"
    )
    token = fields.CharField(max_length=512, unique=True, null=False)
    expires_at = fields.DatetimeField(auto_now=True)
    updated_at = fields.DatetimeField(auto_now=True)
    revoked = fields.BooleanField(default=False)

    class Meta:
        table = "refresh_tokens"

    def __str__(self):
        return self.token
