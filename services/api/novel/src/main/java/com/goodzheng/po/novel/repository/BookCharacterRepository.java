package com.goodzheng.po.novel.repository;

import com.goodzheng.po.novel.entity.BookCharacter;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface BookCharacterRepository extends JpaRepository<BookCharacter, Long> {

    /** 某本书的角色列表（按创建时间升序） */
    List<BookCharacter> findByBookIdAndDeletedAtIsNullOrderByCreatedAtAsc(Long bookId);

    /** 单个角色（限未删除） */
    Optional<BookCharacter> findByIdAndBookIdAndDeletedAtIsNull(Long id, Long bookId);
}
