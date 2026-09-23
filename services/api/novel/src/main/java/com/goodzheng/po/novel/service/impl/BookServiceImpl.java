package com.goodzheng.po.novel.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.goodzheng.po.novel.dto.BookRequest;
import com.goodzheng.po.novel.entity.Book;
import com.goodzheng.po.novel.entity.BookChapter;
import com.goodzheng.po.novel.entity.BookCharacter;
import com.goodzheng.po.novel.repository.BookChapterMapper;
import com.goodzheng.po.novel.repository.BookCharacterMapper;
import com.goodzheng.po.novel.repository.BookMapper;
import com.goodzheng.po.novel.service.BookService;
import com.goodzheng.po.shared.mybatis.MyBatisPages;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.Set;

@Service
@RequiredArgsConstructor
public class BookServiceImpl implements BookService {

    private static final Set<String> VALID_STATUS = Set.of("ongoing", "completed", "paused");

    private final BookMapper bookMapper;
    private final BookChapterMapper chapterMapper;
    private final BookCharacterMapper characterMapper;

    @Override
    @Transactional
    public Book create(BookRequest req, Long authorId) {
        Book book = new Book();
        book.setAuthorId(authorId);
        book.setTitle(req.getTitle());
        book.setDescription(req.getDescription());
        book.setCoverImage(req.getCoverImage());
        book.setGenre(req.getGenre());
        book.setAuthor(req.getAuthor());
        book.setStatus("ongoing");
        book.setWordCount(0);
        bookMapper.insert(book);
        return book;
    }

    @Override
    @Transactional(readOnly = true)
    public Book getById(Long id) {
        Book book = bookMapper.selectById(id);
        if (book == null) {
            throw new RuntimeException("书籍不存在");
        }
        if (book.getDeletedAt() != null) {
            throw new RuntimeException("书籍已删除");
        }
        return book;
    }

    @Override
    @Transactional(readOnly = true)
    public Page<Book> list(String keyword, String genre, String status, Pageable pageable) {
        String kw = (keyword == null || keyword.isBlank()) ? null : keyword.trim();
        String g = (genre == null || genre.isBlank()) ? null : genre.trim();
        String s = (status == null || status.isBlank()) ? null : status.trim();
        LambdaQueryWrapper<Book> wrapper = new LambdaQueryWrapper<Book>()
                .isNull(Book::getDeletedAt)
                .eq(g != null, Book::getGenre, g)
                .eq(s != null, Book::getStatus, s)
                .and(kw != null, w -> w.like(Book::getTitle, kw)
                        .or().like(Book::getDescription, kw));
        var mpPage = MyBatisPages.<Book>toMpPage(pageable);
        bookMapper.selectPage(mpPage, wrapper);
        return MyBatisPages.toPage(mpPage, pageable);
    }

    @Override
    @Transactional
    public Book update(Long id, BookRequest req) {
        Book book = getById(id);

        book.setTitle(req.getTitle());
        book.setDescription(req.getDescription());
        book.setCoverImage(req.getCoverImage());
        book.setGenre(req.getGenre());
        book.setAuthor(req.getAuthor());
        if (req.getStatus() != null && !req.getStatus().isBlank()) {
            if (!VALID_STATUS.contains(req.getStatus())) {
                throw new RuntimeException("无效的创作状态");
            }
            book.setStatus(req.getStatus());
        }
        bookMapper.updateById(book);
        return book;
    }

    @Override
    @Transactional
    public void delete(Long id) {
        Book book = getById(id);

        LocalDateTime now = LocalDateTime.now();
        book.setDeletedAt(now);
        bookMapper.updateById(book);

        // 级联软删除章节和角色
        for (BookChapter chapter : chapterMapper.selectList(
                new LambdaQueryWrapper<BookChapter>()
                        .eq(BookChapter::getBookId, id)
                        .isNull(BookChapter::getDeletedAt))) {
            chapter.setDeletedAt(now);
            chapterMapper.updateById(chapter);
        }
        for (BookCharacter character : characterMapper.selectList(
                new LambdaQueryWrapper<BookCharacter>()
                        .eq(BookCharacter::getBookId, id)
                        .isNull(BookCharacter::getDeletedAt))) {
            character.setDeletedAt(now);
            characterMapper.updateById(character);
        }
    }
}
