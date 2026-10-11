package com.goodzheng.po.novel.controller;

import com.goodzheng.po.identity.security.AuthUser;
import com.goodzheng.po.novel.dto.AliasRequest;
import com.goodzheng.po.novel.dto.CanonRequest;
import com.goodzheng.po.novel.dto.CanonRetireRequest;
import com.goodzheng.po.novel.dto.ChatTicketView;
import com.goodzheng.po.novel.dto.ChapterImpactView;
import com.goodzheng.po.novel.dto.ChapterRevisionView;
import com.goodzheng.po.novel.dto.FindingAdjudicationRequest;
import com.goodzheng.po.novel.dto.FindingAdjudicationView;
import com.goodzheng.po.novel.dto.FindingView;
import com.goodzheng.po.novel.dto.ForeshadowRequest;
import com.goodzheng.po.novel.dto.NovelProgressView;
import com.goodzheng.po.novel.dto.ProposalDecisionRequest;
import com.goodzheng.po.novel.dto.ProposalDecisionView;
import com.goodzheng.po.novel.dto.ProposalRequest;
import com.goodzheng.po.novel.dto.SearchResultsView;
import com.goodzheng.po.novel.dto.StyleProfileRequest;
import com.goodzheng.po.novel.dto.StyleProfileView;
import com.goodzheng.po.novel.entity.Alias;
import com.goodzheng.po.novel.entity.CanonEntry;
import com.goodzheng.po.novel.entity.CanonProposal;
import com.goodzheng.po.novel.entity.Foreshadow;
import com.goodzheng.po.novel.service.CanonProposalService;
import com.goodzheng.po.novel.service.ChatTicketService;
import com.goodzheng.po.novel.service.NovelSearchService;
import com.goodzheng.po.novel.service.NovelStudioService;
import com.goodzheng.po.novel.service.StyleProfileService;
import com.goodzheng.po.shared.dto.Result;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PatchMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

/**
 * 创作工作台的管理端接口（§15 末尾那张表）。
 *
 * <p>与 {@link NovelInternalController} 的区别是身份而不是路径：这里的每一个写动作都以
 * 「作者本人」为准，{@code authority} 一律服务端写死 {@code author}，请求体里没有这个字段
 * 也不可能有（§10.5-②）。访问控制由 SecurityConfig 的 {@code /novel/** → ADMIN_CLIENT} 收口
 * （{@code /novel/internal/**} 那条 permitAll 在前面先匹配，内网通道不受影响）。
 */
@RestController
@RequestMapping("/novel")
@RequiredArgsConstructor
public class NovelStudioController {

    private static final int MAX_PAGE_SIZE = 200;

    /** 检索一页的上限比正典更严：章节命中带正文节选，一页两百条就是几兆字节的响应 */
    private static final int MAX_SEARCH_SIZE = 50;

    private final NovelStudioService studioService;
    private final NovelSearchService searchService;
    private final CanonProposalService proposalService;
    private final StyleProfileService styleService;
    private final ChatTicketService chatTicketService;

    // ── 正典：设定 Tab ────────────────────────────────────

    @GetMapping("/books/{bookId}/canon")
    public Result<Page<CanonEntry>> canonPage(@PathVariable Long bookId,
            @RequestParam(required = false) String subjectKey,
            @RequestParam(required = false) String kind,
            @RequestParam(required = false) String status,
            @RequestParam(required = false) String authority,
            @RequestParam(required = false) Long sourceChapterId,
            @RequestParam(required = false) String keyword,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size) {
        return Result.success(studioService.canonPage(bookId, subjectKey, kind, status, authority,
                sourceChapterId, keyword, pageRequest(page, size)));
    }

    /** 单条断言：工作台中栏点中某一条时要按 id 取它的出处原句，不该为此摊开整本设定 */
    @GetMapping("/canon/{id}")
    public Result<CanonEntry> canon(@PathVariable Long id) {
        try {
            return Result.success(studioService.canonById(id));
        } catch (RuntimeException e) {
            return Result.error(404, e.getMessage());
        }
    }

    /**
     * 写入前的冲突预览（§10.6）：同主同谓且值不同的已生效断言。
     * 作者点头不能省这一步，否则「作者已确认」会变成污染的正名。
     */
    @GetMapping("/books/{bookId}/canon/conflicts")
    public Result<List<CanonEntry>> canonConflicts(@PathVariable Long bookId,
            @RequestParam(required = false) String subjectKey,
            @RequestParam(required = false) String predicate,
            @RequestParam(required = false) String objectText,
            @RequestParam(required = false) Integer asOfChapter,
            @RequestParam(required = false) Long excludeId) {
        CanonRequest probe = new CanonRequest();
        probe.setSubjectKey(subjectKey);
        probe.setPredicate(predicate);
        probe.setObjectText(objectText);
        try {
            return Result.success(studioService.previewConflicts(bookId, probe, asOfChapter, excludeId));
        } catch (RuntimeException e) {
            return Result.error(400, e.getMessage());
        }
    }

