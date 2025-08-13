from tortoise import fields, models


class RtSearchModel(models.Model):
    puuid = fields.CharField(max_length=78, unique=True)  # Riot의 puuid는 78자까지 가능
    summoner_name = fields.CharField(max_length=50, description="소환사 이름")
    tag_line = fields.CharField(max_length=50, description="태그")
    
    highest_solo_tier = fields.CharField(max_length=50, null=True, description="최고 랭크 티어")
    highest_solo_rank = fields.CharField(max_length=5, null=True, description="최고 랭크 디비전")
    highest_solo_lp = fields.IntField(null=True, description="최고 리그 포인트")
    highest_flex_tier = fields.CharField(max_length=50, null=True, description="현재 랭크 티어")
    highest_flex_rank = fields.CharField(max_length=5, null=True, description="현재 랭크 디비전")
    highest_flex_lp = fields.IntField(null=True, description="현재 리그 포인트")
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "rt_search"

    def __str__(self):
        return self.token
