from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `aerich` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `version` VARCHAR(255) NOT NULL,
    `app` VARCHAR(100) NOT NULL,
    `content` JSON NOT NULL
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `user` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `email` VARCHAR(255) NOT NULL UNIQUE COMMENT '이메일',
    `user` VARCHAR(255) NOT NULL UNIQUE COMMENT '닉네임',
    `gender` INT COMMENT '성별 (null 가능)',
    `birthday` DATE COMMENT '생년월일 (null 가능)',
    `riot_user` VARCHAR(255) UNIQUE COMMENT '라이엇 계정',
    `google_or_kakao` VARCHAR(6) NOT NULL COMMENT '소셜 계정 정보',
    `likes` INT NOT NULL COMMENT '좋아요' DEFAULT 0,
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6)
) CHARACTER SET utf8mb4;
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
        """
