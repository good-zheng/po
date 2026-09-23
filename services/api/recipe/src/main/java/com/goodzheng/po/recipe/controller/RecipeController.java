package com.goodzheng.po.recipe.controller;

import com.goodzheng.po.identity.security.AuthUser;
import com.goodzheng.po.recipe.constant.RecipeStatusConstants;
import com.goodzheng.po.recipe.dto.AuditRequest;
import com.goodzheng.po.recipe.dto.LikeResult;
import com.goodzheng.po.recipe.dto.RecipeRequest;
import com.goodzheng.po.recipe.entity.Recipe;
import com.goodzheng.po.recipe.service.RecipeInteractionService;
import com.goodzheng.po.recipe.service.RecipeService;
import com.goodzheng.po.shared.dto.Result;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Sort;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.util.Arrays;
import java.util.List;
import java.util.Objects;
import java.util.stream.Collectors;

/**
 * 菜谱接口。
 * 浏览公开；收藏/点赞/历史/创建需登录；管理端审核队列与审核操作仅管理端管理员。
 * App 用户创建的菜谱进入待审核（pending），管理员在管理端审核通过后公开可见。
 */
@RestController
@RequestMapping("/recipes")
@RequiredArgsConstructor
public class RecipeController {

    private final RecipeService recipeService;
    private final RecipeInteractionService interactionService;

    // ── 创建菜谱（管理员直接通过；App 用户进入待审核） ──────
    @PostMapping
    public Result<Recipe> create(@AuthenticationPrincipal AuthUser principal,
            @Valid @RequestBody RecipeRequest request) {
        try {
            String initialStatus = principal.isManager()
                    ? RecipeStatusConstants.APPROVED
                    : RecipeStatusConstants.PENDING;
            Recipe recipe = recipeService.create(request, principal.id(), initialStatus);
            return Result.success(recipe);
        } catch (RuntimeException e) {
            return Result.error(400, e.getMessage());
        }
    }

    // ── 查询单个菜谱详情（未发布仅作者本人/管理员可见；登录浏览计入历史） ──
    @GetMapping("/{id}")
    public Result<Recipe> getById(@AuthenticationPrincipal AuthUser principal,
            @PathVariable Long id) {
        try {
            Recipe recipe = recipeService.getById(id);
            if (!recipeService.isVisible(recipe) && !canManage(principal, recipe)) {
                return Result.error(404, "菜谱不存在或未通过审核");
            }
            if (principal != null) {
                interactionService.fillFlags(principal.id(), List.of(recipe));
                interactionService.recordHistory(principal.id(), recipe.getId());
            }
            return Result.success(recipe);
        } catch (RuntimeException e) {
            return Result.error(404, e.getMessage());
        }
    }

    // ── 筛选排序列表（公开：仅已通过审核且公开的菜谱） ──────
    @GetMapping
    public Result<Page<Recipe>> list(
            @AuthenticationPrincipal AuthUser principal,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size,
            @RequestParam(required = false) String categoryIdStr,
            @RequestParam(required = false) Integer difficulty,
            @RequestParam(required = false) String keyword,
            @RequestParam(defaultValue = "recommend") String sort) {

        PageRequest pageRequest = PageRequest.of(page, size);
        List<Long> categoryIds = parseCategoryIds(categoryIdStr);
        Page<Recipe> result = recipeService.filteredList(keyword, categoryIds, difficulty, sort, pageRequest);
        if (principal != null) {
            interactionService.fillFlags(principal.id(), result.getContent());
        }
        return Result.success(result);
    }

    // ── 我的菜谱（全部状态，含待审核/已驳回） ──────────────
    @GetMapping("/mine")
    public Result<Page<Recipe>> myRecipes(
            @AuthenticationPrincipal AuthUser principal,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size) {
        PageRequest pageRequest = PageRequest.of(page, size, Sort.by(Sort.Direction.DESC, "createdAt"));
        return Result.success(recipeService.listByAuthor(principal.id(), pageRequest));
    }

    // ── 我的收藏 ──────────────────────────────────────────
    @GetMapping("/favorites")
    public Result<Page<Recipe>> myFavorites(
            @AuthenticationPrincipal AuthUser principal,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size) {
        PageRequest pageRequest = PageRequest.of(page, size);
        Page<Recipe> result = interactionService.listFavorites(principal.id(), pageRequest);
        interactionService.fillFlags(principal.id(), result.getContent());
        return Result.success(result);
    }

