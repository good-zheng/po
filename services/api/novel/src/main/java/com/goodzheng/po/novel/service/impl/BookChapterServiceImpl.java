package com.goodzheng.po.novel.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.goodzheng.po.novel.dto.ChapterRequest;
import com.goodzheng.po.novel.entity.Book;
import com.goodzheng.po.novel.entity.BookChapter;
import com.goodzheng.po.novel.repository.BookChapterMapper;
import com.goodzheng.po.novel.repository.BookMapper;
import com.goodzheng.po.novel.service.BookChapterService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Objects;
import java.util.Optional;

@Service
@RequiredArgsConstructor
public class BookChapterServiceImpl implements BookChapterService {

    /** 已定稿：正典出处的可信度分界，改写后必须退回待复核（§10.5-③） */
    private static final String STATUS_COMMITTED = "committed";
    private static final String STATUS_PENDING_REVIEW = "pending_review";

    private final BookChapterMapper chapterMapper;
    private final BookMapper bookMapper;
    private final ChapterSourceRelocator sourceRelocator;

    @Override
    @Transactional(readOnly = true)
    public List<BookChapter> list(Long bookId) {
        checkBookExists(bookId);
        return chapterMapper.selectList(new LambdaQueryWrapper<BookChapter>()
                .eq(BookChapter::getBookId, bookId)
                .isNull(BookChapter::getDeletedAt)
                .orderByAsc(BookChapter::getChapterIndex));
    }

    @Override
    @Transactional(readOnly = true)
    public int countByBook(Long bookId) {
        checkBookExists(bookId);
        // 列名字符串 Wrapper：与 findOne 同一理由，纯单测没有 mapper 注册时
        // LambdaQueryWrapper 取不到列缓存。
        return Math.toIntExact(chapterMapper.selectCount(new QueryWrapper<BookChapter>()
                .eq("book_id", bookId)
                .isNull("deleted_at")));
    }

    @Override
    @Transactional(readOnly = true)
    public int countWrittenByBook(Long bookId) {
        checkBookExists(bookId);
        // word_count 是正文的派生值（create/update 都重算），所以「字数 > 0」与「有正文」
        // 在这一张表上是同一个判定，不需要再去看 content 列。
        return Math.toIntExact(chapterMapper.selectCount(new QueryWrapper<BookChapter>()
                .eq("book_id", bookId)
                .isNull("deleted_at")
                .gt("word_count", 0)));
    }

    @Override
    @Transactional(readOnly = true)
    public BookChapter get(Long bookId, Long chapterId) {
        return findOne(bookId, chapterId)
                .orElseThrow(() -> new RuntimeException("章节不存在"));
    }

    @Override
    @Transactional
    public BookChapter create(Long bookId, ChapterRequest req) {
        checkBookExists(bookId);

        BookChapter chapter = new BookChapter();
        chapter.setBookId(bookId);
        chapter.setChapterIndex(resolveChapterIndex(bookId, req.getChapterIndex()));
        chapter.setTitle(resolveTitle(req.getTitle(), chapter.getChapterIndex()));
        chapter.setContent(req.getContent());
        chapter.setWordCount(calculateWordCount(req.getContent()));

        chapterMapper.insert(chapter);
        refreshBookWordCount(bookId);
        return chapter;
    }

    @Override
    @Transactional
    public BookChapter putByIndex(Long bookId, ChapterRequest req, Long userId) {
        checkBookExists(bookId);
        int index = resolveChapterIndex(bookId, req.getChapterIndex());
        // 章号定下来交出去：下面两条分支都按它落位，不能让 create 再算一次「最大序号+1」
        req.setChapterIndex(index);

        BookChapter existing = chapterMapper.selectOne(new QueryWrapper<BookChapter>()
                .eq("book_id", bookId)
                .eq("chapter_index", index)
                .isNull("deleted_at"));
        if (existing == null) {
            return create(bookId, req);
        }
        if (existing.getWordCount() != null && existing.getWordCount() > 0) {
            // 只 append 的链路撞上了有正文的章号：说清是哪一章、为什么停，而不是静默换掉正文
            throw new RuntimeException("第 " + index + " 章已有正文（" + existing.getWordCount()
                    + " 字），生成链路不改写已写过的章");
        }
        // 占位章：走 update 而不是 insert，行 id 保持不变（正典断言按 chapter_id 溯源），
        // 且正文写入仍然只经过那一条会连带重算的路径
        return update(bookId, existing.getId(), req, userId);
    }

