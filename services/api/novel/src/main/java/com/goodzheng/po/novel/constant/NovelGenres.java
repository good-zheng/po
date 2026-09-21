package com.goodzheng.po.novel.constant;

import java.util.List;

/**
 * 小说类型字典（与小说类型列表接口保持一致）
 */
public final class NovelGenres {

    private NovelGenres() {
    }

    public record GenreOption(String value, String label) {
    }

    public static final List<GenreOption> ALL = List.of(
            new GenreOption("fantasy", "玄幻"),
            new GenreOption("wuxia", "武侠"),
            new GenreOption("scifi", "科幻"),
            new GenreOption("romance", "言情"),
            new GenreOption("mystery", "悬疑"),
            new GenreOption("history", "历史"),
            new GenreOption("urban", "都市"),
            new GenreOption("game", "游戏"),
            new GenreOption("horror", "恐怖"),
            new GenreOption("other", "其他")
    );
}
