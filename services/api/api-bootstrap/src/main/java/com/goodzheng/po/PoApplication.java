package com.goodzheng.po;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.security.autoconfigure.UserDetailsServiceAutoConfiguration;

@SpringBootApplication(exclude = UserDetailsServiceAutoConfiguration.class)
public class PoApplication {

    public static void main(String[] args) {
        SpringApplication.run(PoApplication.class, args);
    }

}
