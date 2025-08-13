from __future__ import annotations

from typing import TYPE_CHECKING

from tortoise import fields, models

if TYPE_CHECKING:
    from app.models.user import UserModel


class ChatRoom(models.Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100, description="채팅방 이름")
    owner: fields.ForeignKeyRelation[UserModel] = fields.ForeignKeyField(
        "models.UserModel", related_name="owned_chat_rooms", description="방장"
    )
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "chat_rooms"

    def __str__(self):
        return self.name
