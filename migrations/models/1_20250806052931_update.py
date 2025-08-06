from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `refresh_tokens` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `token` VARCHAR(512) NOT NULL UNIQUE,
    `expires_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `revoked` BOOL NOT NULL DEFAULT 0,
    `user_id_id` INT NOT NULL,
    CONSTRAINT `fk_refresh__user_d914dcfb` FOREIGN KEY (`user_id_id`) REFERENCES `user` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS `refresh_tokens`;"""
