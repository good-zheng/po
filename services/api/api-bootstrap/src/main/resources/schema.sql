-- =========================================================
-- po 数据库建表脚本（替代原 JPA ddl-auto: update）
-- 启动时由 spring.sql.init 执行，幂等：表已存在则跳过
-- =========================================================

CREATE TABLE IF NOT EXISTS `sys_user` (
    `id`            BIGINT       NOT NULL AUTO_INCREMENT,
    `username`      VARCHAR(64)  NOT NULL,
    `password`      VARCHAR(100) NOT NULL,
    `email`         VARCHAR(255) DEFAULT NULL,
    `nickname`      VARCHAR(64)  DEFAULT NULL,
    `avatar`        VARCHAR(255) DEFAULT NULL,
    `first_name`    VARCHAR(64)  DEFAULT NULL,
    `last_name`     VARCHAR(64)  DEFAULT NULL,
    `phone_number`  VARCHAR(32)  DEFAULT NULL,
    `wechat_openid` VARCHAR(64)  DEFAULT NULL,
    `role`            VARCHAR(32)  NOT NULL DEFAULT 'user',
    `status`          VARCHAR(32)  NOT NULL DEFAULT 'active',
    `approval_status` VARCHAR(32)  NOT NULL DEFAULT 'approved',
    `create_time`   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `update_time`   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_sys_user_username` (`username`),
    UNIQUE KEY `uk_sys_user_wechat_openid` (`wechat_openid`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COMMENT ='用户表';

CREATE TABLE IF NOT EXISTS `recipe` (
    `id`               BIGINT        NOT NULL AUTO_INCREMENT,
    `title`            VARCHAR(255)  NOT NULL,
    `description`      TEXT          DEFAULT NULL,
    `cover_image_url`  VARCHAR(500)  DEFAULT NULL,
    `prep_time`        INT           DEFAULT NULL,
    `cook_time`        INT           DEFAULT NULL,
    `total_time`       INT           DEFAULT NULL,
    `difficulty`       INT           NOT NULL DEFAULT 1,
    `servings`         INT           DEFAULT NULL,
    `category`         VARCHAR(255)  DEFAULT NULL,
    `tags`             VARCHAR(500)  DEFAULT NULL,
    `author_id`        BIGINT        DEFAULT NULL,
    `is_public`        TINYINT(1)    NOT NULL DEFAULT 1,
    `likes_count`      INT           NOT NULL DEFAULT 0,
    `calories`         INT           DEFAULT NULL,
    `protein`          DOUBLE        DEFAULT NULL,
    `fat`              DOUBLE        DEFAULT NULL,
    `carbs`            DOUBLE        DEFAULT NULL,
    `tips`             TEXT          DEFAULT NULL,
    `flavor_profile`   VARCHAR(255)  DEFAULT NULL,
    `status`           VARCHAR(32)   NOT NULL DEFAULT 'approved' COMMENT '审核状态: pending待审核, approved已通过, rejected已驳回',
    `reject_reason`    VARCHAR(500)  DEFAULT NULL COMMENT '驳回原因',
    `deleted_at`       DATETIME      DEFAULT NULL,
    `created_at`       DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at`       DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `idx_recipe_author` (`author_id`),
    KEY `idx_recipe_deleted_at` (`deleted_at`),
    KEY `idx_recipe_status` (`status`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COMMENT ='菜谱表';

CREATE TABLE IF NOT EXISTS `recipe_ingredient` (
    `id`           BIGINT       NOT NULL AUTO_INCREMENT,
    `recipe_id`    BIGINT       NOT NULL,
    `name`         VARCHAR(255) NOT NULL,
    `amount`       VARCHAR(64)  DEFAULT NULL,
    `unit`         VARCHAR(32)  DEFAULT NULL,
    `is_essential` TINYINT(1)   NOT NULL DEFAULT 1,
    `sort_order`   INT          NOT NULL DEFAULT 0,
    `image_url`    VARCHAR(500) DEFAULT NULL,
    PRIMARY KEY (`id`),
    KEY `idx_recipe_ingredient_recipe` (`recipe_id`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COMMENT ='菜谱食材表';

CREATE TABLE IF NOT EXISTS `recipe_step` (
    `id`          BIGINT       NOT NULL AUTO_INCREMENT,
    `recipe_id`   BIGINT       NOT NULL,
    `step_number` INT          DEFAULT NULL,
    `content`     TEXT         DEFAULT NULL,
    `image_url`   VARCHAR(500) DEFAULT NULL,
    `video_url`   VARCHAR(500) DEFAULT NULL,
    `duration`    INT          DEFAULT NULL,
    PRIMARY KEY (`id`),
    KEY `idx_recipe_step_recipe` (`recipe_id`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COMMENT ='菜谱步骤表';

CREATE TABLE IF NOT EXISTS `recipe_category` (
    `id`          BIGINT       NOT NULL AUTO_INCREMENT,
    `name`        VARCHAR(64)  NOT NULL,
    `icon`        VARCHAR(255) DEFAULT NULL,
    `description` VARCHAR(500) DEFAULT NULL,
    `sort_order`  INT          NOT NULL DEFAULT 0,
    `deleted_at`  DATETIME     DEFAULT NULL,
    `created_at`  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at`  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COMMENT ='菜谱分类表';

CREATE TABLE IF NOT EXISTS `recipe_favorite` (
    `id`         BIGINT   NOT NULL AUTO_INCREMENT,
    `user_id`    BIGINT   NOT NULL,
    `recipe_id`  BIGINT   NOT NULL,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_favorite_user_recipe` (`user_id`, `recipe_id`),
    KEY `idx_favorite_recipe` (`recipe_id`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COMMENT ='菜谱收藏表';

CREATE TABLE IF NOT EXISTS `recipe_like` (
    `id`         BIGINT   NOT NULL AUTO_INCREMENT,
    `user_id`    BIGINT   NOT NULL,
    `recipe_id`  BIGINT   NOT NULL,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_like_user_recipe` (`user_id`, `recipe_id`),
    KEY `idx_like_recipe` (`recipe_id`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COMMENT ='菜谱点赞表';

CREATE TABLE IF NOT EXISTS `recipe_history` (
    `id`        BIGINT   NOT NULL AUTO_INCREMENT,
    `user_id`   BIGINT   NOT NULL,
    `recipe_id` BIGINT   NOT NULL,
    `viewed_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_history_user_recipe` (`user_id`, `recipe_id`),
    KEY `idx_history_recipe` (`recipe_id`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COMMENT ='菜谱浏览历史表';
