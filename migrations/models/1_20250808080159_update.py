from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `rt_search` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `summoner_name` VARCHAR(50) NOT NULL COMMENT '소환사 이름',
    `tag_line` VARCHAR(50) NOT NULL COMMENT '태그'
) CHARACTER SET utf8mb4;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS `rt_search`;"""
