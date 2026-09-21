package com.goodzheng.po.shared.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class Result<T> {

    private int code;
    private Boolean success;
    private T data;
    private String message;

    public static <T> Result<T> success(T data) {
        return new Result<>(1, true, data, "");
    }

    public static <T> Result<T> success(String message, T data) {
        return new Result<>(1, true, data, message);
    }

    public static <T> Result<T> error(String message) {
        return new Result<>(0, false, null, message);
    }

    public static <T> Result<T> error(int code, String message) {
        return new Result<>(code, false, null, message);
    }
}
