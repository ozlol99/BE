from tortoise.contrib.pydantic import pydantic_model_creator

from app.models.search_summoner import RtSearchModel

RiotUser_Pydantic = pydantic_model_creator(RtSearchModel)
