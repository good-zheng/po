package com.goodzheng.po.identity.repository;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.goodzheng.po.identity.entity.User;
import org.apache.ibatis.annotations.Mapper;

import java.util.Collection;
import java.util.List;
import java.util.Optional;

@Mapper
public interface UserMapper extends BaseMapper<User> {

    default Optional<User> findByUsername(String username) {
        return Optional.ofNullable(selectOne(new LambdaQueryWrapper<User>().eq(User::getUsername, username)));
    }

    default boolean existsByUsername(String username) {
        return selectCount(new LambdaQueryWrapper<User>().eq(User::getUsername, username)) > 0;
    }

    default List<User> findAllById(Collection<Long> ids) {
        return selectBatchIds(ids);
    }
}
