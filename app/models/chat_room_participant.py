from __future__ import annotations

from typing import TYPE_CHECKING

from tortoise import fields, models

from app.models.chat_room import PositionEnum

if TYPE_CHECKING:
    from app.models.chat_room import ChatRoom
    from app.models.riot_account import RiotAccount
    from app.models.user import UserModel


class ChatRoomParticipant(models.Model):
    id = fields.IntField(pk=True)
    user: fields.ForeignKeyRelation[UserModel] = fields.ForeignKeyField(
        "models.UserModel", related_name="participating_rooms"
    )
    room: fields.ForeignKeyRelation[ChatRoom] = fields.ForeignKeyField(
        "models.ChatRoom", related_name="participants"
    )
    riot_account: fields.ForeignKeyRelation[RiotAccount] = fields.ForeignKeyField(
        "models.RiotAccount", related_name="room_presences"
    )
    position = fields.CharEnumField(PositionEnum, description="포지션")
    joined_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "chatroom_participants"
        unique_together = (("room", "user"), ("room", "position"))

    def __str__(self):
        return f"User {self.user_id} in Room {self.room_id} as {self.position}"
