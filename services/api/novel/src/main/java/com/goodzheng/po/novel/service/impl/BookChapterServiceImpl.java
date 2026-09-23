package com.goodzheng.po.novel.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.goodzheng.po.novel.dto.ChapterRequest;
import com.goodzheng.po.novel.entity.Book;
import com.goodzheng.po.novel.entity.BookChapter;
import com.goodzheng.po.novel.repository.BookChapterMapper;
import com.goodzheng.po.novel.repository.BookMapper;
import com.goodzheng.po.novel.service.BookChapterService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Service
@RequiredArgsConstructor
public class BookChapterServiceImpl implements BookChapterService {

    private final BookChapterMapper chapterMapper;
    private final BookMapper bookMapper;

    @Override
    @Transactional(readOnly = true)
    public List<BookChapter> list(Long bookId) {
        checkBookExists(bookId);
        return chapterMapper.selectList(new LambdaQueryWrapper<BookChapter>()
                .eq(BookChapter::getBookId, bookId)
                .isNull(BookChapter::getDeletedAt)
                .orderByAsc(BookChapter::getChapterIndex));
    }

    @Override
    @Transactional(readOnly = true)
    public BookChapter get(Long bookId, Long chapterId) {
        return findOne(bookId, chapterId)
                .orElseThrow(() -> new RuntimeException("章节不存在"));
    }

    @Override
    @Transactional
    public BookChapter create(Long bookId, ChapterRequest req) {
        checkBookExists(bookId);

        BookChapter chapter = new BookChapter();
        chapter.setBookId(bookId);
        chapter.setTitle(req.getTitle());
        chapter.setContent(req.getContent());
        chapter.setChapterIndex(resolveChapterIndex(bookId, req.getChapterIndex()));
        chapter.setWordCount(calculateWordCount(req.getContent()));

        chapterMapper.insert(chapter);
        refreshBookWordCount(bookId);
        return chapter;
    }

    @Override
    @Transactional
    public BookChapter update(Long bookId, Long chapterId, ChapterRequest req) {
        checkBookExists(bookId);

        BookChapter chapter = get(bookId, chapterId);
        chapter.setTitle(req.getTitle());
        chapter.setContent(req.getContent());
        if (req.getChapterIndex() != null) {
            chapter.setChapterIndex(req.getChapterIndex());
        }
        chapter.setWordCount(calculateWordCount(req.getContent()));

        chapterMapper.updateById(chapter);
        refreshBookWordCount(bookId);
        return chapter;
    }

    @Override
    @Transactional
    public void delete(Long bookId, Long chapterId) {
        checkBookExists(bookId);

        BookChapter chapter = get(bookId, chapterId);
        chapter.setDeletedAt(LocalDateTime.now());
        chapterMapper.updateById(chapter);
        refreshBookWordCount(bookId);
    }

    // ── 工具方法 ──────────────────────────────────────────

    private Optional<BookChapter> findOne(Long bookId, Long chapterId) {
        return Optional.ofNullable(chapterMapper.selectOne(new LambdaQueryWrapper<BookChapter>()
                .eq(BookChapter::getId, chapterId)
                .eq(BookChapter::getBookId, bookId)
                .isNull(BookChapter::getDeletedAt)));
    }

    private Book checkBookExists(Long bookId) {
        Book book = bookMapper.selectById(bookId);
        if (book == null) {
            throw new RuntimeException("书籍不存在");
        }
        if (book.getDeletedAt() != null) {
            throw new RuntimeException("书籍已删除");
        }
        return book;
    }

    private Integer resolveChapterIndex(Long bookId, Integer requested) {
        if (requested != null) {
            return requested;
        }
        Integer max = chapterMapper.selectObjs(new LambdaQueryWrapper<BookChapter>()
                        .select(BookChapter::getChapterIndex)
                        .eq(BookChapter::getBookId, bookId)
                        .isNull(BookChapter::getDeletedAt))
                .stream().map(o -> (Integer) o).max(Integer::compareTo).orElse(null);
        return (max == null ? 0 : max) + 1;
    }

    private int calculateWordCount(String content) {
        if (content == null || content.isBlank()) {
            return 0;
        }
        return content.replaceAll("\\s", "").length();
    }

    private void refreshBookWordCount(Long bookId) {
        Book book = bookMapper.selectById(bookId);
        if (book == null) {
            return;
        }
        book.setWordCount(sumWordCount(bookId));
        bookMapper.updateById(book);
    }

    /** 未删除章节字数合计（等价原 JPQL 的 SUM(word_count)） */
    private int sumWordCount(Long bookId) {
        List<Object> values = chapterMapper.selectObjs(new QueryWrapper<BookChapter>()
                .select("IFNULL(SUM(word_count), 0)")
                .eq("book_id", bookId)
                .isNull("deleted_at"));
        return values.isEmpty() || values.get(0) == null ? 0 : ((Number) values.get(0)).intValue();
    }
}
