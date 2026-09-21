package com.goodzheng.po.novel.repository;

import com.goodzheng.po.novel.entity.Book;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

@Repository
public interface BookRepository extends JpaRepository<Book, Long> {

    /** 分页查询（类型/状态/关键词均可选，互不冲突） */
    @Query("""
            SELECT b FROM Book b
            WHERE b.deletedAt IS NULL
              AND (:genre IS NULL OR b.genre = :genre)
              AND (:status IS NULL OR b.status = :status)
              AND (:keyword IS NULL
                   OR b.title LIKE CONCAT('%', :keyword, '%')
                   OR b.description LIKE CONCAT('%', :keyword, '%'))
            """)
    Page<Book> search(@Param("keyword") String keyword,
                      @Param("genre") String genre,
                      @Param("status") String status,
                      Pageable pageable);
}
