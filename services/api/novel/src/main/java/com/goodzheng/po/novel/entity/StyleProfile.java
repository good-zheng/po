package com.goodzheng.po.novel.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

/**
 * 文风契约（§5.5）：每章都参与确定性校验的那一份约束。
 *
 * <p>三个 JSON 列（{@code forbiddenWords}/{@code tics}/{@code taboo}）在实体里保持字符串：
 * 本模块没有 JSON 类型处理器，Service 层写入前用 ObjectMapper 验一次「是字符串数组」，
 * 非法 JSON 挡在应用层比让 MySQL 抛 3140 好归因。
 *
 * <p>库约束 {@code (book_id)} 唯一：一本书一份契约，读写都是 upsert。
 */
@Data
@TableName("style_profile")
public class StyleProfile {

    @TableId(type = IdType.AUTO)
    private Long id;

    private Long bookId;

    /** 第几人称，如「第三人称限知」 */
    private String person;

    private String tense;

    private Integer sentenceLenMin;

    private Integer sentenceLenMax;

    private Integer chapterWordsMin;

    private Integer chapterWordsMax;

    /** JSON 字符串数组 */
    private String forbiddenWords;

    /** JSON 字符串数组，口头禅 */
    private String tics;

    /** JSON 字符串数组，禁项 */
    private String taboo;
}
