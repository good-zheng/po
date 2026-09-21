package com.goodzheng.po.novel.service.impl;

import com.goodzheng.po.novel.dto.ChapterRequest;
import com.goodzheng.po.novel.entity.Book;
import com.goodzheng.po.novel.entity.BookChapter;
import com.goodzheng.po.novel.repository.BookChapterRepository;
import com.goodzheng.po.novel.repository.BookRepository;
import com.goodzheng.po.novel.service.BookChapterService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;

@Service
@RequiredArgsConstructor
public class BookChapterServiceImpl implements BookChapterService {

    private final BookChapterRepository chapterRepository;
    private final BookRepository bookRepository;

    @Override
    @Transactional(readOnly = true)
    public List<BookChapter> list(Long bookId) {
        checkBookExists(bookId);
        return chapterRepository.findByBookIdAndDeletedAtIsNullOrderByChapterIndexAsc(bookId);
    }

    @Override
    @Transactional(readOnly = true)
    public BookChapter get(Long bookId, Long chapterId) {
        return chapterRepository.findByIdAndBookIdAndDeletedAtIsNull(chapterId, bookId)
                .orElseThrow(() -> new RuntimeException("章节不存在"));
    }

    @Override
    @Transactional
    public BookChapter create(Long bookId, ChapterRequest req, Long operatorId) {
        Book book = checkBookExists(bookId);
        checkOwner(book, operatorId);

        BookChapter chapter = new BookChapter();
        chapter.setBook(book);
        chapter.setTitle(req.getTitle());
        chapter.setContent(req.getContent());
        chapter.setChapterIndex(resolveChapterIndex(bookId, req.getChapterIndex()));
        chapter.setWordCount(calculateWordCount(req.getContent()));

        BookChapter saved = chapterRepository.save(chapter);
        refreshBookWordCount(bookId);
        return saved;
    }

    @Override
    @Transactional
    public BookChapter update(Long bookId, Long chapterId, ChapterRequest req, Long operatorId) {
        Book book = checkBookExists(bookId);
        checkOwner(book, operatorId);

        BookChapter chapter = get(bookId, chapterId);
        chapter.setTitle(req.getTitle());
        chapter.setContent(req.getContent());
        if (req.getChapterIndex() != null) {
            chapter.setChapterIndex(req.getChapterIndex());
        }
        chapter.setWordCount(calculateWordCount(req.getContent()));

        BookChapter saved = chapterRepository.save(chapter);
        refreshBookWordCount(bookId);
        return saved;
    }

    @Override
    @Transactional
    public void delete(Long bookId, Long chapterId, Long operatorId) {
        Book book = checkBookExists(bookId);
        checkOwner(book, operatorId);

        BookChapter chapter = get(bookId, chapterId);
        chapter.setDeletedAt(LocalDateTime.now());
        chapterRepository.save(chapter);
        refreshBookWordCount(bookId);
    }

    // ── 工具方法 ──────────────────────────────────────────

    private Book checkBookExists(Long bookId) {
        Book book = bookRepository.findById(bookId)
                .orElseThrow(() -> new RuntimeException("书籍不存在"));
        if (book.getDeletedAt() != null) {
            throw new RuntimeException("书籍已删除");
        }
        return book;
    }

    private void checkOwner(Book book, Long operatorId) {
        if (!book.getAuthorId().equals(operatorId)) {
            throw new RuntimeException("无权操作他人书籍");
        }
    }

    private Integer resolveChapterIndex(Long bookId, Integer requested) {
        if (requested != null) {
            return requested;
        }
        Integer max = chapterRepository.findMaxChapterIndex(bookId);
        return (max == null ? 0 : max) + 1;
    }

    private int calculateWordCount(String content) {
        if (content == null || content.isBlank()) {
            return 0;
        }
        return content.replaceAll("\\s", "").length();
    }

    private void refreshBookWordCount(Long bookId) {
        Book book = bookRepository.findById(bookId).orElse(null);
        if (book == null) {
            return;
        }
        book.setWordCount(chapterRepository.sumWordCountByBookId(bookId));
        bookRepository.save(book);
    }
}
