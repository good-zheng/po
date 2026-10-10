package com.goodzheng.po.novel.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.goodzheng.po.novel.dto.SearchResultsView;
import com.goodzheng.po.novel.entity.Alias;
import com.goodzheng.po.novel.entity.BookChapter;
import com.goodzheng.po.novel.entity.CanonEntry;
import com.goodzheng.po.novel.repository.AliasMapper;
import com.goodzheng.po.novel.repository.BookChapterMapper;
import com.goodzheng.po.novel.repository.CanonEntryMapper;
import com.goodzheng.po.novel.service.NovelSearchService;
import com.goodzheng.po.shared.mybatis.MyBatisPages;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.ArrayList;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Objects;
import java.util.Set;
import java.util.stream.Stream;

/**
 * 统一检索的实现：三条 {@code LIKE} 加一次别名展开，没有别的机制。
 *
 * <p>刻意不做跨 scope 的混排打分，也不给查询词加引号语法——一期能回答「哪儿出现过这个名字」
 * 就够左栏用了，把 MySQL 伪装成搜索引擎会让下一次真需要 ES 时误判「已经有了」。
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class NovelSearchServiceImpl implements NovelSearchService {

    private static final String SCOPE_CHAPTER = "chapter";
    private static final String SCOPE_CANON = "canon";
    private static final String SCOPE_ALIAS = "alias";

    private static final Set<String> SCOPES = Set.of(SCOPE_CHAPTER, SCOPE_CANON, SCOPE_ALIAS);

    /** 命中处前后各留的字符数：够读出一个句子，又不至于把整章拖进左栏 */
    private static final int EXCERPT_PAD = 40;

    private final BookChapterMapper chapterMapper;
    private final CanonEntryMapper canonMapper;
    private final AliasMapper aliasMapper;

    @Override
    @Transactional(readOnly = true)
    public SearchResultsView search(Long bookId, String query, List<String> scopes, Pageable pageable) {
        SearchResultsView view = new SearchResultsView();
        String q = query == null ? "" : query.trim();
        List<String> wanted = wantedScopes(scopes);
        view.setBookId(bookId);
        view.setQuery(q);
        view.setScopes(wanted);
        if (q.isEmpty() || wanted.isEmpty() || pageable == null) {
            // 空词不查：LIKE '%%' 会把全书章节连正文一起捞出来，那不是检索而是拖库
            return view;
        }

        if (wanted.contains(SCOPE_CHAPTER)) {
            searchChapters(bookId, q, pageable, view);
        }
        List<String> entityKeys = wanted.contains(SCOPE_CANON) || wanted.contains(SCOPE_ALIAS)
                ? expandEntityKeys(bookId, q) : List.of();
        view.setExpandedEntityKeys(entityKeys);
        if (wanted.contains(SCOPE_CANON)) {
            searchCanon(bookId, q, entityKeys, pageable, view);
        }
        if (wanted.contains(SCOPE_ALIAS)) {
            searchAliases(bookId, q, pageable, view);
        }
        return view;
    }

    // ── 各 scope ──────────────────────────────────────────

    private void searchChapters(Long bookId, String q, Pageable pageable, SearchResultsView view) {
        var mpPage = MyBatisPages.<BookChapter>toMpPage(pageable);
        chapterMapper.selectPage(mpPage, chapterWrapper(bookId, q).orderByAsc("chapter_index"));
        view.setChapterTotal(mpPage.getTotal());
        for (BookChapter chapter : mpPage.getRecords()) {
            SearchResultsView.ChapterHit hit = new SearchResultsView.ChapterHit();
            hit.setChapterId(chapter.getId());
            hit.setChapterIndex(chapter.getChapterIndex());
            hit.setTitle(chapter.getTitle());
            hit.setStatus(chapter.getStatus());
            hit.setRevision(chapter.getRevision());
            hit.setExcerpt(excerpt(chapter.getContent(), q));
            view.getChapters().add(hit);
        }
    }

    private void searchCanon(Long bookId, String q, List<String> entityKeys, Pageable pageable,
            SearchResultsView view) {
        var mpPage = MyBatisPages.<CanonEntry>toMpPage(pageable);
        canonMapper.selectPage(mpPage, canonWrapper(bookId, q, entityKeys).orderByDesc("id"));
        view.setCanonTotal(mpPage.getTotal());
        for (CanonEntry entry : mpPage.getRecords()) {
            SearchResultsView.CanonHit hit = new SearchResultsView.CanonHit();
            hit.setCanonId(entry.getId());
            hit.setKind(entry.getKind());
            hit.setSubjectKey(entry.getSubjectKey());
            hit.setPredicate(entry.getPredicate());
            hit.setObjectText(entry.getObjectText());
            hit.setAuthority(entry.getAuthority());
            hit.setStatus(entry.getStatus());
            hit.setValidFromChapter(entry.getValidFromChapter());
            hit.setValidUntilChapter(entry.getValidUntilChapter());
            // 只靠别名展开命中时，四列文本里并没有查询词，前端要标出「因别名而命中」
            hit.setMatchedViaAlias(!contains(entry, q));
            view.getCanon().add(hit);
        }
    }

    private void searchAliases(Long bookId, String q, Pageable pageable, SearchResultsView view) {
        String like = likeValue(q);
        var mpPage = MyBatisPages.<Alias>toMpPage(pageable);
        aliasMapper.selectPage(mpPage, new QueryWrapper<Alias>()
                .eq("book_id", bookId)
                // entity_key 也参与匹配：作者记得的是归一后的键（char:qing），未必记得哪个称谓指向它
                .and(w -> w.like("alias_text", like).or().like("entity_key", like))
                .orderByAsc("entity_key")
                .orderByAsc("alias_text"));
        view.setAliasTotal(mpPage.getTotal());
        for (Alias alias : mpPage.getRecords()) {
            SearchResultsView.AliasHit hit = new SearchResultsView.AliasHit();
            hit.setAliasId(alias.getId());
            hit.setEntityKey(alias.getEntityKey());
            hit.setAliasText(alias.getAliasText());
            hit.setFirstSeenChapter(alias.getFirstSeenChapter());
            hit.setIsPrimary(alias.getIsPrimary());
            view.getAliases().add(hit);
        }
    }

    /**
     * 别名展开：查询词命中的称谓，换成它们所属的实体键。
     *
     * <p>这是「一次检索穿过三张表」里唯一有信息量的一步。查不到别名不是错误，是「这个词还没被
     * 归一」的信号——正文与设定仍按字面命中，只是别名的那一路没接上（§8-⑧ 不许静默降级，
     * 故展开结果原样回显在 {@code expandedEntityKeys}）。
     */
    private List<String> expandEntityKeys(Long bookId, String q) {
        LinkedHashSet<String> keys = new LinkedHashSet<>();
        for (Alias alias : aliasMapper.selectList(new QueryWrapper<Alias>()
                .select("DISTINCT entity_key")
                .eq("book_id", bookId)
                .like("alias_text", likeValue(q)))) {
            if (alias.getEntityKey() != null && !alias.getEntityKey().isBlank()) {
                keys.add(alias.getEntityKey());
            }
        }
        return new ArrayList<>(keys);
    }

    private QueryWrapper<BookChapter> chapterWrapper(Long bookId, String q) {
        String like = likeValue(q);
        return new QueryWrapper<BookChapter>()
                .eq("book_id", bookId)
                .isNull("deleted_at")
                // 标题与正文同一条 OR：作者搜「渡口」多半在找那一章，而不是在数全书出现过几次
                .and(w -> w.like("title", like).or().like("content", like))
                .select("id", "chapter_index", "title", "status", "revision", "content");
    }

    private QueryWrapper<CanonEntry> canonWrapper(Long bookId, String q, List<String> entityKeys) {
        String like = likeValue(q);
        return new QueryWrapper<CanonEntry>()
                .eq("book_id", bookId)
                .and(w -> {
                    w.like("subject_key", like).or().like("predicate", like)
                            .or().like("object_text", like).or().like("restatement", like);
                    if (!entityKeys.isEmpty()) {
                        w.or().in("subject_key", entityKeys);
                    }
                })
                // 不过滤 status：被停用与被驳回的断言正是作者回查时最想看「当初为什么这么写」的那些
                .select("id", "kind", "subject_key", "predicate", "object_text", "authority",
                        "status", "valid_from_chapter", "valid_until_chapter");
    }

    // ── 工具 ──────────────────────────────────────────────

    private static List<String> wantedScopes(List<String> scopes) {
        if (scopes == null || scopes.isEmpty()) {
            return List.of(SCOPE_CHAPTER, SCOPE_CANON, SCOPE_ALIAS);
        }
        List<String> out = new ArrayList<>();
        for (String scope : scopes) {
            String normalized = scope == null ? "" : scope.trim().toLowerCase();
            if (SCOPES.contains(normalized) && !out.contains(normalized)) {
                out.add(normalized);
            }
        }
        return out;
    }

    /**
     * LIKE 的值侧转义。
     *
     * <p>MySQL 的 LIKE 转义符就是反斜杠，所以先转 {@code \} 再转 {@code %} 与 {@code _}；
     * 不转的话作者搜「100%」会命中全书，而搜「a_b」会命中 axb——MyBatis-Plus 的
     * {@code like()} 只加百分号，不负责这件事。
     */
    static String likeValue(String raw) {
        return raw.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_");
    }

    /** 命中处前后各截一段；找不到（库层做了大小写与全半角折叠而 Java 没折）就退回段首 */
    static String excerpt(String content, String q) {
        if (content == null || content.isEmpty()) {
            return "";
        }
        int at = content.toLowerCase().indexOf(q.toLowerCase());
        if (at < 0) {
            return flatten(content.substring(0, Math.min(content.length(), 2 * EXCERPT_PAD))) + "…";
        }
        int from = Math.max(0, at - EXCERPT_PAD);
        int to = Math.min(content.length(), at + q.length() + EXCERPT_PAD);
        return (from > 0 ? "…" : "") + flatten(content.substring(from, to))
                + (to < content.length() ? "…" : "");
    }

    /** 摘出来是要贴着一行显示的，正文里的换行与缩进会把它撑成一段 */
    private static String flatten(String text) {
        return text.replaceAll("\\s+", " ").trim();
    }

    private static boolean contains(CanonEntry entry, String q) {
        String needle = q.toLowerCase();
        return Stream.of(entry.getSubjectKey(), entry.getPredicate(), entry.getObjectText(),
                        entry.getRestatement())
                .filter(Objects::nonNull)
                .anyMatch(text -> text.toLowerCase().contains(needle));
    }
}
