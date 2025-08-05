from tortoise import fields, models
from app.models.user import UserModel # User 모델 임포트

class RSOUser(models.Model):
    id = fields.IntField(pk=True)
    # User 모델의 riot_user 필드를 외래 키로 참조합니다.
    # riot_user 필드는 User 모델에서 반드시 unique 해야 합니다.
    user: fields.ForeignKeyRelation[UserModel] = fields.ForeignKeyField(
        "models.UserModel", related_name="rso_users", to_field="riot_user", on_delete=fields.CASCADE
    )
    # 여기에 RSO_user 모델에 필요한 다른 필드를 추가하세요.
    # 예시:
    # rso_account_id = fields.CharField(max_length=255, unique=True)
    # rso_token = fields.TextField()

    class Meta:
        table = "rso_users"
