package com.goodzheng.po.novel.service;

import com.goodzheng.po.novel.dto.BookRequest;
import com.goodzheng.po.novel.entity.Book;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;

public interface BookService {

    Book create(BookRequest request, Long authorId);

    Book getById(Long id);

    Page<Book> list(String keyword, String genre, String status, Pageable pageable);

    Book update(Long id, BookRequest request);

    void delete(Long id);
}
