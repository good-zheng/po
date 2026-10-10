package com.goodzheng.po.novel.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.goodzheng.po.novel.entity.CanonEntry;
import com.goodzheng.po.novel.entity.ChapterRevision;
import com.goodzheng.po.novel.entity.ReviewFinding;
import com.goodzheng.po.novel.repository.CanonEntryMapper;
import com.goodzheng.po.novel.repository.ChapterRevisionMapper;
import com.goodzheng.po.novel.repository.ReviewFindingMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.List;
import java.util.Objects;

/**
 * 作者改正文后的连带重算（§10.5-③ 的四件事）。
 *
 * <p>正文是正典断言的**出处**（{@code source_chapter_id + start/end}），一改就可能悬空。
 * 本组件只由 {@link BookChapterServiceImpl#update} 在事务内调用——把重算放在唯一的正文写路径上
 * 而不是各入口，是因为「改完必重校验」这条约束一旦能被绕过就等于不存在
 * （与 {@code authority} 只能由服务端判定同构）。
 *
 * <p>空白归一口径必须与 Python 侧 {@code gates._WHITESPACE} 一致，否则「这条引文还在不在正文里」
 * 两边答案不同，闸门收下过的证据会在管理端被判成孤儿。
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class ChapterSourceRelocator {

    /**
     * 出处已失效：断言的引文在改写后的正文里逐字找不到了。
     *
     * <p>刻意**不**加进 Python 的 {@code schemas.FindingCode}——闸门永远不产这个码，它只由
     * 改稿路径写入；台账里因此能一眼分出「模型报的」与「作者自己改出来的」。
     */
    public static final String CODE_SOURCE_ORPHANED = "source_orphaned";

    private static final String STATUS_OPEN = "open";
    private static final String STATUS_ORPHANED = "orphaned";

    private final ChapterRevisionMapper revisionMapper;
    private final CanonEntryMapper canonMapper;
    private final ReviewFindingMapper findingMapper;

    /**
     * @param chapterIndex 章号，只用于台账里给人看的说明文字
     * @param oldRevision  被改写的那一版编号，其正文进 {@code chapter_revision}
     * @param oldContent   被改写的正文
     * @param newRevision  改写后的当前编号
     * @param newContent   改写后的正文
     * @param userId       作者 ID；非人类调用方传 null
     */
    @Transactional
    public void relocate(Long chapterId, Integer chapterIndex, int oldRevision, String oldContent,
            int newRevision, String newContent, Long userId) {
        snapshot(chapterId, oldRevision, oldContent, userId);
        int orphaned = relocateCanonSources(chapterId, chapterIndex, newRevision, newContent);
        int staleFindings = markOrphanedFindings(chapterId, newContent);
        if (orphaned > 0 || staleFindings > 0) {
            log.info("第 {} 章改稿：{} 条断言出处失效，{} 条待裁定冲突的证据已失效",
                    chapterIndex, orphaned, staleFindings);
        }
    }

    /** ① 旧文不覆盖：让位出去的那一版落一行快照 */
    private void snapshot(Long chapterId, int revision, String content, Long userId) {
        String body = content == null ? "" : content;
        Long already = revisionMapper.selectCount(new QueryWrapper<ChapterRevision>()
                .eq("chapter_id", chapterId)
                .eq("revision", revision));
        if (already != null && already > 0) {
            // 同一版只可能让位一次。重复到达还去覆盖，(chapter_id, revision) 就失去唯一含义了
            return;
        }
        ChapterRevision row = new ChapterRevision();
        row.setChapterId(chapterId);
        row.setRevision(revision);
        row.setContent(body);
        row.setContentHash(sha256Hex(body));
        row.setCreatedBy(userId);
        revisionMapper.insert(row);
    }

    /** ② 逐条重定位引用该章的断言 span：找得到就搬位置，找不到就进台账 */
    private int relocateCanonSources(Long chapterId, Integer chapterIndex, int newRevision, String newContent) {
        List<CanonEntry> entries = canonMapper.selectList(new QueryWrapper<CanonEntry>()
                .eq("source_chapter_id", chapterId)
                .isNotNull("evidence_quote")
                .orderByAsc("id"));
        int orphaned = 0;
        for (CanonEntry entry : entries) {
            Span span = locate(newContent, entry.getEvidenceQuote(), entry.getSourceStart());
            if (span == null) {
                writeOrphanRow(entry, chapterIndex, newRevision);
                orphaned++;
                continue;
            }
            // 引文还在但位置动了（作者在前面插了一段）：只搬 span，断言内容一个字都不改
            if (!Objects.equals(span.start(), entry.getSourceStart())
                    || !Objects.equals(span.end(), entry.getSourceEnd())) {
                entry.setSourceStart(span.start());
                entry.setSourceEnd(span.end());
                canonMapper.updateById(entry);
            }
        }
        return orphaned;
    }

    /**
     * 失效出处进台账，一条断言一行。
     *
     * <p>断言本身不动——作者改的可能是更准确的说法，也可能是手滑，能判断的只有作者；
     * 这里只负责把「这条断言暂时没有可核对的原文」摆出来。
     * {@code text_start/text_end} 留空：新版本里本就没有这段位置，填旧坐标等于指着一行不存在的字，
     * 且 NULL 不参与唯一键冲突，同章两条断言引同一句也不会撞 {@code uk_finding_dedup}。
     */
    private void writeOrphanRow(CanonEntry entry, Integer chapterIndex, int newRevision) {
        String refs = "[" + entry.getId() + "]";
        Long exists = findingMapper.selectCount(new QueryWrapper<ReviewFinding>()
                .eq("chapter_id", entry.getSourceChapterId())
                .eq("code", CODE_SOURCE_ORPHANED)
                .eq("status", STATUS_OPEN)
                .eq("canon_refs", refs));
        if (exists != null && exists > 0) {
            // 反复改稿不该把台账刷成一串重复行：未裁定的那条继续挂着
            return;
        }
        ReviewFinding finding = new ReviewFinding();
        finding.setBookId(entry.getBookId());
        finding.setChapterId(entry.getSourceChapterId());
        finding.setRevision(newRevision);
        finding.setCode(CODE_SOURCE_ORPHANED);
        finding.setSeverity("major");
        finding.setChecker("rule");
        finding.setCanonRefs(refs);
        finding.setEvidenceQuote(entry.getEvidenceQuote());
        finding.setExplanation("作者改写第 " + chapterIndex + " 章正文后，这条断言的出处引文已不在该章正文中逐字出现。"
                + "断言内容未被改动，但它暂时没有可核对的原文。");
        finding.setFixInstruction("把正文改回含该引文的句子，或在「设定」Tab 按新原文重录这条断言的出处。");
        finding.setStatus(STATUS_OPEN);
        findingMapper.insert(finding);
    }

    /**
     * 该章未裁定的冲突，证据引文若已被改掉则标 {@code orphaned}（③ 的一部分：改过的章要重过闸门）。
     *
     * <p>不删行：黄金集样本按 {@code (chapter_id, revision)} 引用，删掉就再也无法复现「当时模型报了什么」。
     * {@code source_orphaned} 自身被排除——它的引文按定义就是找不到，否则会立刻把自己刷成孤儿。
     */
    private int markOrphanedFindings(Long chapterId, String newContent) {
        List<ReviewFinding> rows = findingMapper.selectList(new QueryWrapper<ReviewFinding>()
                .eq("chapter_id", chapterId)
                .eq("status", STATUS_OPEN)
                .ne("code", CODE_SOURCE_ORPHANED)
                .isNotNull("evidence_quote"));
        int count = 0;
        for (ReviewFinding row : rows) {
            if (locate(newContent, row.getEvidenceQuote(), row.getTextStart()) != null) {
                continue;
            }
            row.setStatus(STATUS_ORPHANED);
            findingMapper.updateById(row);
            count++;
        }
        return count;
    }

    // ── 定位工具 ──────────────────────────────────────────

    /**
     * 把引文逐字找回来，返回它在**原始正文**里的区间（半开，与 {@code canon_entry.source_*} 同口径）。
     *
     * <p>命中多处时取离旧起点最近的一处：改稿通常只动局部，同一句重现的概率远高于它被整体挪走，
     * 按「第一个匹配」搬 span 会把出处指到错误的段落上。
     */
    static Span locate(String text, String quote, Integer preferredStart) {
        if (text == null || quote == null) {
            return null;
        }
        String needle = stripGaps(quote);
        if (needle.isEmpty()) {
            return null;
        }
        int[] rawAt = new int[text.length()];
        StringBuilder haystack = new StringBuilder(text.length());
        for (int i = 0; i < text.length(); i++) {
            char c = text.charAt(i);
            if (isGap(c)) {
                continue;
            }
            rawAt[haystack.length()] = i;
            haystack.append(c);
        }
        Span best = null;
        int drift = Integer.MAX_VALUE;
        for (int at = haystack.indexOf(needle); at >= 0; at = haystack.indexOf(needle, at + 1)) {
            int distance = preferredStart == null ? 0 : Math.abs(rawAt[at] - preferredStart);
            if (distance < drift) {
                drift = distance;
                best = new Span(rawAt[at], rawAt[at + needle.length() - 1] + 1);
            }
        }
        return best;
    }

    private static String stripGaps(String value) {
        StringBuilder sb = new StringBuilder(value.length());
        for (int i = 0; i < value.length(); i++) {
            char c = value.charAt(i);
            if (!isGap(c)) {
                sb.append(c);
            }
        }
        return sb.toString();
    }

    /**
     * 抹空白，口径等价于 Python 的 {@code re.sub(r"\s+", "", s)}。
     *
     * <p>Java 的 {@code \s} 默认只认 ASCII，中文正文里的全角空格（U+3000）、不换行空格（U+00A0）
     * 与行分隔符（U+2028/2029）必须一并算作空白，否则同一句引文两边判定相反。
     */
    private static boolean isGap(char c) {
        return Character.isWhitespace(c)
                || Character.isSpaceChar(c)
                || (c >= 0x1C && c <= 0x1F)
                || c == 0x85;
    }

    static String sha256Hex(String text) {
        try {
            byte[] digest = MessageDigest.getInstance("SHA-256").digest(text.getBytes(StandardCharsets.UTF_8));
            StringBuilder hex = new StringBuilder(digest.length * 2);
            for (byte b : digest) {
                hex.append(Character.forDigit((b >> 4) & 0xF, 16)).append(Character.forDigit(b & 0xF, 16));
            }
            return hex.toString();
        } catch (NoSuchAlgorithmException e) {
            throw new IllegalStateException("SHA-256 不可用", e);
        }
    }

    /** 正文里的半开区间 */
    record Span(int start, int end) {
    }
}
