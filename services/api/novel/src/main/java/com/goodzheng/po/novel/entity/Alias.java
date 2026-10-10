package com.goodzheng.po.novel.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

/**
 * 称谓别名表（C3「一人多名 / 多名同人」的依据）。
 *
 * <p>库约束 (bookId, aliasText) 唯一：一个称谓在一本书内只能指向一个实体，
 * 所以抽取重放或冲突登记必须走「先查后改」，不能盲目 insert。
 */
@Data
@TableName("alias")
public class Alias {

    @TableId(type = IdType.AUTO)
    private Long id;

    private Long bookId;

    private String entityKey;

    private String aliasText;

    private Integer firstSeenChapter;

    private Boolean isPrimary;
}
