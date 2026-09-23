package com.goodzheng.po.config;

import com.baomidou.mybatisplus.core.handlers.MetaObjectHandler;
import org.apache.ibatis.reflection.MetaObject;
import org.springframework.stereotype.Component;

import java.time.LocalDateTime;

/**
 * 更新时间自动填充（等价原 JPA @PreUpdate）。
 * 仅对实体上标了 @TableField(fill = FieldFill.UPDATE) 的字段生效。
 * 注意必须用 setFieldValByName 无条件覆盖：从库里查出的实体 updatedAt 非空，
 * strictUpdateFill 遇到非空值会跳过，时间戳就永远不会刷新。
 */
@Component
public class AuditMetaObjectHandler implements MetaObjectHandler {

    @Override
    public void insertFill(MetaObject metaObject) {
        // 创建时间由实体默认值/数据库默认值负责，不在这里填充
    }

    @Override
    public void updateFill(MetaObject metaObject) {
        LocalDateTime now = LocalDateTime.now();
        if (metaObject.hasSetter("updateTime")) {
            this.setFieldValByName("updateTime", now, metaObject);
        }
        if (metaObject.hasSetter("updatedAt")) {
            this.setFieldValByName("updatedAt", now, metaObject);
        }
    }
}
