package com.goodzheng.po.identity.service;

import com.goodzheng.po.identity.dto.UserRequest;
import com.goodzheng.po.identity.entity.User;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;

import java.util.List;

public interface UserService {

    Page<User> list(Pageable pageable);

    Page<User> search(String keyword, Pageable pageable);

    User getById(Long id);

    User create(UserRequest request);

    User update(Long id, UserRequest request);

    /** 验证原密码后修改当前用户密码 */
    void changePassword(Long id, String oldPassword, String newPassword);

    void delete(Long id);

    void batchDelete(List<Long> ids);

    void batchUpdateStatus(List<Long> ids, String status);
}
