from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `user` ALTER COLUMN `likes` SET DEFAULT 0;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `user` ALTER COLUMN `likes` DROP DEFAULT;"""
