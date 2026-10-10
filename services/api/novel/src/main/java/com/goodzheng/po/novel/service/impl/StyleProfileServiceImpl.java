package com.goodzheng.po.novel.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.goodzheng.po.novel.dto.StyleProfileRequest;
import com.goodzheng.po.novel.dto.StyleProfileView;
import com.goodzheng.po.novel.entity.StyleProfile;
import com.goodzheng.po.novel.repository.StyleProfileMapper;
import com.goodzheng.po.novel.service.StyleProfileService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.ArrayList;
import java.util.LinkedHashSet;
import java.util.List;

/**
 * 文风契约读写。
 *
 * <p>三个词表列在库里是 JSON 文本，在接口上是字符串数组，转换只发生在本类：
 * 写入前用 ObjectMapper 造合法 JSON，非法输入挡在应用层比让 MySQL 抛 3140 好归因。
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class StyleProfileServiceImpl implements StyleProfileService {

    private final StyleProfileMapper styleMapper;
    // 与 NovelStudioServiceImpl 同因：Spring Boot 4 只自动装配 Jackson 3 的 ObjectMapper，
    // 这里要的是把词表写成 JSON 文本，不必占容器里的 Bean
    private final ObjectMapper objectMapper = new ObjectMapper();

    @Override
    @Transactional(readOnly = true)
    public StyleProfileView get(Long bookId) {
        StyleProfile row = findRow(bookId);
        return row == null ? null : toView(row);
    }

    @Override
    @Transactional
    public StyleProfileView update(Long bookId, StyleProfileRequest req) {
        requireBand("句长带", req.getSentenceLenMin(), req.getSentenceLenMax());
        requireBand("章字数带", req.getChapterWordsMin(), req.getChapterWordsMax());

        StyleProfile row = findRow(bookId);
        boolean created = row == null;
        if (created) {
            row = new StyleProfile();
            row.setBookId(bookId);
        }
        // null 表示「这次没提」，保留原值；空数组表示「清空这一项」，照写
        if (req.getPerson() != null) {
            row.setPerson(clip(blankToNull(req.getPerson()), 16));
        }
        if (req.getTense() != null) {
            row.setTense(clip(blankToNull(req.getTense()), 16));
        }
        if (req.getSentenceLenMin() != null) {
            row.setSentenceLenMin(req.getSentenceLenMin());
        }
        if (req.getSentenceLenMax() != null) {
            row.setSentenceLenMax(req.getSentenceLenMax());
        }
        if (req.getChapterWordsMin() != null) {
            row.setChapterWordsMin(req.getChapterWordsMin());
        }
        if (req.getChapterWordsMax() != null) {
            row.setChapterWordsMax(req.getChapterWordsMax());
        }
        if (req.getForbiddenWords() != null) {
            row.setForbiddenWords(writeWords(req.getForbiddenWords()));
        }
        if (req.getTics() != null) {
            row.setTics(writeWords(req.getTics()));
        }
        if (req.getTaboo() != null) {
            row.setTaboo(writeWords(req.getTaboo()));
        }
        if (created) {
            styleMapper.insert(row);
        } else {
            styleMapper.updateById(row);
        }
        return toView(row);
    }

    /** {@code uk_style_book} 保证一本书最多一份契约，取不到就是没定过 */
    private StyleProfile findRow(Long bookId) {
        if (bookId == null) {
            throw new RuntimeException("缺少必填字段：bookId");
        }
        return styleMapper.selectOne(new QueryWrapper<StyleProfile>().eq("book_id", bookId));
    }

    private static void requireBand(String label, Integer min, Integer max) {
        if (min != null && max != null && min > max) {
            // 下限大于上限的契约会让每一条正文都违规或永远违规，那是填错了而不是风格
            throw new RuntimeException(label + "的下限不能大于上限：" + min + " > " + max);
        }
    }

    private String writeWords(List<String> words) {
        LinkedHashSet<String> clean = new LinkedHashSet<>();
        for (String word : words) {
            String trimmed = blankToNull(word);
            if (trimmed != null) {
                clean.add(trimmed);
            }
        }
        try {
            return objectMapper.writeValueAsString(new ArrayList<>(clean));
        } catch (JsonProcessingException e) {
            throw new RuntimeException("词表无法序列化为 JSON", e);
        }
    }

    private List<String> readWords(String json) {
        if (json == null || json.isBlank()) {
            return List.of();
        }
        try {
            return objectMapper.readValue(json, new TypeReference<List<String>>() {
            });
        } catch (JsonProcessingException e) {
            // 库里已有非法值时不炸整条读路径：契约的其余字段仍然有效，缺的那项按「无词表」处理
            log.warn("文风契约的词表不是字符串数组，本项按空处理：{}", json);
            return List.of();
        }
    }

    private StyleProfileView toView(StyleProfile row) {
        StyleProfileView view = new StyleProfileView();
        view.setId(row.getId());
        view.setBookId(row.getBookId());
        view.setPerson(row.getPerson());
        view.setTense(row.getTense());
        view.setSentenceLenMin(row.getSentenceLenMin());
        view.setSentenceLenMax(row.getSentenceLenMax());
        view.setChapterWordsMin(row.getChapterWordsMin());
        view.setChapterWordsMax(row.getChapterWordsMax());
        view.setForbiddenWords(readWords(row.getForbiddenWords()));
        view.setTics(readWords(row.getTics()));
        view.setTaboo(readWords(row.getTaboo()));
        return view;
    }

    private static String blankToNull(String value) {
        return value == null || value.isBlank() ? null : value.trim();
    }

    private static String clip(String value, int limit) {
        if (value == null) {
            return null;
        }
        return value.length() <= limit ? value : value.substring(0, limit);
    }
}
