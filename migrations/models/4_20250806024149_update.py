from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `user` DROP INDEX `user`;
        ALTER TABLE `user` ALTER COLUMN `likes` DROP DEFAULT;
        ALTER TABLE `user` MODIFY COLUMN `user` VARCHAR(255) COMMENT '닉네임';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `user` ALTER COLUMN `likes` SET DEFAULT 0;
        ALTER TABLE `user` MODIFY COLUMN `user` VARCHAR(255) NOT NULL COMMENT '닉네임';
        ALTER TABLE `user` ADD UNIQUE INDEX `user` (`user`);"""
