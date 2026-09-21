package com.goodzheng.po.recipe.controller;

import com.goodzheng.po.recipe.dto.RecipeRequest;
import com.goodzheng.po.shared.dto.Result;
import com.goodzheng.po.recipe.entity.Recipe;
import com.goodzheng.po.recipe.service.RecipeService;
import com.goodzheng.po.identity.security.JwtUtil;
import com.goodzheng.po.identity.repository.UserRepository;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Sort;
import org.springframework.web.bind.annotation.*;

import java.util.ArrayList;
import java.util.List;
import java.util.Objects;
import java.util.stream.Collectors;
import java.util.Arrays;

@RestController
@RequestMapping("/recipes")
@CrossOrigin(origins = "*")
@RequiredArgsConstructor
public class RecipeController {

    private final RecipeService recipeService;
    private final JwtUtil jwtUtil;
    private final UserRepository userRepository;

    // ── 创建菜谱 ──────────────────────────────────────────
    @PostMapping
    public Result<Recipe> create(@RequestHeader("Authorization") String auth,
            @Valid @RequestBody RecipeRequest request) {
        try {
            Long authorId = resolveUserId(auth);
            Recipe recipe = recipeService.create(request, authorId);
            return Result.success(recipe);
        } catch (RuntimeException e) {
            return Result.error(400, e.getMessage());
        }
    }

    // ── 查询单个菜谱详情 ──────────────────────────────────
    @GetMapping("/{id}")
    public Result<Recipe> getById(@PathVariable Long id) {
        try {
            return Result.success(recipeService.getById(id));
        } catch (RuntimeException e) {
            return Result.error(404, e.getMessage());
        }
    }

    // ── 分页列表 ──────────────────────────────────────────
    @GetMapping
    public Result<Page<Recipe>> list(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size,
            @RequestParam(required = false) String categoryIdStr,
            @RequestParam(required = false) String keyword) {

        PageRequest pageRequest = PageRequest.of(page, size, Sort.by(Sort.Direction.DESC, "createdAt"));

        Page<Recipe> result;
        if (keyword != null && !keyword.isBlank()) {
            result = recipeService.search(keyword, pageRequest);
        } else if (!Objects.isNull(categoryIdStr) && !categoryIdStr.isBlank()) {

            List<Long> categoryId = Arrays.stream(categoryIdStr.split(","))
                    .map(String::trim) // 去除每个元素前后的空格
                    .filter(s -> !s.isEmpty()) // 过滤掉空字符串
                    .map(Long::parseLong) // 将字符串转换为 Long
                    .collect(Collectors.toList());
            
            result = recipeService.listByCategories(categoryId, pageRequest);
        } else {
            result = recipeService.list(pageRequest);
        }
        return Result.success(result);
    }

    // ── 我的菜谱 ──────────────────────────────────────────
    @GetMapping("/mine")
    public Result<Page<Recipe>> myRecipes(
            @RequestHeader("Authorization") String auth,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size) {
        try {
            Long authorId = resolveUserId(auth);
            PageRequest pageRequest = PageRequest.of(page, size, Sort.by(Sort.Direction.DESC, "createdAt"));
            return Result.success(recipeService.listByAuthor(authorId, pageRequest));
        } catch (RuntimeException e) {
            return Result.error(401, e.getMessage());
        }
    }

    // ── 更新菜谱 ──────────────────────────────────────────
    @PutMapping("/{id}")
    public Result<Recipe> update(@PathVariable Long id,
            @RequestHeader("Authorization") String auth,
            @Valid @RequestBody RecipeRequest request) {
        try {
            Long authorId = resolveUserId(auth);
            return Result.success(recipeService.update(id, request, authorId));
        } catch (RuntimeException e) {
            return Result.error(400, e.getMessage());
        }
    }

    // ── 删除菜谱（软删除） ───────────────────────────────
    @DeleteMapping("/{id}")
    public Result<String> delete(@PathVariable Long id,
            @RequestHeader("Authorization") String auth) {
        try {
            Long authorId = resolveUserId(auth);
            recipeService.delete(id, authorId);
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
