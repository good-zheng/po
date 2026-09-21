package com.goodzheng.po.novel.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.Data;

@Data
public class CharacterRequest {

    @NotBlank(message = "角色名称不能为空")
    private String name;

    private String description;
    private String avatar;
}
