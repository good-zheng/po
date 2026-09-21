package com.goodzheng.po.novel.controller;

import com.goodzheng.po.novel.dto.CharacterRequest;
import com.goodzheng.po.shared.dto.Result;
import com.goodzheng.po.novel.entity.BookCharacter;
import com.goodzheng.po.identity.repository.UserRepository;
import com.goodzheng.po.novel.service.BookCharacterService;
import com.goodzheng.po.identity.security.JwtUtil;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/books/{bookId}/characters")
@CrossOrigin(origins = "*")
@RequiredArgsConstructor
public class BookCharacterController {

    private final BookCharacterService characterService;
    private final JwtUtil jwtUtil;
    private final UserRepository userRepository;

    // ── 角色列表 ──────────────────────────────────────────
    @GetMapping
    public Result<List<BookCharacter>> list(@PathVariable Long bookId) {
        try {
            return Result.success(characterService.list(bookId));
        } catch (RuntimeException e) {
            return Result.error(404, e.getMessage());
        }
    }

    // ── 创建角色 ──────────────────────────────────────────
    @PostMapping
    public Result<BookCharacter> create(@PathVariable Long bookId,
            @RequestHeader("Authorization") String auth,
            @Valid @RequestBody CharacterRequest request) {
        try {
            Long operatorId = resolveUserId(auth);
            return Result.success(characterService.create(bookId, request, operatorId));
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

    // ── 更新角色 ──────────────────────────────────────────
    @PutMapping("/{characterId}")
    public Result<BookCharacter> update(@PathVariable Long bookId, @PathVariable Long characterId,
            @RequestHeader("Authorization") String auth,
            @Valid @RequestBody CharacterRequest request) {
        try {
            Long operatorId = resolveUserId(auth);
            return Result.success(characterService.update(bookId, characterId, request, operatorId));
        } catch (RuntimeException e) {
            return Result.error(400, e.getMessage());
        }
    }

    // ── 删除角色 ──────────────────────────────────────────
    @DeleteMapping("/{characterId}")
    public Result<String> delete(@PathVariable Long bookId, @PathVariable Long characterId,
            @RequestHeader("Authorization") String auth) {
        try {
            Long operatorId = resolveUserId(auth);
            characterService.delete(bookId, characterId, operatorId);
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
