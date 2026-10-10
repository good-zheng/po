package com.goodzheng.po.novel.dto;

import lombok.Data;

/** 别名改判入参（PUT /novel/books/{bookId}/aliases/{aliasId}）。 */
@Data
public class AliasRequest {

    /** 把称谓指向哪个实体键；一个称谓在一本书内只能指向一个实体，改判即裁定 C3 */
    private String entityKey;

    private Boolean isPrimary;
}