    @Override
    @Transactional
    public BookChapter update(Long bookId, Long chapterId, ChapterRequest req, Long userId) {
        checkBookExists(bookId);

        BookChapter chapter = get(bookId, chapterId);
        String previousContent = chapter.getContent();
        int previousRevision = chapter.getRevision() == null ? 1 : chapter.getRevision();
        boolean contentChanged = !Objects.equals(previousContent, req.getContent());

        if (req.getChapterIndex() != null) {
            chapter.setChapterIndex(req.getChapterIndex());
        }
        chapter.setTitle(resolveTitle(req.getTitle(), chapter.getChapterIndex()));
        chapter.setContent(req.getContent());
        chapter.setWordCount(calculateWordCount(req.getContent()));
        if (contentChanged) {
            // 版本号只跟着正文走：正典断言的出处与黄金集样本按 (chapterId, revision) 引用，
            // 改个标题就加一版会让台账对上从未存在过的内容。
            chapter.setRevision(previousRevision + 1);
            // §10.5-③ 第③件事：已定稿的章被改写就退回「待复核」，重过闸门才准重新 commit
            if (STATUS_COMMITTED.equals(chapter.getStatus())) {
                chapter.setStatus(STATUS_PENDING_REVIEW);
            }
        }

        chapterMapper.updateById(chapter);
        refreshBookWordCount(bookId);
        if (contentChanged) {
            // §10.5-③ 的第①②件事挂在这条唯一的正文写路径上：入口再多也没法只存正文不重算
            sourceRelocator.relocate(chapterId, chapter.getChapterIndex(), previousRevision, previousContent,
                    chapter.getRevision(), req.getContent(), userId);
        }
        return chapter;
    }

    @Override
    @Transactional
    public void delete(Long bookId, Long chapterId) {
        checkBookExists(bookId);

        BookChapter chapter = get(bookId, chapterId);
        chapter.setDeletedAt(LocalDateTime.now());
        chapterMapper.updateById(chapter);
        refreshBookWordCount(bookId);
    }

    // ── 工具方法 ──────────────────────────────────────────

    /**
     * 用列名字符串而不是 {@code LambdaQueryWrapper} 的方法引用：后者在构建阶段就要查
     * MyBatis-Plus 的 lambda 列缓存，纯单测里没有 mapper 注册就没有这份缓存，
     * 而「改正文的连带重算」这条不变量恰恰只能在纯单测里验得干净。
     */
    private Optional<BookChapter> findOne(Long bookId, Long chapterId) {
        return Optional.ofNullable(chapterMapper.selectOne(new QueryWrapper<BookChapter>()
                .eq("id", chapterId)
                .eq("book_id", bookId)
                .isNull("deleted_at")));
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

    /**
     * 缺省章号 = 当前最大章号 + 1（没有章时是 1）。
     *
     * <p>同样用列名字符串而不是方法引用，理由见 {@link #findOne}——「留空排到下一章」是
     * 新建章节那条入口的行为，它得能在纯单测里被验到。
     */
    private Integer resolveChapterIndex(Long bookId, Integer requested) {
        if (requested != null) {
            return requested;
        }
        Integer max = chapterMapper.selectObjs(new QueryWrapper<BookChapter>()
                        .select("chapter_index")
                        .eq("book_id", bookId)
                        .isNull("deleted_at"))
                .stream().map(o -> (Integer) o).max(Integer::compareTo).orElse(null);
        return (max == null ? 0 : max) + 1;
    }

    /**
     * 标题留空时的自动命名。
     *
     * <p>{@code book_chapter.title} 是 NOT NULL，「留空」必须在服务层落成一个可显示的值，
     * 而不是让建章请求在数据库层面报错——占位章的存在理由正是「作者还没决定这一章叫什么」，
     * 等它被生成链路填掉时标题会跟着正文一起换成新章的题。
     */
    private static String resolveTitle(String title, Integer chapterIndex) {
        if (title != null && !title.isBlank()) {
            return title;
        }
        return "第 " + chapterIndex + " 章";
    }

    private int calculateWordCount(String content) {
        if (content == null || content.isBlank()) {
            return 0;
        }
        return content.replaceAll("\\s", "").length();
    }

    private void refreshBookWordCount(Long bookId) {
        Book book = bookMapper.selectById(bookId);
        if (book == null) {
            return;
        }
        book.setWordCount(sumWordCount(bookId));
        bookMapper.updateById(book);
    }

    /** 未删除章节字数合计（等价原 JPQL 的 SUM(word_count)） */
    private int sumWordCount(Long bookId) {
        List<Object> values = chapterMapper.selectObjs(new QueryWrapper<BookChapter>()
                .select("IFNULL(SUM(word_count), 0)")
                .eq("book_id", bookId)
                .isNull("deleted_at"));
        return values.isEmpty() || values.get(0) == null ? 0 : ((Number) values.get(0)).intValue();
    }
}
