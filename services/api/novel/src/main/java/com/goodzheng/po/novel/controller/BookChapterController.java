package com.goodzheng.po.novel.controller;

import com.goodzheng.po.novel.dto.ChapterRequest;
import com.goodzheng.po.shared.dto.Result;
import com.goodzheng.po.novel.entity.BookChapter;
import com.goodzheng.po.identity.repository.UserRepository;
import com.goodzheng.po.novel.service.BookChapterService;
import com.goodzheng.po.identity.security.JwtUtil;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/books/{bookId}/chapters")
@CrossOrigin(origins = "*")
@RequiredArgsConstructor
public class BookChapterController {

    private final BookChapterService chapterService;
    private final JwtUtil jwtUtil;
    private final UserRepository userRepository;

    // ── 章节列表 ──────────────────────────────────────────
    @GetMapping
    public Result<List<BookChapter>> list(@PathVariable Long bookId) {
        try {
            return Result.success(chapterService.list(bookId));
        } catch (RuntimeException e) {
            return Result.error(404, e.getMessage());
        }
    }

    // ── 创建章节 ──────────────────────────────────────────
    @PostMapping
    public Result<BookChapter> create(@PathVariable Long bookId,
            @RequestHeader("Authorization") String auth,
            @Valid @RequestBody ChapterRequest request) {
        try {
            Long operatorId = resolveUserId(auth);
            return Result.success(chapterService.create(bookId, request, operatorId));
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

    // ── 更新章节 ──────────────────────────────────────────
    @PutMapping("/{chapterId}")
    public Result<BookChapter> update(@PathVariable Long bookId, @PathVariable Long chapterId,
            @RequestHeader("Authorization") String auth,
            @Valid @RequestBody ChapterRequest request) {
        try {
            Long operatorId = resolveUserId(auth);
            return Result.success(chapterService.update(bookId, chapterId, request, operatorId));
        } catch (RuntimeException e) {
            return Result.error(400, e.getMessage());
        }
    }

    // ── 删除章节 ──────────────────────────────────────────
    @DeleteMapping("/{chapterId}")
    public Result<String> delete(@PathVariable Long bookId, @PathVariable Long chapterId,
            @RequestHeader("Authorization") String auth) {
        try {
            Long operatorId = resolveUserId(auth);
            chapterService.delete(bookId, chapterId, operatorId);
            return Result.success("删除成功", null);
        } catch (RuntimeException e) {
            return Result.error(400, e.getMessage());
        }
    }

    private Long resolveUserId(String authHeader) {
        String token = authHeader.replace("Bearer ", "");
        String username = jwtUtil.getUsernameFromToken(token);
        return userRepository.findByUsername(username)
                .orElseThrow(() -> new RuntimeException("用户不存在"))
                .getId();
    }
}
