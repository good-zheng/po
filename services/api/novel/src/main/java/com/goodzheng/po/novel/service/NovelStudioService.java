package com.goodzheng.po.novel.service;

import com.goodzheng.po.novel.dto.AliasRequest;
import com.goodzheng.po.novel.dto.CanonRequest;
import com.goodzheng.po.novel.dto.CanonRetireRequest;
import com.goodzheng.po.novel.dto.ChapterImpactView;
import com.goodzheng.po.novel.dto.ChapterRevisionView;
import com.goodzheng.po.novel.dto.FindingAdjudicationRequest;
import com.goodzheng.po.novel.dto.FindingAdjudicationView;
import com.goodzheng.po.novel.dto.FindingView;
import com.goodzheng.po.novel.dto.ForeshadowRequest;
import com.goodzheng.po.novel.dto.NovelProgressView;
import com.goodzheng.po.novel.entity.Alias;
import com.goodzheng.po.novel.entity.CanonEntry;
import com.goodzheng.po.novel.entity.Foreshadow;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;

import java.util.List;

/**
 * 创作工作台的管理端读写面（§15 末尾那张表）。
 *
 * <p>与 {@link CanonInternalService} 分开的理由不是路径而是身份：内部通道拿内网令牌，
 * 只能写 model 级；本接口拿管理端 JWT，是 {@code author} 级唯一的入口。
 * 两者共用一张表但绝不能共用一个写方法，否则「谁都能把自己标成作者」这条路就会在
 * 某个重构里被顺手合并掉。
 */
public interface NovelStudioService {

    // ── 正典 ──────────────────────────────────────────────

    Page<CanonEntry> canonPage(Long bookId, String subjectKey, String kind,
            String status, String authority, Long sourceChapterId, String keyword,
            Pageable pageable);

    /** 单条断言：工作台中栏要按 id 取「被点中的那一条」的出处原句，不该为此摊开全书设定 */
    CanonEntry canonById(Long canonId);

    CanonEntry createCanon(Long bookId, CanonRequest req, Long userId);

    CanonEntry updateCanon(Long canonId, CanonRequest req, Long userId);

    CanonEntry retireCanon(Long canonId, CanonRetireRequest req, Long userId);

    /**
     * 写入前的确定性冲突预览（§10.6 最后一行）：同主同谓且值不同的已生效断言。
     *
     * <p>作者点头不能省这一步——「作者已确认」会让污染拿到正名，而同屏列出「要覆盖哪条、
     * 旧区间是否关闭」才让裁定是有信息的裁定。纯比对，不调模型。
     *
     * @param excludeId 正在被编辑的那条断言自身：改自己的值不算和自己撞车，传 {@code null} 表示新建
     */
    List<CanonEntry> previewConflicts(Long bookId, CanonRequest req, Integer asOfChapter, Long excludeId);

    /**
     * 该书当前最大章号，即作者视角里的「现在」。
     *
     * <p>没有章时返回 {@code null} 而不是 0：0 会让「开篇即有」的断言被写成「第 0 章确立」，
     * 而那是伪造记忆。提议卡采纳与手改设定共用这一个口径，两处对「现在」的理解不许分叉。
     */
    Integer currentChapterIndex(Long bookId);

    // ── 别名 ──────────────────────────────────────────────

    List<Alias> listAliases(Long bookId);

    Alias updateAlias(Long bookId, Long aliasId, AliasRequest req);

    // ── 伏笔 ──────────────────────────────────────────────

    List<Foreshadow> listForeshadows(Long bookId, String status);

    Foreshadow createForeshadow(Long bookId, ForeshadowRequest req);

    Foreshadow updateForeshadow(Long bookId, Long foreshadowId, ForeshadowRequest req);

    // ── 冲突台账 ──────────────────────────────────────────

    /**
     * @param chapterId 只看某一章的冲突；设定级冲突（没有落点章）的 {@code chapter_id} 为 NULL，
     *                  按章筛时天然不出现，所以中栏「本章冲突」只收闸门真正落在这一章上的那些
     */
    Page<FindingView> findingPage(Long bookId, Long chapterId, String severity, String status,
            String checker, String code, Pageable pageable);

    FindingAdjudicationView adjudicate(Long findingId, FindingAdjudicationRequest req, Long userId);

    // ── 章节版本与改稿影响 ────────────────────────────────

    /**
     * 本章的全部正文版本，当前版本在第一位。
     *
     * <p>{@code (chapterId, revision)} 是断言出处与黄金集样本的坐标：没有这段历史，
     * 作者改完正文就再也定位不到断言当初引的是哪一版原文，已录的误报样本也会失去可比性（§12）。
     */
    List<ChapterRevisionView> chapterRevisions(Long bookId, Long chapterId);

    /** 改这一章会波及谁：受影响的后章清单 + 出处已失效的断言（§10.5-③ 的第④件事） */
    ChapterImpactView chapterImpact(Long bookId, Long chapterId);

    // ── 进度 ──────────────────────────────────────────────

    NovelProgressView progress(Long bookId);
}
