package com.goodzheng.po.novel.service;

import com.goodzheng.po.novel.dto.StyleProfileRequest;
import com.goodzheng.po.novel.dto.StyleProfileView;

/**
 * 文风契约（§5.5）的读写面。
 *
 * <p>读侧有两个身份完全不同的调用方，但<b>只有一份实现</b>：管理端给作者看、内网通道给
 * L1 编译器与闸门用。分叉会变成「作者以为的字数带」和「闸门实际用的字数带」两个数，
 * 而这类漂移在台账里没有任何痕迹。
 */
public interface StyleProfileService {

    /**
     * @return 本书的契约；一本没定过契约的书返回 {@code null}，那是「还没有契约」而不是错误——
     *         装配侧据此退回本轮构思派生的默认契约，Tier-0 永不为空
     */
    StyleProfileView get(Long bookId);

    /** upsert：一本书一份契约；入参里为 null 的字段保留库中原值 */
    StyleProfileView update(Long bookId, StyleProfileRequest req);
}
