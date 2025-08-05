from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `user` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `email` VARCHAR(255) NOT NULL UNIQUE COMMENT '이메일',
    `user` VARCHAR(255) NOT NULL UNIQUE COMMENT '닉네임',
    `riot_user` VARCHAR(255) UNIQUE COMMENT '라이엇 계정',
    `google_or_kakao` VARCHAR(6) NOT NULL COMMENT '소셜 계정 정보',
    `likes` INT NOT NULL COMMENT '좋아요'
) CHARACTER SET utf8mb4;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS `user`;"""
