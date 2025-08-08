from tortoise import fields, models


class RtSearchModel(models.Model):
    puuid = fields.CharField(max_length=78, unique=True)  # Riot의 puuid는 78자까지 가능
    summoner_name = fields.CharField(
        max_length=50, description="소환사 이름"
    )
    tag_line = fields.CharField(
        max_length=50, description="태그"
    )
    class Meta:
        table = "rt_search"

    def __str__(self):
        return self.token

