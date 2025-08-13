from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `rt_search` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `puuid` VARCHAR(78) NOT NULL UNIQUE,
    `summoner_name` VARCHAR(50) NOT NULL COMMENT '소환사 이름',
    `tag_line` VARCHAR(50) NOT NULL COMMENT '태그'
) CHARACTER SET utf8mb4;
        CREATE TABLE IF NOT EXISTS `chat_rooms` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `name` VARCHAR(100) NOT NULL COMMENT '채팅방 이름',
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `owner_id` INT NOT NULL COMMENT '방장',
    CONSTRAINT `fk_chat_roo_user_42dc1056` FOREIGN KEY (`owner_id`) REFERENCES `user` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS `chat_rooms`;
        DROP TABLE IF EXISTS `rt_search`;"""
