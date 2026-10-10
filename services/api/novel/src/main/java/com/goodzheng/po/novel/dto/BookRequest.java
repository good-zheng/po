package com.goodzheng.po.novel.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.Data;

@Data
public class BookRequest {

    @NotBlank(message = "书籍名称不能为空")
    private String title;

    private String description;
    private String coverImage;
    private String genre;
    private String author;

    /** 创作状态: ongoing-连载中, completed-已完结, paused-暂停更新 */
    private String status;

    /** Tier-0 常驻注入的世界观摘要 + 主线进度；对外简介是 description，两者不可互相覆盖 */
    private String summary;
}
