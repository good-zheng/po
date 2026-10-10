package com.goodzheng.po.novel.controller;

import com.goodzheng.po.novel.dto.CharacterRequest;
import com.goodzheng.po.shared.dto.Result;
import com.goodzheng.po.novel.entity.BookCharacter;
import com.goodzheng.po.novel.service.BookCharacterService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * 书籍角色接口。
 * 写操作仅管理端管理员，由 SecurityConfig 统一约束。
 */
@RestController
@RequestMapping("/books/{bookId}/characters")
@RequiredArgsConstructor
public class BookCharacterController {

    private final BookCharacterService characterService;

    // ── 角色列表 ──────────────────────────────────────────
    @GetMapping
    public Result<List<BookCharacter>> list(@PathVariable Long bookId) {
        try {
            return Result.success(characterService.list(bookId));
        } catch (RuntimeException e) {
            return Result.error(404, e.getMessage());
        }
    }

    // ── 创建角色（管理端） ────────────────────────────────
    @PostMapping
    public Result<BookCharacter> create(@PathVariable Long bookId,
            @Valid @RequestBody CharacterRequest request) {
        try {
            return Result.success(characterService.create(bookId, request));
        } catch (RuntimeException e) {
            return Result.error(400, e.getMessage());
        }
    }

    // ── 角色详情 ──────────────────────────────────────────
    @GetMapping("/{characterId}")
    public Result<BookCharacter> get(@PathVariable Long bookId, @PathVariable Long characterId) {
        try {
            return Result.success(characterService.get(bookId, characterId));
        } catch (RuntimeException e) {
            return Result.error(404, e.getMessage());
        }
    }

    // ── 更新角色（管理端） ────────────────────────────────
    @PutMapping("/{characterId}")
    public Result<BookCharacter> update(@PathVariable Long bookId, @PathVariable Long characterId,
            @Valid @RequestBody CharacterRequest request) {
        try {
            return Result.success(characterService.update(bookId, characterId, request));
        } catch (RuntimeException e) {
            return Result.error(400, e.getMessage());
        }
    }

    // ── 删除角色（管理端） ────────────────────────────────
    @DeleteMapping("/{characterId}")
    public Result<String> delete(@PathVariable Long bookId, @PathVariable Long characterId) {
        try {
            characterService.delete(bookId, characterId);
            return Result.success("删除成功", null);
        } catch (RuntimeException e) {
            return Result.error(400, e.getMessage());
        }
    }
}
