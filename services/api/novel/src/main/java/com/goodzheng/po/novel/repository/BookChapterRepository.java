package com.goodzheng.po.novel.repository;

import com.goodzheng.po.novel.entity.BookChapter;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface BookChapterRepository extends JpaRepository<BookChapter, Long> {

    /** 某本书的章节列表（按章节序号升序） */
    List<BookChapter> findByBookIdAndDeletedAtIsNullOrderByChapterIndexAsc(Long bookId);

    /** 单个章节（限未删除） */
    Optional<BookChapter> findByIdAndBookIdAndDeletedAtIsNull(Long id, Long bookId);

    /** 当前最大章节序号 */
    @Query("SELECT MAX(c.chapterIndex) FROM BookChapter c WHERE c.book.id = :bookId AND c.deletedAt IS NULL")
    Integer findMaxChapterIndex(@Param("bookId") Long bookId);

    /** 未删除章节字数合计 */
    @Query("SELECT COALESCE(SUM(c.wordCount), 0) FROM BookChapter c WHERE c.book.id = :bookId AND c.deletedAt IS NULL")
    Integer sumWordCountByBookId(@Param("bookId") Long bookId);

    long countByBookIdAndDeletedAtIsNull(Long bookId);
}