    // ── 我的浏览历史 ──────────────────────────────────────
    @GetMapping("/history")
    public Result<Page<Recipe>> myHistory(
            @AuthenticationPrincipal AuthUser principal,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size) {
        PageRequest pageRequest = PageRequest.of(page, size);
        Page<Recipe> result = interactionService.listHistory(principal.id(), pageRequest);
        interactionService.fillFlags(principal.id(), result.getContent());
        return Result.success(result);
    }

    // ── 管理端审核队列（仅管理端管理员） ──────────────────
    @GetMapping("/review")
    public Result<Page<Recipe>> reviewList(
            @RequestParam(required = false) String status,
            @RequestParam(required = false) String keyword,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size) {
        try {
            PageRequest pageRequest = PageRequest.of(page, size);
            return Result.success(recipeService.reviewList(status, keyword, pageRequest));
        } catch (RuntimeException e) {
            return Result.error(400, e.getMessage());
        }
    }

    // ── 管理端审核（仅管理端管理员） ──────────────────────
    @PutMapping("/{id}/audit")
    public Result<Recipe> audit(@PathVariable Long id,
            @Valid @RequestBody AuditRequest request) {
        try {
            recipeService.audit(id, request.getAction(), request.getReason());
            return Result.success(recipeService.getById(id));
        } catch (RuntimeException e) {
            return Result.error(400, e.getMessage());
        }
    }

    // ── 收藏 / 取消收藏（登录用户） ───────────────────────
    @PostMapping("/{id}/favorite")
    public Result<String> favorite(@AuthenticationPrincipal AuthUser principal,
            @PathVariable Long id) {
        try {
            interactionService.favorite(principal.id(), id);
            return Result.success("收藏成功", null);
        } catch (RuntimeException e) {
            return Result.error(400, e.getMessage());
        }
    }

    @DeleteMapping("/{id}/favorite")
    public Result<String> unfavorite(@AuthenticationPrincipal AuthUser principal,
            @PathVariable Long id) {
        try {
            interactionService.unfavorite(principal.id(), id);
            return Result.success("已取消收藏", null);
        } catch (RuntimeException e) {
            return Result.error(400, e.getMessage());
        }
    }

    // ── 点赞切换（登录用户） ──────────────────────────────
    @PostMapping("/{id}/like")
    public Result<LikeResult> like(@AuthenticationPrincipal AuthUser principal,
            @PathVariable Long id) {
        try {
            return Result.success(interactionService.toggleLike(principal.id(), id));
        } catch (RuntimeException e) {
            return Result.error(400, e.getMessage());
        }
    }

    // ── 更新菜谱（管理员任意；作者本人，修改后重新送审） ────
    @PutMapping("/{id}")
    public Result<Recipe> update(@AuthenticationPrincipal AuthUser principal,
            @PathVariable Long id,
            @Valid @RequestBody RecipeRequest request) {
        try {
            return Result.success(recipeService.update(id, request, principal.id(), principal.isManager()));
        } catch (RuntimeException e) {
            return Result.error(400, e.getMessage());
        }
    }

    // ── 删除菜谱（软删除；管理员任意，作者只能删自己的） ────
    @DeleteMapping("/{id}")
    public Result<String> delete(@AuthenticationPrincipal AuthUser principal,
            @PathVariable Long id) {
        try {
            recipeService.delete(id, principal.id(), principal.isManager());
            return Result.success("删除成功", null);
        } catch (RuntimeException e) {
            return Result.error(400, e.getMessage());
        }
    }

    // ── 参数解析 ──────────────────────────────────────────

    /** 未发布菜谱仅作者本人或管理员可见 */
    private boolean canManage(AuthUser principal, Recipe recipe) {
        return principal != null
                && (principal.isManager() || principal.id().equals(recipe.getAuthorId()));
    }

    private List<Long> parseCategoryIds(String categoryIdStr) {
        if (Objects.isNull(categoryIdStr) || categoryIdStr.isBlank()) {
            return List.of();
        }
        return Arrays.stream(categoryIdStr.split(","))
                .map(String::trim)
                .filter(s -> !s.isEmpty())
                .map(Long::parseLong)
                .collect(Collectors.toList());
    }
}
