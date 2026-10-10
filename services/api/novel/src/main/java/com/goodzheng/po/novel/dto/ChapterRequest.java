package com.goodzheng.po.novel.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.Data;

@Data
public class ChapterRequest {

    @NotBlank(message = "章节名称不能为空")
    private String title;

    private String content;

    /** 章节索引（可选，为空时自动取当前最大序号+1） */
    private Integer chapterIndex;
}
