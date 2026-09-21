package com.goodzheng.po.novel.service;

import com.goodzheng.po.novel.dto.ChapterRequest;
import com.goodzheng.po.novel.entity.BookChapter;

import java.util.List;

public interface BookChapterService {

    List<BookChapter> list(Long bookId);

    BookChapter get(Long bookId, Long chapterId);

    BookChapter create(Long bookId, ChapterRequest request, Long operatorId);

    BookChapter update(Long bookId, Long chapterId, ChapterRequest request, Long operatorId);

    void delete(Long bookId, Long chapterId, Long operatorId);
}
