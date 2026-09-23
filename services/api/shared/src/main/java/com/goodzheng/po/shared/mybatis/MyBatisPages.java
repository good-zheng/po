package com.goodzheng.po.shared.mybatis;

import com.baomidou.mybatisplus.core.metadata.OrderItem;
import org.springframework.data.domain.PageImpl;
import org.springframework.data.domain.Pageable;

import java.util.ArrayList;
import java.util.List;
import java.util.regex.Pattern;

/**
 * Spring Data Commons 分页模型（Page/Pageable）与 MyBatis-Plus 分页的互转工具。
 * Controller / Service 接口继续面向 Page/Pageable，仅 Service 实现内部做转换。
 */
public final class MyBatisPages {

    private static final Pattern UPPERCASE = Pattern.compile("([A-Z])");

    private MyBatisPages() {
    }

    /** 把 Spring Pageable（含排序）转换为 MyBatis-Plus Page */
    public static <T> com.baomidou.mybatisplus.extension.plugins.pagination.Page<T> toMpPage(Pageable pageable) {
        com.baomidou.mybatisplus.extension.plugins.pagination.Page<T> page =
                new com.baomidou.mybatisplus.extension.plugins.pagination.Page<>(
                        pageable.getPageNumber() + 1, pageable.getPageSize());
        List<OrderItem> orders = new ArrayList<>();
        pageable.getSort().forEach(order -> orders.add(order.isAscending()
                ? OrderItem.asc(toSnakeCase(order.getProperty()))
                : OrderItem.desc(toSnakeCase(order.getProperty()))));
        page.addOrder(orders);
        return page;
    }

    /** 把 MyBatis-Plus 分页结果转换回 Spring Page（保持 Service 返回类型不变） */
    public static <T> org.springframework.data.domain.Page<T> toPage(
            com.baomidou.mybatisplus.extension.plugins.pagination.Page<T> mpPage, Pageable pageable) {
        return new PageImpl<>(mpPage.getRecords(), pageable, mpPage.getTotal());
    }

    /** camelCase 属性名 → snake_case 列名（与 map-underscore-to-camel-case 对应） */
    private static String toSnakeCase(String property) {
        return UPPERCASE.matcher(property).replaceAll("_$1").toLowerCase();
    }
}
