from __future__ import annotations

import enum
from typing import TYPE_CHECKING
from enum import Enum

from tortoise import fields, models

if TYPE_CHECKING:
    from app.models.user import UserModel
    from app.models.hash_tag import HashTag


class Queue(str, Enum):
    solo = "solo_lank"
    aram = "aram"
    flex = "flex"



class ChatRoom(models.Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100, description="채팅방 이름")
    owner: fields.ForeignKeyRelation[UserModel] = fields.ForeignKeyField(
        "models.UserModel", related_name="owned_chat_rooms", description="방장"
    )
    max_members = fields.IntField(description="최대 인원수", default=5)
    created_at = fields.DatetimeField(auto_now_add=True)
    queue_type = fields.CharEnumField(
        Queue,
        unique=True, max_length=30, null=True, description="Queue Type"
    )
    hashtags: fields.ManyToManyRelation[HashTag] = fields.ManyToManyField(
        "models.HashTag", related_name="chat_rooms", through="chatroom_hashtag"
    )


    class Meta:
        table = "chat_rooms"

    def __str__(self):
        return self.name
