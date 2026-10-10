package com.goodzheng.po.novel.controller;

import com.goodzheng.po.identity.security.AuthUser;
import com.goodzheng.po.novel.dto.ChapterRequest;
import com.goodzheng.po.shared.dto.Result;
import com.goodzheng.po.novel.entity.BookChapter;
import com.goodzheng.po.novel.service.BookChapterService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * 章节接口。
 * 写操作仅管理端管理员，由 SecurityConfig 统一约束。
 */
@RestController
@RequestMapping("/books/{bookId}/chapters")
@RequiredArgsConstructor
public class BookChapterController {

    private final BookChapterService chapterService;

    // ── 章节列表 ──────────────────────────────────────────
    @GetMapping
    public Result<List<BookChapter>> list(@PathVariable Long bookId) {
        try {
            return Result.success(chapterService.list(bookId));
        } catch (RuntimeException e) {
            return Result.error(404, e.getMessage());
        }
    }

    // ── 创建章节（管理端） ────────────────────────────────
    @PostMapping
    public Result<BookChapter> create(@PathVariable Long bookId,
            @Valid @RequestBody ChapterRequest request) {
        try {
            return Result.success(chapterService.create(bookId, request));
        } catch (RuntimeException e) {
            return Result.error(400, e.getMessage());
        }
    }

    // ── 章节详情 ──────────────────────────────────────────
    @GetMapping("/{chapterId}")
    public Result<BookChapter> get(@PathVariable Long bookId, @PathVariable Long chapterId) {
        try {
            return Result.success(chapterService.get(bookId, chapterId));
        } catch (RuntimeException e) {
            return Result.error(404, e.getMessage());
        }
    }

    // ── 更新章节（管理端） ────────────────────────────────
    @PutMapping("/{chapterId}")
    public Result<BookChapter> update(@AuthenticationPrincipal AuthUser principal,
            @PathVariable Long bookId, @PathVariable Long chapterId,
            @Valid @RequestBody ChapterRequest request) {
        try {
            // userId 进 chapter_revision.created_by：「谁动了正文」在长篇里必须可追
            return Result.success(chapterService.update(bookId, chapterId, request,
                    principal == null ? null : principal.id()));
        } catch (RuntimeException e) {
            return Result.error(400, e.getMessage());
        }
    }

    // ── 删除章节（管理端） ────────────────────────────────
    @DeleteMapping("/{chapterId}")
    public Result<String> delete(@PathVariable Long bookId, @PathVariable Long chapterId) {
        try {
            chapterService.delete(bookId, chapterId);
            return Result.success("删除成功", null);
        } catch (RuntimeException e) {
            return Result.error(400, e.getMessage());
        }
    }
}
