from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `rt_search` ADD `highest_solo_tier` VARCHAR(50) COMMENT '최고 랭크 티어';
        ALTER TABLE `rt_search` ADD `highest_solo_rank` VARCHAR(5) COMMENT '최고 랭크 디비전';
        ALTER TABLE `rt_search` ADD `highest_solo_lp` INT COMMENT '최고 리그 포인트';
        ALTER TABLE `rt_search` ADD `highest_flex_rank` VARCHAR(5) COMMENT '현재 랭크 디비전';
        ALTER TABLE `rt_search` ADD `highest_flex_lp` INT COMMENT '현재 리그 포인트';
        ALTER TABLE `rt_search` ADD `highest_flex_tier` VARCHAR(50) COMMENT '현재 랭크 티어';
        ALTER TABLE `rt_search` ADD `updated_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `rt_search` DROP COLUMN `highest_solo_tier`;
        ALTER TABLE `rt_search` DROP COLUMN `highest_solo_rank`;
        ALTER TABLE `rt_search` DROP COLUMN `highest_solo_lp`;
        ALTER TABLE `rt_search` DROP COLUMN `highest_flex_rank`;
        ALTER TABLE `rt_search` DROP COLUMN `highest_flex_lp`;
        ALTER TABLE `rt_search` DROP COLUMN `highest_flex_tier`;
        ALTER TABLE `rt_search` DROP COLUMN `updated_at`;"""
