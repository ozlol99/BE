from typing import TYPE_CHECKING

from tortoise import fields, models

if TYPE_CHECKING:
    from app.models.chat_room import ChatRoom


class HashTag(models.Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=50, unique=True, description="해시태그 이름")
    chat_rooms: fields.ManyToManyRelation["ChatRoom"]

    class Meta:
        table = "hashtags"

    def __str__(self):
        return self.name
