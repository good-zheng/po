package com.goodzheng.po.novel.controller;

import com.goodzheng.po.novel.constant.NovelGenres;
import com.goodzheng.po.novel.dto.BookRequest;
import com.goodzheng.po.shared.dto.Result;
import com.goodzheng.po.novel.entity.Book;
import com.goodzheng.po.identity.repository.UserRepository;
import com.goodzheng.po.novel.service.BookService;
import com.goodzheng.po.identity.security.JwtUtil;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Sort;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/books")
@CrossOrigin(origins = "*")
@RequiredArgsConstructor
public class BookController {

    private final BookService bookService;
    private final JwtUtil jwtUtil;
    private final UserRepository userRepository;

    // ── 创建书籍 ──────────────────────────────────────────
    @PostMapping
    public Result<Book> create(@RequestHeader("Authorization") String auth,
            @Valid @RequestBody BookRequest request) {
        try {
            Long authorId = resolveUserId(auth);
            return Result.success(bookService.create(request, authorId));
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

    // ── 更新书籍 ──────────────────────────────────────────
    @PutMapping("/{id}")
    public Result<Book> update(@PathVariable Long id,
            @RequestHeader("Authorization") String auth,
            @Valid @RequestBody BookRequest request) {
        try {
            Long authorId = resolveUserId(auth);
            return Result.success(bookService.update(id, request, authorId));
        } catch (RuntimeException e) {
            return Result.error(400, e.getMessage());
        }
    }

    // ── 删除书籍（级联软删除章节和角色） ──────────────────
    @DeleteMapping("/{id}")
    public Result<String> delete(@PathVariable Long id,
            @RequestHeader("Authorization") String auth) {
        try {
            Long authorId = resolveUserId(auth);
            bookService.delete(id, authorId);
            return Result.success("删除成功", null);
        } catch (RuntimeException e) {
            return Result.error(400, e.getMessage());
        }
    }

    // ── 工具：从 JWT 解析用户 ID ─────────────────────────
    private Long resolveUserId(String authHeader) {
        String token = authHeader.replace("Bearer ", "");
        String username = jwtUtil.getUsernameFromToken(token);
        return userRepository.findByUsername(username)
                .orElseThrow(() -> new RuntimeException("用户不存在"))
                .getId();
    }
}
