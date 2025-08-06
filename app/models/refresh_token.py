# from tortoise import fields, models
# #
# #
# # class RefreshToken(models.Model):
# #     id = fields.IntField(pk=True)
# #     user_id = fields.ForeignKeyField("models.User", related_name="refresh_tokens")
# #     token = fields.TextField(unique=True, null=False)
# #     expires_at = fields.DatetimeField(auto_now=True)
# #     updated_at = fields.DatetimeField(auto_now=True)
# #     revoked = fields.BooleanField(default=False)
