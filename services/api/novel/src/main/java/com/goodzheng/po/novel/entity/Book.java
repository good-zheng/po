package com.goodzheng.po.novel.entity;

import jakarta.persistence.*;
import lombok.Data;

import java.time.LocalDateTime;

@Data
@Entity
@Table(name = "book")
public class Book {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    /** 创建用户ID */
    @Column(nullable = false)
    private Long authorId;

    @Column(nullable = false, length = 200)
    private String title;

    @Column(columnDefinition = "TEXT")
    private String description;

    @Column(length = 500)
    private String coverImage;

    /** 书籍类型，如：fantasy-玄幻、wuxia-武侠、scifi-科幻 */
    @Column(length = 50)
    private String genre;

    /** 创作状态: ongoing-连载中, completed-已完结, paused-暂停更新 */
    @Column(length = 20)
    private String status = "ongoing";

    /** 书籍总字数（各未删除章节字数合计） */
    @Column(nullable = false)
    private Integer wordCount = 0;

    /** 作者署名 */
    @Column(length = 100)
    private String author;

    // ── 软删除 ────────────────────────────────────────────
    private LocalDateTime deletedAt;

    @Column(updatable = false)
    private LocalDateTime createdAt = LocalDateTime.now();

    private LocalDateTime updatedAt = LocalDateTime.now();

    @PreUpdate
    protected void onUpdate() {
        this.updatedAt = LocalDateTime.now();
    }
}
