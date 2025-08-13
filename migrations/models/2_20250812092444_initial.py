from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `user_likes` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `from_user_id` INT NOT NULL COMMENT '좋아요를 누른 사용자',
    `to_user_id` INT NOT NULL COMMENT '좋아요를 받은 사용자',
    UNIQUE KEY `uid_user_likes_from_us_8cee44` (`from_user_id`, `to_user_id`),
    CONSTRAINT `fk_user_lik_user_b46e7c66` FOREIGN KEY (`from_user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_user_lik_user_a4886358` FOREIGN KEY (`to_user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;
        ALTER TABLE `user` DROP COLUMN `likes`;
        ALTER TABLE `user` MODIFY COLUMN `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6);
        ALTER TABLE `rt_search` ADD `puuid` VARCHAR(78) NOT NULL UNIQUE;
        ALTER TABLE `rt_search` ADD UNIQUE INDEX `puuid` (`puuid`);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `rt_search` DROP INDEX `puuid`;
        ALTER TABLE `user` ADD `likes` INT NOT NULL COMMENT '좋아요' DEFAULT 0;
        ALTER TABLE `user` MODIFY COLUMN `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6);
        ALTER TABLE `rt_search` DROP COLUMN `puuid`;
        DROP TABLE IF EXISTS `user_likes`;"""
