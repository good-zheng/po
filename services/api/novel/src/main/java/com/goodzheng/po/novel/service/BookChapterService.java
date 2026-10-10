package com.goodzheng.po.novel.service;

import com.goodzheng.po.novel.dto.ChapterRequest;
import com.goodzheng.po.novel.entity.BookChapter;

import java.util.List;

public interface BookChapterService {

    List<BookChapter> list(Long bookId);

    /**
     * 未删除章节数（内网对话装配用：判断参照章号有没有越界）。
     *
     * <p>单独一条 count 而不是 {@code list(bookId).size()}：一书的正文加起来是百 KB 量级，
     * 而装配只要一个数字。
     */
    int countByBook(Long bookId);

    BookChapter get(Long bookId, Long chapterId);

    BookChapter create(Long bookId, ChapterRequest request);

    /**
     * 唯一的正文写路径：改完必须连带重算（§10.5-③），所以重定位、快照、状态退回都在这一个方法里，
     * 任何入口都没有「只存正文」的选项。
     *
     * @param userId 作者 ID，写进 {@code chapter_revision.created_by}
     */
    BookChapter update(Long bookId, Long chapterId, ChapterRequest request, Long userId);

    void delete(Long bookId, Long chapterId);
}
