package com.goodzheng.po.recipe.controller;

import com.goodzheng.po.shared.dto.Result;
import com.goodzheng.po.recipe.entity.RecipeCategory;
import com.goodzheng.po.recipe.service.RecipeCategoryService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/recipe-categories")
@CrossOrigin(origins = "*")
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
}
