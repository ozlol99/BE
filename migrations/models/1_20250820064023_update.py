from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `chatroom_participants` MODIFY COLUMN `position` VARCHAR(6) NOT NULL COMMENT '포지션';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `chatroom_participants` MODIFY COLUMN `position` VARCHAR(10) NOT NULL COMMENT '포지션';"""
