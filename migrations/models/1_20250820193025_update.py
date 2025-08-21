from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `chat_rooms` DROP INDEX `queue_type`;
        ALTER TABLE `chatroom_participants` MODIFY COLUMN `position` VARCHAR(6) NOT NULL COMMENT '포지션';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `chatroom_participants` MODIFY COLUMN `position` VARCHAR(10) NOT NULL COMMENT '포지션';
        ALTER TABLE `chat_rooms` ADD UNIQUE INDEX `queue_type` (`queue_type`);"""
