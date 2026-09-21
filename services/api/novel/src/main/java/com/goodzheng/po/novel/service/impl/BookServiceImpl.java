package com.goodzheng.po.novel.service.impl;

import com.goodzheng.po.novel.dto.BookRequest;
import com.goodzheng.po.novel.entity.Book;
import com.goodzheng.po.novel.entity.BookChapter;
import com.goodzheng.po.novel.entity.BookCharacter;
import com.goodzheng.po.novel.repository.BookChapterRepository;
import com.goodzheng.po.novel.repository.BookCharacterRepository;
import com.goodzheng.po.novel.repository.BookRepository;
import com.goodzheng.po.novel.service.BookService;
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

    private final BookRepository bookRepository;
    private final BookChapterRepository chapterRepository;
    private final BookCharacterRepository characterRepository;

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
        return bookRepository.save(book);
    }

    @Override
    @Transactional(readOnly = true)
    public Book getById(Long id) {
        Book book = bookRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("书籍不存在"));
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
        return bookRepository.search(kw, g, s, pageable);
    }

    @Override
    @Transactional
    public Book update(Long id, BookRequest req, Long authorId) {
        Book book = getById(id);
        checkOwner(book, authorId);

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
        return bookRepository.save(book);
    }

    @Override
    @Transactional
    public void delete(Long id, Long authorId) {
        Book book = getById(id);
        checkOwner(book, authorId);

        LocalDateTime now = LocalDateTime.now();
        book.setDeletedAt(now);
        bookRepository.save(book);

        // 级联软删除章节和角色
        for (BookChapter chapter : chapterRepository.findByBookIdAndDeletedAtIsNullOrderByChapterIndexAsc(id)) {
            chapter.setDeletedAt(now);
            chapterRepository.save(chapter);
        }
        for (BookCharacter character : characterRepository.findByBookIdAndDeletedAtIsNullOrderByCreatedAtAsc(id)) {
            character.setDeletedAt(now);
            characterRepository.save(character);
        }
    }

    private void checkOwner(Book book, Long authorId) {
        if (!book.getAuthorId().equals(authorId)) {
            throw new RuntimeException("无权操作他人书籍");
        }
    }
}
