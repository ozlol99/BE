from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `rt_search` ADD `puuid` VARCHAR(78) NOT NULL UNIQUE;
        ALTER TABLE `rt_search` ADD UNIQUE INDEX `puuid` (`puuid`);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `rt_search` DROP INDEX `puuid`;
        ALTER TABLE `rt_search` DROP COLUMN `puuid`;"""
