
from tortoise.contrib.pydantic import pydantic_model_creator

from app.models.rtSearch import RtSearchModel

RiotUser_Pydantic = pydantic_model_creator(RtSearchModel)

