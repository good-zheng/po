package com.goodzheng.po.recipe.controller;

import com.goodzheng.po.recipe.dto.RecipeCategoryRequest;
import com.goodzheng.po.shared.dto.Result;
import com.goodzheng.po.recipe.entity.RecipeCategory;
import com.goodzheng.po.recipe.service.RecipeCategoryService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

/**
 * 菜谱分类接口。
 * 查询公开（App 未登录也要看分类）；写操作由 SecurityConfig 限定为管理端管理员。
 */
@RestController
@RequestMapping("/recipe-categories")
@RequiredArgsConstructor
public class RecipeCategoryController {

    private final RecipeCategoryService recipeCategoryService;

    // ── 查询所有菜谱分类（公开接口，无需登录） ───────────
    @GetMapping
    public Result<List<RecipeCategory>> listAll() {
        try {
            return Result.success(recipeCategoryService.listAll());
        } catch (RuntimeException e) {
            return Result.error(500, e.getMessage());
        }
    }

    // ── 新建分类（管理员） ──────────────────────────────
    @PostMapping
    public Result<RecipeCategory> create(@Valid @RequestBody RecipeCategoryRequest request) {
        try {
            return Result.success(recipeCategoryService.create(request));
        } catch (RuntimeException e) {
            return Result.error(400, e.getMessage());
        }
    }

    // ── 更新分类（管理员） ──────────────────────────────
    @PutMapping("/{id}")
    public Result<RecipeCategory> update(
            @PathVariable Long id,
            @Valid @RequestBody RecipeCategoryRequest request) {
        try {
            return Result.success(recipeCategoryService.update(id, request));
        } catch (RuntimeException e) {
            return Result.error(400, e.getMessage());
        }
    }

    // ── 删除分类（管理员，软删除） ──────────────────────
    @DeleteMapping("/{id}")
    public Result<String> delete(@PathVariable Long id) {
        try {
            recipeCategoryService.delete(id);
            return Result.success("删除成功", null);
        } catch (RuntimeException e) {
            return Result.error(400, e.getMessage());
        }
    }
}
