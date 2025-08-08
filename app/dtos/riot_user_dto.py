from tortoise.contrib.pydantic import pydantic_model_creator
from app.models.rtSearch import rtSearchModel

rtSearch_Summoner_List = pydantic_model_creator(rtSearchModel, many=True)
