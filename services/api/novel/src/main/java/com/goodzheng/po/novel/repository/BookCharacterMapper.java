package com.goodzheng.po.novel.repository;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.goodzheng.po.novel.entity.BookCharacter;
import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface BookCharacterMapper extends BaseMapper<BookCharacter> {
}
