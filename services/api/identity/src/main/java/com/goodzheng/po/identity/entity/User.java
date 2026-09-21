package com.goodzheng.po.identity.entity;

import com.fasterxml.jackson.annotation.JsonIgnore;
import jakarta.persistence.*;
import lombok.Data;
import java.time.LocalDateTime;

@Data
@Entity
@Table(name = "sys_user", uniqueConstraints = @UniqueConstraint(columnNames = "username"))
public class User {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true, length = 50)
    private String username;

    @JsonIgnore
    @Column(nullable = false)
    private String password;

    @Column(length = 100)
    private String email;

    @Column(length = 50)
    private String nickname;

    @Column(length = 255)
    private String avatar;

    @Column(length = 50)
    private String firstName;

    @Column(length = 50)
    private String lastName;

    @Column(length = 20)
    private String phoneNumber;

    /** 角色: superadmin, admin, user */
    @Column(length = 20)
    private String role = "user";

    /** 状态: active, inactive, invited, suspended */
    @Column(nullable = false, length = 20)
    private String status = "active";

    @Column(updatable = false)
    private LocalDateTime createTime = LocalDateTime.now();

    private LocalDateTime updateTime = LocalDateTime.now();

    @PreUpdate
    protected void onUpdate() {
        this.updateTime = LocalDateTime.now();
    }
}
