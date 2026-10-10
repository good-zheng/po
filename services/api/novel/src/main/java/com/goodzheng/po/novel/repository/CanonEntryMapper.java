package com.goodzheng.po.novel.repository;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.goodzheng.po.novel.entity.CanonEntry;
import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface CanonEntryMapper extends BaseMapper<CanonEntry> {
}
