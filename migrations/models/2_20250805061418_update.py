from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `user` ADD `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6);
        ALTER TABLE `user` ADD `updated_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6);
        CREATE TABLE IF NOT EXISTS `token_blacklist` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `token` VARCHAR(500) NOT NULL UNIQUE COMMENT '블랙리스트 토큰',
    `created_at` DATETIME(6) NOT NULL COMMENT '생성일' DEFAULT CURRENT_TIMESTAMP(6)
) CHARACTER SET utf8mb4;
        CREATE TABLE IF NOT EXISTS `rso_users` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `user_id` VARCHAR(255) NOT NULL,
    CONSTRAINT `fk_rso_user_user_87c25ecc` FOREIGN KEY (`user_id`) REFERENCES `user` (`riot_user`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `user` DROP COLUMN `created_at`;
        ALTER TABLE `user` DROP COLUMN `updated_at`;
        DROP TABLE IF EXISTS `rso_users`;
        DROP TABLE IF EXISTS `token_blacklist`;"""