    @PostMapping("/books/{bookId}/canon")
    public Result<CanonEntry> createCanon(@AuthenticationPrincipal AuthUser principal,
            @PathVariable Long bookId,
            @RequestBody CanonRequest request) {
        try {
            return Result.success(studioService.createCanon(bookId, request, principal.id()));
        } catch (RuntimeException e) {
            return Result.error(400, e.getMessage());
        }
    }

    @PatchMapping("/canon/{id}")
    public Result<CanonEntry> updateCanon(@AuthenticationPrincipal AuthUser principal,
            @PathVariable Long id,
            @RequestBody CanonRequest request) {
        try {
            return Result.success(studioService.updateCanon(id, request, principal.id()));
        } catch (RuntimeException e) {
            return Result.error(400, e.getMessage());
        }
    }

    @PostMapping("/canon/{id}/retire")
    public Result<CanonEntry> retireCanon(@AuthenticationPrincipal AuthUser principal,
            @PathVariable Long id,
            @RequestBody(required = false) CanonRetireRequest request) {
        try {
            return Result.success(studioService.retireCanon(id, request, principal.id()));
        } catch (RuntimeException e) {
            return Result.error(400, e.getMessage());
        }
    }

    // ── 别名：别名 Tab ────────────────────────────────────

    @GetMapping("/books/{bookId}/aliases")
    public Result<List<Alias>> aliases(@PathVariable Long bookId) {
        return Result.success(studioService.listAliases(bookId));
    }

    @PutMapping("/books/{bookId}/aliases/{aliasId}")
    public Result<Alias> updateAlias(@PathVariable Long bookId, @PathVariable Long aliasId,
            @RequestBody AliasRequest request) {
        try {
            return Result.success(studioService.updateAlias(bookId, aliasId, request));
        } catch (RuntimeException e) {
            return Result.error(400, e.getMessage());
        }
    }

    // ── 伏笔：伏笔 Tab ────────────────────────────────────

    @GetMapping("/books/{bookId}/foreshadows")
    public Result<List<Foreshadow>> foreshadows(@PathVariable Long bookId,
            @RequestParam(required = false) String status) {
        return Result.success(studioService.listForeshadows(bookId, status));
    }

    @PostMapping("/books/{bookId}/foreshadows")
    public Result<Foreshadow> createForeshadow(@PathVariable Long bookId,
            @RequestBody ForeshadowRequest request) {
        try {
            return Result.success(studioService.createForeshadow(bookId, request));
        } catch (RuntimeException e) {
            return Result.error(400, e.getMessage());
        }
    }

    @PutMapping("/books/{bookId}/foreshadows/{foreshadowId}")
    public Result<Foreshadow> updateForeshadow(@PathVariable Long bookId, @PathVariable Long foreshadowId,
            @RequestBody ForeshadowRequest request) {
        try {
            return Result.success(studioService.updateForeshadow(bookId, foreshadowId, request));
        } catch (RuntimeException e) {
            return Result.error(400, e.getMessage());
        }
    }

    // ── 章节版本与改稿影响 ────────────────────────────────

    /**
     * 本章的正文版本历史（当前版本在第一位），工作台中栏的 diff 取这里。
     *
     * <p>挂在 {@code /novel/**} 而不是读者侧的 {@code /books/**}：历史正文里可能含尚未定稿的
     * 伏笔与被改掉的事实，读者的口径不外扩（§10.5-①）。
     */
    @GetMapping("/books/{bookId}/chapters/{chapterId}/revisions")
    public Result<List<ChapterRevisionView>> chapterRevisions(@PathVariable Long bookId,
            @PathVariable Long chapterId) {
        try {
            return Result.success(studioService.chapterRevisions(bookId, chapterId));
        } catch (RuntimeException e) {
            return Result.error(404, e.getMessage());
        }
    }

    /** 改这一章会波及谁。保存前后都该看一眼：事前看风险，事后看新出现的失效出处 */
    @GetMapping("/books/{bookId}/chapters/{chapterId}/impact")
    public Result<ChapterImpactView> chapterImpact(@PathVariable Long bookId,
            @PathVariable Long chapterId) {
        try {
            return Result.success(studioService.chapterImpact(bookId, chapterId));
        } catch (RuntimeException e) {
            return Result.error(404, e.getMessage());
        }
    }

    // ── 统一检索：左栏 ────────────────────────────────────

    /**
     * 章题、正文、正典断言、人名别名一起搜（§10.3 左栏）。
     *
     * <p>{@code scope} 可重复也可逗号分隔，缺省三样都查；结果<b>按 scope 分节</b>返回，
     * 各节自带 total，分页参数对每一节分别生效。
     */
    @GetMapping("/books/{bookId}/search")
    public Result<SearchResultsView> search(@PathVariable Long bookId,
            @RequestParam(required = false) String q,
            @RequestParam(required = false) List<String> scope,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size) {
        int safeSize = Math.max(1, Math.min(size, MAX_SEARCH_SIZE));
        return Result.success(searchService.search(bookId, q, scope,
                PageRequest.of(Math.max(0, page), safeSize)));
    }

    // ── 提议卡：右栏 ──────────────────────────────────────

