package com.goodzheng.po.talk.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import com.goodzheng.po.talk.constant.TalkConstants;
import java.time.LocalDateTime;
import lombok.Data;

/** 言外-会话：一次完整对话（从开始录音到结束）。threadId 对齐 LangGraph 的会话记忆。 */
@Data
@TableName("talk_session")
public class TalkSession {

    @TableId(type = IdType.AUTO)
    private Long id;

    private Long userId;

    /** LangGraph thread_id，同时是 /ws/chat 的 conversation_id */
    private String threadId;

    private String title;

    /** 场景: general通用, work职场, sales销售, romance亲密 */
    private String scene = TalkConstants.SCENE_GENERAL;

    /** 状态: recording进行中, ended已结束 */
    private String status = TalkConstants.STATUS_RECORDING;

    /** 对方话语轮次（不含「我」的话） */
    private Integer turnCount = 0;

    private Long durationMs = 0L;

    private LocalDateTime createdAt = LocalDateTime.now();

    private LocalDateTime updatedAt = LocalDateTime.now();
}
