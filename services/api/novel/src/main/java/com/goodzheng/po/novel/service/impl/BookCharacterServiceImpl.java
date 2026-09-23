package com.goodzheng.po.novel.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.goodzheng.po.novel.dto.CharacterRequest;
import com.goodzheng.po.novel.entity.Book;
import com.goodzheng.po.novel.entity.BookCharacter;
import com.goodzheng.po.novel.repository.BookCharacterMapper;
import com.goodzheng.po.novel.repository.BookMapper;
import com.goodzheng.po.novel.service.BookCharacterService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Service
@RequiredArgsConstructor
public class BookCharacterServiceImpl implements BookCharacterService {

    private final BookCharacterMapper characterMapper;
    private final BookMapper bookMapper;

    @Override
    @Transactional(readOnly = true)
    public List<BookCharacter> list(Long bookId) {
        checkBookExists(bookId);
        return characterMapper.selectList(new LambdaQueryWrapper<BookCharacter>()
                .eq(BookCharacter::getBookId, bookId)
                .isNull(BookCharacter::getDeletedAt)
                .orderByAsc(BookCharacter::getCreatedAt));
    }

    @Override
    @Transactional(readOnly = true)
    public BookCharacter get(Long bookId, Long characterId) {
        return findOne(bookId, characterId)
                .orElseThrow(() -> new RuntimeException("角色不存在"));
    }

    @Override
    @Transactional
    public BookCharacter create(Long bookId, CharacterRequest req) {
        checkBookExists(bookId);

        BookCharacter character = new BookCharacter();
        character.setBookId(bookId);
        character.setName(req.getName());
        character.setDescription(req.getDescription());
        character.setAvatar(req.getAvatar());
        characterMapper.insert(character);
        return character;
    }

    @Override
    @Transactional
    public BookCharacter update(Long bookId, Long characterId, CharacterRequest req) {
        checkBookExists(bookId);

        BookCharacter character = get(bookId, characterId);
        character.setName(req.getName());
        character.setDescription(req.getDescription());
        character.setAvatar(req.getAvatar());
        characterMapper.updateById(character);
        return character;
    }

    @Override
    @Transactional
    public void delete(Long bookId, Long characterId) {
        checkBookExists(bookId);

        BookCharacter character = get(bookId, characterId);
        character.setDeletedAt(LocalDateTime.now());
        characterMapper.updateById(character);
    }

    private Optional<BookCharacter> findOne(Long bookId, Long characterId) {
        return Optional.ofNullable(characterMapper.selectOne(new LambdaQueryWrapper<BookCharacter>()
                .eq(BookCharacter::getId, characterId)
                .eq(BookCharacter::getBookId, bookId)
                .isNull(BookCharacter::getDeletedAt)));
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
}
