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

-- ==========================
-- 言外 EchoTalk：会话 / 话语 / 建议
-- ==========================
CREATE TABLE IF NOT EXISTS `talk_session` (
    `id`          BIGINT      NOT NULL AUTO_INCREMENT,
    `user_id`     BIGINT      NOT NULL,
    `thread_id`   VARCHAR(64) NOT NULL COMMENT 'LangGraph thread_id，同 /ws/chat 的 conversation_id',
    `title`       VARCHAR(128)         DEFAULT NULL COMMENT 'AI 生成标题',
    `scene`       VARCHAR(32) NOT NULL DEFAULT 'general' COMMENT '场景: general通用, work职场, sales销售, romance亲密',
    `status`      VARCHAR(16) NOT NULL DEFAULT 'recording' COMMENT '状态: recording进行中, ended已结束',
    `turn_count`  INT         NOT NULL DEFAULT 0 COMMENT '对方话语轮次',
    `duration_ms` BIGINT      NOT NULL DEFAULT 0,
    `created_at`  DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at`  DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_talk_session_thread` (`thread_id`),
    KEY `idx_talk_session_user` (`user_id`, `updated_at`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COMMENT ='言外-会话';

CREATE TABLE IF NOT EXISTS `talk_utterance` (
    `id`         BIGINT     NOT NULL AUTO_INCREMENT,
    `session_id` BIGINT     NOT NULL,
    `user_id`    BIGINT     NOT NULL,
    `seq`        INT        NOT NULL COMMENT '段内序号',
    `speaker`    VARCHAR(16) NOT NULL DEFAULT 'other' COMMENT '说话人: other对方, me我, unknown未知',
    `source`     VARCHAR(16) NOT NULL DEFAULT 'voice' COMMENT '来源: voice语音, text文字',
    `content`    TEXT       NOT NULL,
    `edited`     TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否被用户手工纠错',
    `confidence` DOUBLE              DEFAULT NULL COMMENT 'ASR 置信度',
    `start_ms`   BIGINT              DEFAULT NULL,
    `end_ms`     BIGINT              DEFAULT NULL,
    `created_at` DATETIME   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `idx_talk_utterance_session` (`session_id`, `seq`),
    KEY `idx_talk_utterance_user` (`user_id`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COMMENT ='言外-话语';

CREATE TABLE IF NOT EXISTS `talk_suggestion` (
    `id`           BIGINT      NOT NULL AUTO_INCREMENT,
    `session_id`   BIGINT      NOT NULL,
    `utterance_id` BIGINT      NOT NULL,
    `user_id`      BIGINT      NOT NULL,
    `model`        VARCHAR(64)          DEFAULT NULL,
    `intent`       VARCHAR(512)         DEFAULT NULL COMMENT '对方真正想要的',
    `subtext`      VARCHAR(512)         DEFAULT NULL COMMENT '潜台词',
    `emotion`      VARCHAR(32)          DEFAULT NULL COMMENT '情绪标签',
    `risk`         VARCHAR(512)         DEFAULT NULL COMMENT '风险提示',
    -- 完整结构化结果（含 suggestions / followups）的 JSON 文本
    `payload`      LONGTEXT             DEFAULT NULL,
    `latency_ms`   INT                  DEFAULT NULL,
    `created_at`   DATETIME   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `idx_talk_suggestion_utterance` (`utterance_id`),
    KEY `idx_talk_suggestion_session` (`session_id`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COMMENT ='言外-建议';

-- =========================================================
-- 小说业务线（恢复自 b23a633^，列宽按旧 DDL；新增列见 NOVEL_AGENT_PRD.md §5/§10）
-- 坑：本地这三张表可能由 JPA ddl-auto 建过（列宽偏窄、content 是 TEXT）。
--     CREATE TABLE IF NOT EXISTS 不会修正已存在的表，所以老库必须跑 scripts/novel-migrate.mjs
-- =========================================================

CREATE TABLE IF NOT EXISTS `book` (
    `id`          BIGINT       NOT NULL AUTO_INCREMENT,
    `author_id`   BIGINT       NOT NULL,
    `title`       VARCHAR(255) NOT NULL,
    `description` TEXT         DEFAULT NULL,
    `cover_image` VARCHAR(500) DEFAULT NULL,
    `genre`       VARCHAR(64)  DEFAULT NULL,
    `status`      VARCHAR(32)  NOT NULL DEFAULT 'ongoing',
    `word_count`  INT          NOT NULL DEFAULT 0,
    `author`      VARCHAR(64)  DEFAULT NULL,
    -- Tier-0 常驻注入用，不是 description 那种对外简介文案
    `summary`     TEXT         DEFAULT NULL COMMENT '世界观摘要 + 主线进度',
    `deleted_at`  DATETIME     DEFAULT NULL,
    `created_at`  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at`  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `idx_book_author` (`author_id`),
    KEY `idx_book_deleted_at` (`deleted_at`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COMMENT ='书籍表';

CREATE TABLE IF NOT EXISTS `book_chapter` (
    `id`            BIGINT       NOT NULL AUTO_INCREMENT,
    `book_id`       BIGINT       NOT NULL,
    `chapter_index` INT          DEFAULT NULL,
    `title`         VARCHAR(255) NOT NULL,
    -- 必须 LONGTEXT：TEXT 上限 64KB，utf8mb4 下约 2.1 万字就会被静默截断
    `content`       LONGTEXT     DEFAULT NULL,
    `word_count`    INT          NOT NULL DEFAULT 0,
    `status`        VARCHAR(16)  NOT NULL DEFAULT 'draft' COMMENT 'draft草稿/pending_review待复核/committed已定稿',
    `revision`      INT          NOT NULL DEFAULT 1 COMMENT '每次保存加 1，出处与黄金集按 chapter_id+revision 引用',
    `deleted_at`    DATETIME     DEFAULT NULL,
    `created_at`    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at`    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `idx_book_chapter_book` (`book_id`),
    KEY `idx_book_chapter_status` (`book_id`, `status`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COMMENT ='书籍章节表';

CREATE TABLE IF NOT EXISTS `book_character` (
    `id`          BIGINT       NOT NULL AUTO_INCREMENT,
    `book_id`     BIGINT       NOT NULL,
    `name`        VARCHAR(128) NOT NULL,
    `description` TEXT         DEFAULT NULL,
    `avatar`      VARCHAR(500) DEFAULT NULL,
    `deleted_at`  DATETIME     DEFAULT NULL,
    `created_at`  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at`  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `idx_book_character_book` (`book_id`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COMMENT ='书籍角色表';

-- =========================================================
-- L0 正典层（§5）：断言级而非卡片级、append-only 演进、读侧永远带 as-of 章节过滤
-- =========================================================

CREATE TABLE IF NOT EXISTS `canon_entry` (
    `id`                  BIGINT        NOT NULL AUTO_INCREMENT,
    `book_id`             BIGINT        NOT NULL,
    `kind`                VARCHAR(24)   NOT NULL COMMENT 'world_rule/character/relation/location/item/theme/style',
    `subject_key`         VARCHAR(128)  NOT NULL COMMENT '别名归一后的实体键，如 char:shenqing',
    `predicate`           VARCHAR(64)   NOT NULL COMMENT '机器可比谓词，如 eye_color/is_alive/cannot_use',
    `object_text`         VARCHAR(512)  NOT NULL COMMENT '值，比对用它',
    `restatement`         VARCHAR(512)  DEFAULT NULL COMMENT '给提示词读的自然语言句，注入用它',
    `authority`           VARCHAR(16)   NOT NULL DEFAULT 'model' COMMENT 'author/text/model，由服务端判定',
    `confidence`          DECIMAL(3, 2) NOT NULL DEFAULT 1.00 COMMENT 'author 恒 1.00',
    `established_chapter` INT           DEFAULT NULL COMMENT '第几章确立，NULL 表示开篇即有的全局设定',
    `valid_from_chapter`  INT           NOT NULL DEFAULT 0,
    `valid_until_chapter` INT           DEFAULT NULL COMMENT 'NULL 至今有效；演进靠闭区间而非覆盖',
    `supersedes_id`       BIGINT        DEFAULT NULL COMMENT '被本条取代的旧断言',
    `status`              VARCHAR(16)   NOT NULL DEFAULT 'confirmed' COMMENT 'confirmed/disputed/todo(缺口)/rejected',
    `source_chapter_id`   BIGINT        DEFAULT NULL,
    `source_start`        INT           DEFAULT NULL,
    `source_end`          INT           DEFAULT NULL,
    `evidence_quote`      VARCHAR(512)  DEFAULT NULL COMMENT '入库时的原文逐字片段，作者改正文后按它重定位',
    `prompt_version`      VARCHAR(32)   DEFAULT NULL,
    `model`               VARCHAR(64)   DEFAULT NULL,
    `decided_by`          BIGINT        DEFAULT NULL COMMENT '作者裁定人，authority=author 时必填',
    `decided_at`          DATETIME      DEFAULT NULL,
    `created_at`          DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at`          DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `idx_canon_asof` (`book_id`, `valid_from_chapter`, `valid_until_chapter`),
    KEY `idx_canon_subject` (`book_id`, `subject_key`, `predicate`),
    KEY `idx_canon_status` (`book_id`, `status`),
    KEY `idx_canon_source` (`source_chapter_id`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COMMENT ='正典断言';

CREATE TABLE IF NOT EXISTS `character_state` (
    `id`                BIGINT       NOT NULL AUTO_INCREMENT,
    `book_id`           BIGINT       NOT NULL,
    `char_key`          VARCHAR(128) NOT NULL,
    `as_of_chapter`     INT          NOT NULL COMMENT '该章结束时的快照',
    `is_alive`          TINYINT(1)   NOT NULL DEFAULT 1,
    `location_key`      VARCHAR(128) DEFAULT NULL,
    `knows`             JSON         DEFAULT NULL COMMENT '已知信息键，判越地知情',
    `holds`             JSON         DEFAULT NULL COMMENT '持有物',
    `mood`              VARCHAR(64)  DEFAULT NULL,
    `last_seen_chapter` INT          DEFAULT NULL,
    `created_at`        DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_state_chapter` (`book_id`, `char_key`, `as_of_chapter`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COMMENT ='角色状态快照，C2 生死与在场的依据';

CREATE TABLE IF NOT EXISTS `foreshadow` (
    `id`              BIGINT       NOT NULL AUTO_INCREMENT,
    `book_id`         BIGINT       NOT NULL,
    `planted_chapter` INT          NOT NULL,
    `content`         VARCHAR(512) NOT NULL,
    `due_by_arc`      INT          DEFAULT NULL,
    `payoff_chapter`  INT          DEFAULT NULL COMMENT 'NULL 表示未收',
    `status`          VARCHAR(16)  NOT NULL DEFAULT 'opened' COMMENT 'opened/paid/abandoned',
    `created_at`      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `idx_foreshadow_open` (`book_id`, `status`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COMMENT ='伏笔台账，C6 烂尾的抓手';

CREATE TABLE IF NOT EXISTS `alias` (
    `id`                 BIGINT       NOT NULL AUTO_INCREMENT,
    `book_id`            BIGINT       NOT NULL,
    `entity_key`         VARCHAR(128) NOT NULL,
    `alias_text`         VARCHAR(128) NOT NULL,
    `first_seen_chapter` INT          DEFAULT NULL,
    `is_primary`         TINYINT(1)   NOT NULL DEFAULT 0,
    PRIMARY KEY (`id`),
    -- 同一书内一个称谓只能指向一个实体，把 C3 的一人多名与多名同人挡在库约束层
    UNIQUE KEY `uk_alias_per_book` (`book_id`, `alias_text`),
    KEY `idx_alias_entity` (`book_id`, `entity_key`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COMMENT ='称谓别名表，抽取与检测先归一再比对';

CREATE TABLE IF NOT EXISTS `timeline_anchor` (
    `id`                  BIGINT        NOT NULL AUTO_INCREMENT,
    `book_id`             BIGINT        NOT NULL,
    `chapter_no`          INT           NOT NULL,
    `story_time_label`    VARCHAR(64)   DEFAULT NULL COMMENT '如第三日黄昏',
    `story_time_absolute` DATETIME      DEFAULT NULL,
    `duration_days`       DECIMAL(7, 2) DEFAULT NULL COMMENT '本章跨越天数，判三天后到达十天路程这类越界',
    `upstream_event_key`  VARCHAR(128)  DEFAULT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_timeline_chapter` (`book_id`, `chapter_no`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COMMENT ='时间锚点，C4 区间越界检查';

CREATE TABLE IF NOT EXISTS `style_profile` (
    `id`                BIGINT      NOT NULL AUTO_INCREMENT,
    `book_id`           BIGINT      NOT NULL,
    `person`            VARCHAR(16) DEFAULT NULL COMMENT '第几人称',
    `tense`             VARCHAR(16) DEFAULT NULL,
    `sentence_len_min`  INT         DEFAULT NULL,
    `sentence_len_max`  INT         DEFAULT NULL,
    `chapter_words_min` INT         DEFAULT NULL,
    `chapter_words_max` INT         DEFAULT NULL,
    `forbidden_words`   JSON        DEFAULT NULL,
    `tics`              JSON        DEFAULT NULL COMMENT '口头禅',
    `taboo`             JSON        DEFAULT NULL COMMENT '禁项',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_style_book` (`book_id`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COMMENT ='文风契约，每章参与确定性校验';

CREATE TABLE IF NOT EXISTS `scene_plan` (
    `id`            BIGINT       NOT NULL AUTO_INCREMENT,
    `book_id`       BIGINT       NOT NULL,
    `chapter_index` INT          NOT NULL,
    `scene_no`      INT          NOT NULL,
    `goal`          VARCHAR(512) DEFAULT NULL COMMENT '本场景要发生什么',
    `entities`      JSON         DEFAULT NULL COMMENT '涉及的实体键，先抽实体再检索',
    `must_change`   JSON         DEFAULT NULL COMMENT '必须改变的状态',
    `must_not`      JSON         DEFAULT NULL COMMENT '禁止出现的事',
    `status`        VARCHAR(16)  NOT NULL DEFAULT 'pending' COMMENT 'pending/approved/rejected，计划闸门 A 的产物',
    `created_at`    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_scene_no` (`book_id`, `chapter_index`, `scene_no`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COMMENT ='场景卡';

CREATE TABLE IF NOT EXISTS `review_finding` (
    `id`              BIGINT       NOT NULL AUTO_INCREMENT,
    `book_id`         BIGINT       NOT NULL,
    `chapter_id`      BIGINT       NOT NULL,
    `revision`        INT          NOT NULL DEFAULT 1 COMMENT '挂版本，作者改正文不会让已录样本失效',
    `code`            VARCHAR(32)  NOT NULL COMMENT '冲突编码，对应 C1-C6',
    `severity`        VARCHAR(16)  NOT NULL COMMENT 'blocker/major/minor',
    `checker`         VARCHAR(16)  NOT NULL COMMENT 'rule 规则引擎 / judge 语义裁判',
    `canon_refs`      JSON         DEFAULT NULL COMMENT '被违反的 canon 编号列表',
    `text_start`      INT          DEFAULT NULL,
    `text_end`        INT          DEFAULT NULL,
    `evidence_quote`  VARCHAR(512) DEFAULT NULL COMMENT '裁判必须引原文，与正文逐字相等才收下',
    `explanation`     VARCHAR(512) DEFAULT NULL,
    `fix_instruction` VARCHAR(512) DEFAULT NULL COMMENT '定向修补指令',
    `status`          VARCHAR(16)  NOT NULL DEFAULT 'open' COMMENT 'open/adopted/rejected/waived/orphaned',
    `decided_by`      BIGINT       DEFAULT NULL,
    `decided_at`      DATETIME     DEFAULT NULL,
    `basis`           VARCHAR(512) DEFAULT NULL COMMENT '裁定依据',
    `created_at`      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_finding_dedup` (`chapter_id`, `revision`, `code`, `checker`, `text_start`),
    KEY `idx_finding_book_status` (`book_id`, `status`),
    KEY `idx_finding_severity` (`book_id`, `severity`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COMMENT ='冲突台账，双闸门的产物';

CREATE TABLE IF NOT EXISTS `gen_job` (
    `id`              BIGINT        NOT NULL AUTO_INCREMENT,
    `book_id`         BIGINT        NOT NULL,
    `chapter_index`   INT           DEFAULT NULL,
    `stage`           VARCHAR(32)   NOT NULL COMMENT 'queued/writing/gating/awaiting_review/committed/failed',
    `idempotency_key` VARCHAR(128)  NOT NULL COMMENT 'chapter_id+content_hash+prompt_version+model',
    `retry_count`     INT           NOT NULL DEFAULT 0,
    `last_error`      VARCHAR(512)  DEFAULT NULL COMMENT '写库失败必须有终态，不许仅记日志',
    `created_at`      DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at`      DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_job_idempotency` (`idempotency_key`),
    KEY `idx_job_book` (`book_id`, `stage`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COMMENT ='生成任务与幂等键';

CREATE TABLE IF NOT EXISTS `chapter_summary` (
    `id`             BIGINT      NOT NULL AUTO_INCREMENT,
    `book_id`        BIGINT      NOT NULL,
    `chapter_id`     BIGINT      DEFAULT NULL COMMENT 'arc 级为 NULL',
    `level`          VARCHAR(16) NOT NULL COMMENT 'scene/chapter/arc，层级摘要，禁止摘要的摘要',
    `scene_no`       INT         DEFAULT NULL,
    -- 覆盖区间：scene/chapter 级 from=to=该章序号，arc 级跨章；读侧按「整段 <= as-of」判已知，防剧透
    `from_chapter`   INT         DEFAULT NULL COMMENT '覆盖区间起始章',
    `to_chapter`     INT         DEFAULT NULL COMMENT '覆盖区间结束章',
    `content`        TEXT        NOT NULL,
    `tokens`         INT         DEFAULT NULL COMMENT '预算核算，注入超限要能看见',
    -- 可空：arc 级不对应某一章正文，没有 revision 可记；DEFAULT 1 会把它伪造成「版本 1 且永不过期」
    `source_version` INT         DEFAULT NULL COMMENT '来源正文版本，正文改了则过期重算；arc 级为 NULL',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_summary_level` (`book_id`, `chapter_id`, `level`, `scene_no`),
    KEY `idx_summary_arc` (`book_id`, `level`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COMMENT ='层级摘要树 scene-chapter-arc-book';

CREATE TABLE IF NOT EXISTS `canon_proposal` (
    `id`                 BIGINT       NOT NULL AUTO_INCREMENT,
    `book_id`            BIGINT       NOT NULL,
    `session_id`         VARCHAR(64)  DEFAULT NULL COMMENT '对话会话，便于回溯是哪次聊出来的',
    `as_of_chapter`      INT          DEFAULT NULL,
    `kind`               VARCHAR(24)  NOT NULL,
    `subject_key`        VARCHAR(128) NOT NULL,
    `predicate`          VARCHAR(64)  NOT NULL,
    `object_text`        VARCHAR(512) NOT NULL,
    `valid_from_chapter` INT          DEFAULT NULL,
    `basis_quote`        VARCHAR(512) DEFAULT NULL COMMENT '依据：引哪一章哪一句',
    `status`             VARCHAR(16)  NOT NULL DEFAULT 'pending' COMMENT 'pending/adopted/dismissed/expired',
    `adopted_entry_id`   BIGINT       DEFAULT NULL,
    `decided_by`         BIGINT       DEFAULT NULL,
    `decided_at`         DATETIME     DEFAULT NULL,
    `decided_basis`      VARCHAR(512) DEFAULT NULL COMMENT '驳回依据：卡片内容留下了，为什么不要它必须也留下',
    `created_at`         DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `idx_proposal_pending` (`book_id`, `status`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COMMENT ='对话面板的提议卡，未采纳永不参与注入';

CREATE TABLE IF NOT EXISTS `chapter_revision` (
    `id`           BIGINT       NOT NULL AUTO_INCREMENT,
    `chapter_id`   BIGINT       NOT NULL,
    `revision`     INT          NOT NULL,
    `content`      LONGTEXT     NOT NULL,
    `content_hash` VARCHAR(64)  DEFAULT NULL,
    `created_by`   BIGINT       DEFAULT NULL COMMENT '作者手改记 user_id，Agent 写记 NULL',
    `created_at`   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_revision` (`chapter_id`, `revision`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COMMENT ='章节历史版本，旧文不覆盖';
