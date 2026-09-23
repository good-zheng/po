package com.goodzheng.po.novel.service;

import com.goodzheng.po.novel.dto.CharacterRequest;
import com.goodzheng.po.novel.entity.BookCharacter;

import java.util.List;

public interface BookCharacterService {

    List<BookCharacter> list(Long bookId);

    BookCharacter get(Long bookId, Long characterId);

    BookCharacter create(Long bookId, CharacterRequest request);

    BookCharacter update(Long bookId, Long characterId, CharacterRequest request);

    void delete(Long bookId, Long characterId);
}
