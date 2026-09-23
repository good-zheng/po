package com.goodzheng.po.recipe.dto;

import lombok.AllArgsConstructor;
import lombok.Data;

/** 点赞切换结果 */
@Data
@AllArgsConstructor
public class LikeResult {

    /** 切换后的点赞状态 */
    private boolean liked;

    private int likesCount;
}
