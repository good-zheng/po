package com.goodzheng.po.novel.dto;

import lombok.Data;

/** 握手票据校验出的作者身份（只回 uid：chat 侧要的就是「这是谁的读」） */
@Data
public class InternalActorView {

    private Long uid;
}
