package com.goodzheng.po.novel.service.impl;

import com.goodzheng.po.novel.dto.CharacterRequest;
import com.goodzheng.po.novel.entity.Book;
import com.goodzheng.po.novel.entity.BookCharacter;
import com.goodzheng.po.novel.repository.BookCharacterRepository;
import com.goodzheng.po.novel.repository.BookRepository;
import com.goodzheng.po.novel.service.BookCharacterService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;

@Service
@RequiredArgsConstructor
public class BookCharacterServiceImpl implements BookCharacterService {

    private final BookCharacterRepository characterRepository;
    private final BookRepository bookRepository;

    @Override
    @Transactional(readOnly = true)
    public List<BookCharacter> list(Long bookId) {
        checkBookExists(bookId);
        return characterRepository.findByBookIdAndDeletedAtIsNullOrderByCreatedAtAsc(bookId);
    }

    @Override
    @Transactional(readOnly = true)
    public BookCharacter get(Long bookId, Long characterId) {
        return characterRepository.findByIdAndBookIdAndDeletedAtIsNull(characterId, bookId)
                .orElseThrow(() -> new RuntimeException("角色不存在"));
    }

    @Override
    @Transactional
    public BookCharacter create(Long bookId, CharacterRequest req, Long operatorId) {
        Book book = checkBookExists(bookId);
        checkOwner(book, operatorId);

        BookCharacter character = new BookCharacter();
        character.setBook(book);
        character.setName(req.getName());
        character.setDescription(req.getDescription());
        character.setAvatar(req.getAvatar());
        return characterRepository.save(character);
    }

    @Override
    @Transactional
    public BookCharacter update(Long bookId, Long characterId, CharacterRequest req, Long operatorId) {
        Book book = checkBookExists(bookId);
        checkOwner(book, operatorId);

        BookCharacter character = get(bookId, characterId);
        character.setName(req.getName());
        character.setDescription(req.getDescription());
        character.setAvatar(req.getAvatar());
        return characterRepository.save(character);
    }

    @Override
    @Transactional
    public void delete(Long bookId, Long characterId, Long operatorId) {
        Book book = checkBookExists(bookId);
        checkOwner(book, operatorId);

        BookCharacter character = get(bookId, characterId);
        character.setDeletedAt(LocalDateTime.now());
        characterRepository.save(character);
    }

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
}
