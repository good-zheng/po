package com.goodzheng.po.talk.dto;

import com.goodzheng.po.talk.constant.TalkConstants;
import lombok.Data;

/** 创建会话。场景决定 agent-talk 的分析视角。 */
@Data
public class CreateSessionRequest {

    /** 场景: general通用, work职场, sales销售, romance亲密；缺省 general */
    private String scene = TalkConstants.SCENE_GENERAL;
}
