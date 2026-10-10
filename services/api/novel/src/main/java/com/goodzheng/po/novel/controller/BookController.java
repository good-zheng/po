package com.goodzheng.po.novel.controller;

import com.goodzheng.po.novel.constant.NovelGenres;
import com.goodzheng.po.novel.dto.BookRequest;
import com.goodzheng.po.shared.dto.Result;
import com.goodzheng.po.novel.entity.Book;
import com.goodzheng.po.identity.security.AuthUser;
import com.goodzheng.po.novel.service.BookService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Sort;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * 小说接口。
 * 访问控制由 SecurityConfig 统一完成：浏览公开，写操作仅管理端管理员。
 */
@RestController
@RequestMapping("/books")
@RequiredArgsConstructor
public class BookController {

    private final BookService bookService;

    // ── 创建书籍（管理端） ────────────────────────────────
    @PostMapping
    public Result<Book> create(@AuthenticationPrincipal AuthUser principal,
            @Valid @RequestBody BookRequest request) {
        try {
            return Result.success(bookService.create(request, principal.id()));
        } catch (RuntimeException e) {
            return Result.error(400, e.getMessage());
        }
    }

    // ── 书籍类型字典 ──────────────────────────────────────
    @GetMapping("/genres")
    public Result<List<NovelGenres.GenreOption>> genres() {
        return Result.success(NovelGenres.ALL);
    }

    // ── 查询单个书籍详情 ──────────────────────────────────
    @GetMapping("/{id}")
    public Result<Book> getById(@PathVariable Long id) {
        try {
            return Result.success(bookService.getById(id));
        } catch (RuntimeException e) {
            return Result.error(404, e.getMessage());
        }
    }

    // ── 分页列表（支持类型/状态筛选与关键词搜索） ──────────
    @GetMapping
    public Result<Page<Book>> list(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size,
            @RequestParam(required = false) String genre,
            @RequestParam(required = false) String status,
            @RequestParam(required = false) String keyword) {
        PageRequest pageRequest = PageRequest.of(page, size, Sort.by(Sort.Direction.DESC, "updatedAt"));
        return Result.success(bookService.list(keyword, genre, status, pageRequest));
    }

    // ── 更新书籍（管理端） ────────────────────────────────
    @PutMapping("/{id}")
    public Result<Book> update(@PathVariable Long id,
            @Valid @RequestBody BookRequest request) {
        try {
            return Result.success(bookService.update(id, request));
        } catch (RuntimeException e) {
            return Result.error(400, e.getMessage());
        }
    }

    // ── 删除书籍（管理端，级联软删除章节和角色） ──────────
    @DeleteMapping("/{id}")
    public Result<String> delete(@PathVariable Long id) {
        try {
            bookService.delete(id);
            return Result.success("删除成功", null);
        } catch (RuntimeException e) {
            return Result.error(400, e.getMessage());
        }
    }
}
