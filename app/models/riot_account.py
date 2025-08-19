from __future__ import annotations

from typing import TYPE_CHECKING

from tortoise import fields, models

if TYPE_CHECKING:
    from app.models.user import UserModel


class RiotAccount(models.Model):
    id = fields.IntField(pk=True)
    user: fields.ForeignKeyRelation[UserModel] = fields.ForeignKeyField(
        "models.UserModel", related_name="riot_accounts", description="소유자"
    )
    game_name = fields.CharField(max_length=50, description="라이엇 게임 이름")
    tag_line = fields.CharField(max_length=10, description="태그 라인")
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "riot_accounts"
        unique_together = ("game_name", "tag_line")

    def __str__(self):
        return f"{self.game_name}#{self.tag_line}"
