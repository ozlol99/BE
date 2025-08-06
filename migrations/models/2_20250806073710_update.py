from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `refresh_tokens` DROP FOREIGN KEY `fk_refresh__user_d914dcfb`;
        ALTER TABLE `refresh_tokens` RENAME COLUMN `user_id_id` TO `user_id`;
        ALTER TABLE `refresh_tokens` ADD CONSTRAINT `fk_refresh__user_07a7a7a5` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `refresh_tokens` DROP FOREIGN KEY `fk_refresh__user_07a7a7a5`;
        ALTER TABLE `refresh_tokens` RENAME COLUMN `user_id` TO `user_id_id`;
        ALTER TABLE `refresh_tokens` ADD CONSTRAINT `fk_refresh__user_d914dcfb` FOREIGN KEY (`user_id_id`) REFERENCES `user` (`id`) ON DELETE CASCADE;"""
