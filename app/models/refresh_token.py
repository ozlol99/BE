from tortoise import fields, models


class RefreshTokenModel(models.Model):
    id = fields.IntField(pk=True)
    user_id = fields.ForeignKeyField("models.UserModel", related_name="refresh_tokens")
    token = fields.CharField(max_length=512, unique=True, null=False)
    expires_at = fields.DatetimeField(auto_now=True)
    updated_at = fields.DatetimeField(auto_now=True)
    revoked = fields.BooleanField(default=False)

    class Meta:
        table = "refresh_tokens"

    def __str__(self):
        return self.token
