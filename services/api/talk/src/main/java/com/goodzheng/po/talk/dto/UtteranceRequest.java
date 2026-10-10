package com.goodzheng.po.talk.dto;

import com.goodzheng.po.talk.constant.TalkConstants;
import jakarta.validation.constraints.NotBlank;
import lombok.Data;

/** 保存一句话：语音定稿或手动输入，两种来源走同一条落库路径。 */
@Data
public class UtteranceRequest {

    /** 说话人: other对方, me我；缺省 other */
    private String speaker = TalkConstants.SPEAKER_OTHER;

    /** 来源: voice语音, text文字；缺省 voice */
    private String source = TalkConstants.SOURCE_VOICE;

    @NotBlank(message = "内容不能为空")
    private String content;

    /** ASR 置信度，文字输入不传 */
    private Double confidence;

    /** 相对会话开始的毫秒偏移 */
    private Long startMs;

    private Long endMs;
}
