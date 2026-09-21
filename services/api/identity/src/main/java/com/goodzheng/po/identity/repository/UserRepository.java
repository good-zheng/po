package com.goodzheng.po.identity.repository;

import com.goodzheng.po.identity.entity.User;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface UserRepository extends JpaRepository<User, Long> {

    Optional<User> findByUsername(String username);

    boolean existsByUsername(String username);

    @Query("SELECT u FROM User u WHERE " +
           "LOWER(u.username) LIKE LOWER(CONCAT('%', :keyword, '%')) OR " +
           "LOWER(u.email) LIKE LOWER(CONCAT('%', :keyword, '%')) OR " +
           "LOWER(u.firstName) LIKE LOWER(CONCAT('%', :keyword, '%')) OR " +
           "LOWER(u.lastName) LIKE LOWER(CONCAT('%', :keyword, '%'))")
    Page<User> searchByKeyword(@Param("keyword") String keyword, Pageable pageable);
}
