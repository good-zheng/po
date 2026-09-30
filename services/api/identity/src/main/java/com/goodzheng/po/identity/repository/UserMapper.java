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

    default Optional<User> findByPhoneNumber(String phoneNumber) {
        return Optional.ofNullable(selectOne(new LambdaQueryWrapper<User>().eq(User::getPhoneNumber, phoneNumber)));
    }

    default Optional<User> findByWechatOpenid(String wechatOpenid) {
        return Optional.ofNullable(selectOne(new LambdaQueryWrapper<User>().eq(User::getWechatOpenid, wechatOpenid)));
    }

    default boolean existsByUsername(String username) {
        return selectCount(new LambdaQueryWrapper<User>().eq(User::getUsername, username)) > 0;
    }

    default List<User> findAllById(Collection<Long> ids) {
        return selectBatchIds(ids);
    }

    default List<User> findByApprovalStatus(String approvalStatus) {
        return selectList(new LambdaQueryWrapper<User>()
                .eq(User::getApprovalStatus, approvalStatus)
                .orderByDesc(User::getCreateTime));
    }

    default long countByApprovalStatus(String approvalStatus) {
        return selectCount(new LambdaQueryWrapper<User>().eq(User::getApprovalStatus, approvalStatus));
    }
}
