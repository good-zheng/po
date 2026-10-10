package com.goodzheng.po.novel.entity;

import com.baomidou.mybatisplus.annotation.FieldStrategy;
import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.time.LocalDateTime;

/**
 * 角色状态快照（C2「死人复活 / 越地知情」的依据）。
 *
 * <p>唯一键 (bookId, charKey, asOfChapter)：同一角色在同一章只有一份快照，
 * 因此抽取重放天然幂等。knows/holds 在库里是 JSON 列，实体侧按原始 JSON 文本存取。
 */
@Data
@TableName("character_state")
public class CharacterState {

    @TableId(type = IdType.AUTO)
    private Long id;

    private Long bookId;

    private String charKey;

    /** 该章结束时的快照 */
    private Integer asOfChapter;

    private Boolean isAlive;

    private String locationKey;

    /** 已知信息键，JSON 数组文本 */
    private String knows;

    /** 持有物，JSON 数组文本 */
    private String holds;

    private String mood;

    private Integer lastSeenChapter;

    @TableField(updateStrategy = FieldStrategy.NEVER)
    private LocalDateTime createdAt;
}
