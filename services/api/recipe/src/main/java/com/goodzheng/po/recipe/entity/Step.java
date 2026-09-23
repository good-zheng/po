package com.goodzheng.po.recipe.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import com.fasterxml.jackson.annotation.JsonIgnore;
import lombok.Data;

@Data
@TableName("recipe_step")
public class Step {

    @TableId(type = IdType.AUTO)
    private Long id;

    /** 所属菜谱 ID（原 JPA @ManyToOne 关联，MyBatis-Plus 用普通外键字段） */
    @JsonIgnore
    private Long recipeId;

    private Integer stepNumber;

    private String content;

    private String imageUrl;

    private String videoUrl;

    /** 该步骤耗时（分钟） */
    private Integer duration;
}
