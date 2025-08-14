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
    `user` VARCHAR(255) COMMENT '닉네임',
    `gender` INT COMMENT '성별 (null 가능)',
    `birthday` DATE COMMENT '생년월일 (null 가능)',
    `riot_user` VARCHAR(255) UNIQUE COMMENT '라이엇 계정',
    `google_or_kakao` VARCHAR(6) NOT NULL COMMENT '소셜 계정 정보',
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6)
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `user_likes` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `from_user_id` INT NOT NULL COMMENT '좋아요를 누른 사용자',
    `to_user_id` INT NOT NULL COMMENT '좋아요를 받은 사용자',
    UNIQUE KEY `uid_user_likes_from_us_8cee44` (`from_user_id`, `to_user_id`),
    CONSTRAINT `fk_user_lik_user_b46e7c66` FOREIGN KEY (`from_user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_user_lik_user_a4886358` FOREIGN KEY (`to_user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `token_blacklist` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `token` VARCHAR(500) NOT NULL UNIQUE COMMENT '블랙 리스트 토큰',
    `created_at` DATETIME(6) NOT NULL COMMENT '생성일' DEFAULT CURRENT_TIMESTAMP(6)
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `rso_users` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `user_id` VARCHAR(255) NOT NULL,
    CONSTRAINT `fk_rso_user_user_87c25ecc` FOREIGN KEY (`user_id`) REFERENCES `user` (`riot_user`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `refresh_tokens` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `token` VARCHAR(512) NOT NULL UNIQUE,
    `expires_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `revoked` BOOL NOT NULL DEFAULT 0,
    `user_id` INT NOT NULL,
    CONSTRAINT `fk_refresh__user_07a7a7a5` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `rt_search` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `puuid` VARCHAR(78) NOT NULL UNIQUE,
    `summoner_name` VARCHAR(50) NOT NULL COMMENT '소환사 이름',
    `tag_line` VARCHAR(50) NOT NULL COMMENT '태그',
    `highest_solo_tier` VARCHAR(50) COMMENT '최고 랭크 티어',
    `highest_solo_rank` VARCHAR(5) COMMENT '최고 랭크 디비전',
    `highest_solo_lp` INT COMMENT '최고 리그 포인트',
    `highest_flex_tier` VARCHAR(50) COMMENT '현재 랭크 티어',
    `highest_flex_rank` VARCHAR(5) COMMENT '현재 랭크 디비전',
    `highest_flex_lp` INT COMMENT '현재 리그 포인트',
    `updated_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6)
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
        """