    @GetMapping("/proposals")
    public Result<Page<CanonProposal>> proposals(@RequestParam(required = false) Long bookId,
            @RequestParam(required = false) String status,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size) {
        try {
            return Result.success(proposalService.page(bookId, status, pageRequest(page, size)));
        } catch (RuntimeException e) {
            return Result.error(400, e.getMessage());
        }
    }

    /**
     * 提议卡入库。
     *
     * <p>由工作台前端代作者提交：右栏的卡片是模型说的话，入队是作者把它留在台账上的动作。
     * 状态服务端写死 pending，入参里也没有 status（§10.3 约定 3）。
     */
    @PostMapping("/proposals")
    public Result<CanonProposal> createProposal(@RequestBody ProposalRequest request) {
        try {
            return Result.success(proposalService.create(request));
        } catch (RuntimeException e) {
            return Result.error(400, e.getMessage());
        }
    }

    /** 采纳 → {@code canon_entry(authority=author)}；撞车未显式指定覆盖项时整体不落库 */
    @PutMapping("/proposals/{proposalId}/adopt")
    public Result<ProposalDecisionView> adoptProposal(@AuthenticationPrincipal AuthUser principal,
            @PathVariable Long proposalId,
            @RequestBody(required = false) ProposalDecisionRequest request) {
        try {
            return Result.success(proposalService.adopt(proposalId, request, principal.id()));
        } catch (RuntimeException e) {
            return Result.error(400, e.getMessage());
        }
    }

    @PutMapping("/proposals/{proposalId}/dismiss")
    public Result<ProposalDecisionView> dismissProposal(@AuthenticationPrincipal AuthUser principal,
            @PathVariable Long proposalId,
            @RequestBody(required = false) ProposalDecisionRequest request) {
        try {
            return Result.success(proposalService.dismiss(proposalId, request, principal.id()));
        } catch (RuntimeException e) {
            return Result.error(400, e.getMessage());
        }
    }

    // ── 文风契约 ──────────────────────────────────────────

    /** 一本没定过契约的书返回 null：那是「还没有契约」，装配侧据此退回派生的默认契约 */
    @GetMapping("/books/{bookId}/style")
    public Result<StyleProfileView> style(@PathVariable Long bookId) {
        return Result.success(styleService.get(bookId));
    }

    /** PUT 而不是 PATCH：契约是整份覆盖的语义，未提供的字段保留原值已经写在服务侧了 */
    @PutMapping("/books/{bookId}/style")
    public Result<StyleProfileView> updateStyle(@PathVariable Long bookId,
            @RequestBody StyleProfileRequest request) {
        try {
            return Result.success(styleService.update(bookId, request));
        } catch (RuntimeException e) {
            return Result.error(400, e.getMessage());
        }
    }

    // ── 冲突台账 ──────────────────────────────────────────

    @GetMapping("/reviews")
    public Result<Page<FindingView>> reviews(@RequestParam(required = false) Long bookId,
            @RequestParam(required = false) Long chapterId,
            @RequestParam(required = false) String severity,
            @RequestParam(required = false) String status,
            @RequestParam(required = false) String checker,
            @RequestParam(required = false) String code,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size) {
        return Result.success(studioService.findingPage(bookId, chapterId, severity, status, checker,
                code, pageRequest(page, size)));
    }

    @PutMapping("/reviews/{findingId}")
    public Result<FindingAdjudicationView> adjudicate(@AuthenticationPrincipal AuthUser principal,
            @PathVariable Long findingId,
            @RequestBody FindingAdjudicationRequest request) {
        try {
            return Result.success(studioService.adjudicate(findingId, request, principal.id()));
        } catch (RuntimeException e) {
            return Result.error(400, e.getMessage());
        }
    }

    // ── 进度 ──────────────────────────────────────────────

    @GetMapping("/progress")
    public Result<NovelProgressView> progress(@RequestParam Long bookId) {
        return Result.success(studioService.progress(bookId));
    }

    // ── 对话面板握手票据 ──────────────────────────────────

    /**
     * 换一张 60 秒的一次性票据去开 {@code /ws/chat} 的连接（右栏 novel-chat 用它证明「是谁在读」）。
     *
     * <p>放在 {@code /novel/**} 而不是 {@code /auth/**} 下：SecurityConfig 里这一族要求
     * ADMIN_CLIENT，于是「能领到读正典的票」与「能进创作工作台」是同一个门槛，不必再造第二条
     * 规则。票据只带 uid，不带角色，所以它不能当会话令牌拿去打普通接口。
     */
    @GetMapping("/chat-ticket")
    public Result<ChatTicketView> chatTicket(@AuthenticationPrincipal AuthUser principal) {
        ChatTicketView view = new ChatTicketView();
        view.setTicket(chatTicketService.issue(principal.id()));
        view.setExpiresIn(chatTicketService.expiresIn());
        return Result.success(view);
    }

    /** size 夹在 [1,200]：正典表一页拉一万行会把作者的浏览器变成渲染事故现场 */
    private static PageRequest pageRequest(int page, int size) {
        int safeSize = Math.max(1, Math.min(size, MAX_PAGE_SIZE));
        return PageRequest.of(Math.max(0, page), safeSize);
    }
}
