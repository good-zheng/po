package com.goodzheng.po.identity.constant;

public final class ApprovalStatusConstants {

    public static final String PENDING = "pending";
    public static final String APPROVED = "approved";
    public static final String REJECTED = "rejected";

    private ApprovalStatusConstants() {
    }

    public static boolean isValid(String status) {
        return PENDING.equals(status) || APPROVED.equals(status) || REJECTED.equals(status);
    }
}
