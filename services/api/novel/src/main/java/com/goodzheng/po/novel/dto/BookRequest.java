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
}
