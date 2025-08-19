from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `chatroom_participants` DROP FOREIGN KEY `fk_chatroom_position_878368bc`;
        ALTER TABLE `chatroom_participants` ADD `position` VARCHAR(10) NOT NULL COMMENT '포지션';
        ALTER TABLE `chatroom_participants` DROP COLUMN `position_id`;
        DROP TABLE IF EXISTS `positions`;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `chatroom_participants` ADD `position_id` INT NOT NULL;
        ALTER TABLE `chatroom_participants` DROP COLUMN `position`;
        ALTER TABLE `chatroom_participants` ADD CONSTRAINT `fk_chatroom_position_878368bc` FOREIGN KEY (`position_id`) REFERENCES `positions` (`id`) ON DELETE CASCADE;"""
