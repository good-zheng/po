package com.goodzheng.po.novel.controller;

import com.goodzheng.po.novel.dto.BookRequest;
import com.goodzheng.po.novel.dto.ChapterRequest;
import com.goodzheng.po.novel.dto.CharacterRequest;
import com.goodzheng.po.novel.dto.InternalActorView;
import com.goodzheng.po.novel.dto.InternalAssertionAppendRequest;
import com.goodzheng.po.novel.dto.InternalAssertionCloseRequest;
import com.goodzheng.po.novel.dto.InternalBookView;
import com.goodzheng.po.novel.dto.InternalChatTicketRequest;
import com.goodzheng.po.novel.dto.InternalFindingRequest;
import com.goodzheng.po.novel.dto.InternalSummaryRequest;
import com.goodzheng.po.novel.dto.InternalSummaryView;
import com.goodzheng.po.novel.dto.InternalWriteResult;
import com.goodzheng.po.novel.dto.StyleProfileView;
import com.goodzheng.po.novel.entity.Alias;
import com.goodzheng.po.novel.entity.Book;
import com.goodzheng.po.novel.entity.BookChapter;
import com.goodzheng.po.novel.entity.BookCharacter;
import com.goodzheng.po.novel.entity.CanonEntry;
import com.goodzheng.po.novel.entity.Foreshadow;
import com.goodzheng.po.novel.repository.AliasMapper;
import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.goodzheng.po.novel.service.BookChapterService;
import com.goodzheng.po.novel.service.BookCharacterService;
import com.goodzheng.po.novel.service.BookService;
import com.goodzheng.po.novel.service.CanonInternalService;
import com.goodzheng.po.novel.service.ChatTicketService;
import com.goodzheng.po.novel.service.StyleProfileService;
import com.goodzheng.po.shared.dto.Result;
import jakarta.servlet.http.HttpServletRequest;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.Arrays;
import java.util.List;

/**
 * agent-novel 的内网回调通道（{@code X-Internal-Token}）。
 *
 * <p>为什么要单独一条通道而不是让 Python 复用 {@code /books/**}：那条写接口按
 * SecurityConfig 口径要求管理端 JWT，而 JWT 只活 24 小时——把用户令牌存进 chat
 * 服务等于造一个会过期 yet 长期持有的凭据，运维上迟早变成「定时脚本偷偷续期」。
 * 内网令牌走 TalkController 同一家族：端点在 SecurityConfig 放行、由本类自校，
 * 令牌未配置时一律拒绝。
 *
 * <p>本类只保证「写入者是被授权的内网服务」，不保证内容正确——正典的权威级在这里
 * 一律写死 {@code model}（见 CanonTxWriter），作者级只能走管理端裁定接口（N5b）。
 *
 * <p>读口另有一层作者作用域：chat 服务在校验握手票据（{@code /internal/chat-ticket/verify}）
 * 之后带上 {@code X-Actor-Uid}，带了就必须是该书作者，否则 403。这一层是为了补 §15.13-12 那个
 * 「WS 对等方用别人的 bookId 读正典」的缺口，写在读侧是因为读口才是数据的出口。
 */
@Slf4j
@RestController
@RequestMapping("/novel")
@RequiredArgsConstructor
public class NovelInternalController {

    private static final String INTERNAL_HEADER = "X-Internal-Token";

    /**
     * 调用方代表的作者（chat 在校验握手票据后带上）。缺省即「没有终端用户身份」，
     * 走的是生成链路那种「内网服务自己写自己的书」的旧口径，见 {@link #actorUid}。
     */
    private static final String ACTOR_HEADER = "X-Actor-Uid";

    private final CanonInternalService canonService;
    private final BookService bookService;
    private final BookChapterService chapterService;
    private final BookCharacterService characterService;
    private final AliasMapper aliasMapper;
    // 与管理端读写同一份实现：作者定的契约和闸门用的契约必须是一个数
    private final StyleProfileService styleService;
    // 握手票据的验票方：chat 服务没有 JWT 库，也不该再持一份签名密钥
    private final ChatTicketService chatTicketService;

    /** 内部回调令牌；未配置时一律拒绝（安全默认值） */
    @Value("${app.internal-token:}")
    private String internalToken;

    // ── 握手票据校验 ──────────────────────────────────────

    /**
     * chat 服务在 WS 握手阶段拿到的票据交回这里校验，成功即换回作者身份。
     *
     * <p>为什么由 Java 验而不是 chat 自验：票据与用户 JWT 同钥签名，让 Python 校验等于把
     * {@code jwt.secret} 分发到第二个服务（多一处密钥、云托管多一个环境变量，且两处都能签
     * 就两处可伪造）。chat 已经持 {@code X-Internal-Token} 打这条内网通道，验票顺路。
     *
     * <p>失败一律 403 而不是把「票据过期」与「票据伪造」分档返回：客户端不需要据此区别处理，
     * 而区分它们会把有效期信息泄漏给外部探测者。
     */
    @PostMapping("/internal/chat-ticket/verify")
    public Result<InternalActorView> verifyChatTicket(HttpServletRequest http,
            @RequestBody(required = false) InternalChatTicketRequest request) {
        Result<InternalActorView> denied = denyUnlessInternal(http);
        if (denied != null) {
            return denied;
        }
        Long uid = request == null ? null : chatTicketService.consume(request.getTicket());
        if (uid == null) {
            return Result.error(403, "握手票据无效");
        }
        InternalActorView view = new InternalActorView();
        view.setUid(uid);
        return Result.success(view);
    }

    // ── 正典写入通道 ──────────────────────────────────────

    @PostMapping("/internal/assertions:append")
    public Result<InternalWriteResult> appendAssertions(HttpServletRequest http,
            @RequestBody(required = false) InternalAssertionAppendRequest request) {
        Result<InternalWriteResult> denied = denyUnlessInternal(http);
        if (denied != null) {
            return denied;
        }
        if (request == null) {
            return Result.error(400, "请求体缺失");
        }
        try {
            return Result.success(canonService.append(request));
        } catch (RuntimeException e) {
            return Result.error(400, e.getMessage());
        }
    }

    @PostMapping("/internal/assertions:close")
    public Result<InternalWriteResult> closeAssertion(HttpServletRequest http,
            @RequestBody(required = false) InternalAssertionCloseRequest request) {
        Result<InternalWriteResult> denied = denyUnlessInternal(http);
        if (denied != null) {
            return denied;
        }
        if (request == null) {
            return Result.error(400, "请求体缺失");
        }
        try {
            return Result.success(canonService.close(request));
        } catch (RuntimeException e) {
            return Result.error(400, e.getMessage());
        }
    }

    @PostMapping("/internal/findings")
    public Result<InternalWriteResult> saveFindings(HttpServletRequest http,
            @RequestBody(required = false) InternalFindingRequest request) {
        Result<InternalWriteResult> denied = denyUnlessInternal(http);
        if (denied != null) {
            return denied;
        }
        if (request == null) {
            return Result.error(400, "请求体缺失");
        }
        try {
            return Result.success(canonService.saveFindings(request));
        } catch (RuntimeException e) {
            return Result.error(400, e.getMessage());
        }
    }

    @PostMapping("/internal/summaries")
    public Result<InternalWriteResult> saveSummaries(HttpServletRequest http,
            @RequestBody(required = false) InternalSummaryRequest request) {
        Result<InternalWriteResult> denied = denyUnlessInternal(http);
        if (denied != null) {
            return denied;
        }
        if (request == null) {
            return Result.error(400, "请求体缺失");
        }
        try {
            return Result.success(canonService.saveSummaries(request));
        } catch (RuntimeException e) {
            return Result.error(400, e.getMessage());
        }
    }

    // ── 正典读取（as-of 快照，注入侧唯一入口） ─────────────

    @GetMapping("/internal/canon/snapshot")
    public Result<List<CanonEntry>> snapshot(HttpServletRequest http,
            @RequestParam Long bookId,
            @RequestParam Integer asOf,
            @RequestParam(required = false) String entities,
            @RequestParam(required = false) String kinds) {
        Result<List<CanonEntry>> denied = denyUnlessInternal(http);
        if (denied != null) {
            return denied;
        }
        Result<List<CanonEntry>> foreign = denyUnlessActorOwns(http, bookId);
        if (foreign != null) {
            return foreign;
        }
        try {
            return Result.success(canonService.snapshot(bookId, asOf, split(entities), split(kinds)));
        } catch (RuntimeException e) {
            return Result.error(400, e.getMessage());
        }
    }

    @GetMapping("/internal/canon/foreshadows/open")
    public Result<List<Foreshadow>> openForeshadows(HttpServletRequest http,
            @RequestParam Long bookId,
            @RequestParam Integer asOf) {
        Result<List<Foreshadow>> denied = denyUnlessInternal(http);
        if (denied != null) {
            return denied;
        }
        Result<List<Foreshadow>> foreign = denyUnlessActorOwns(http, bookId);
        if (foreign != null) {
            return foreign;
        }
        try {
            return Result.success(canonService.openForeshadows(bookId, asOf));
        } catch (RuntimeException e) {
            return Result.error(400, e.getMessage());
        }
    }

    @GetMapping("/internal/canon/aliases")
    public Result<List<Alias>> aliases(HttpServletRequest http, @RequestParam Long bookId) {
        Result<List<Alias>> denied = denyUnlessInternal(http);
        if (denied != null) {
            return denied;
        }
        Result<List<Alias>> foreign = denyUnlessActorOwns(http, bookId);
        if (foreign != null) {
            return foreign;
        }
        return Result.success(aliasMapper.selectList(new LambdaQueryWrapper<Alias>()
                .eq(Alias::getBookId, bookId)
                .orderByAsc(Alias::getId)));
    }

    /**
     * 文风契约读回（Tier-0 与确定性闸门的同一份）。
     *
     * <p>没有契约行时返回 {@code data: null}，这是「作者还没定过契约」而不是错误：装配侧
     * 据此退回本轮构思派生的默认契约，Tier-0 因此永不为空。让读回缺省时抛错会让一本新书
     * 在第一次 worldbuild 之前就取不到上下文。
     */
    @GetMapping("/internal/canon/style")
    public Result<StyleProfileView> style(HttpServletRequest http, @RequestParam Long bookId) {
        Result<StyleProfileView> denied = denyUnlessInternal(http);
        if (denied != null) {
            return denied;
        }
        Result<StyleProfileView> foreign = denyUnlessActorOwns(http, bookId);
        if (foreign != null) {
            return foreign;
        }
        return Result.success(styleService.get(bookId));
    }

    /**
     * 层级摘要读取（L1 编译器用）。as-of 口径与 {@code /canon/snapshot} 不同：摘要只在整个
     * 覆盖区间都落在 {@code upto} 之前时才返回，相交即剧透——详见 CanonInternalService#summaries。
     */
    @GetMapping("/internal/canon/summaries")
    public Result<List<InternalSummaryView>> summaries(HttpServletRequest http,
            @RequestParam Long bookId,
            @RequestParam Integer upto,
            @RequestParam(required = false) String levels,
            @RequestParam(required = false) Integer limit) {
        Result<List<InternalSummaryView>> denied = denyUnlessInternal(http);
        if (denied != null) {
            return denied;
        }
        Result<List<InternalSummaryView>> foreign = denyUnlessActorOwns(http, bookId);
        if (foreign != null) {
            return foreign;
        }
        try {
            return Result.success(canonService.summaries(bookId, upto, split(levels), limit));
        } catch (RuntimeException e) {
            return Result.error(400, e.getMessage());
        }
    }

    // ── 成稿入库（归档确认后的 book / chapter / character） ──

    /**
     * 书本读回（对话面板装配用，§10.3-②「同一份上下文」）。
     *
     * <p>参照章按 {@code chapterId} 点名单章，整本正文不过网：L1 编译器对已定稿章节
     * 只读那一章的标题与末尾原文，其余都在摘要树里。缺这一条读口时，对话侧就只能
     * 自己拼一份「大概一样」的上下文，而两份上下文的差异恰好是查不出来的那种漂移。
     */
    @GetMapping("/internal/books/detail")
    public Result<InternalBookView> bookDetail(HttpServletRequest http,
            @RequestParam Long bookId,
            @RequestParam(required = false) Long chapterId) {
        Result<InternalBookView> denied = denyUnlessInternal(http);
        if (denied != null) {
            return denied;
        }
        final Long actor;
        try {
            actor = actorUid(http);
        } catch (IllegalArgumentException e) {
            return Result.error(400, e.getMessage());
        }
        try {
            Book book = bookService.getById(bookId);
            // 归属校验放在这里而不是复用 denyUnlessActorOwns：这本 Book 无论如何都要读出来，
            // 再查一次只是多打一条 SQL
            if (actor != null && !actor.equals(book.getAuthorId())) {
                log.warn("拒绝越界的书本读回：actor={} bookId={}", actor, bookId);
                return Result.error(403, "无权读取该书");
            }
            InternalBookView view = new InternalBookView();
            view.setBookId(book.getId());
            view.setTitle(book.getTitle());
            view.setGenre(book.getGenre());
            view.setSummary(book.getSummary());
            view.setChapterCount(chapterService.countWrittenByBook(bookId));
            if (chapterId != null) {
                // get 自带 book 归属校验：别的书的章号打到这里一样抛「章节不存在」
                BookChapter chapter = chapterService.get(bookId, chapterId);
                InternalBookView.Chapter one = new InternalBookView.Chapter();
                one.setChapterId(chapter.getId());
                one.setChapterIndex(chapter.getChapterIndex());
                one.setTitle(chapter.getTitle());
                one.setContent(chapter.getContent());
                view.setChapter(one);
            }
            return Result.success(view);
        } catch (RuntimeException e) {
            return Result.error(400, e.getMessage());
        }
    }

    @PostMapping("/internal/books")
    public Result<Book> createBook(HttpServletRequest http,
            @RequestParam Long authorId,
            @RequestBody(required = false) BookRequest request) {
        Result<Book> denied = denyUnlessInternal(http);
        if (denied != null) {
            return denied;
        }
        if (request == null) {
            return Result.error(400, "请求体缺失");
        }
        try {
            return Result.success(bookService.create(request, authorId));
        } catch (RuntimeException e) {
            return Result.error(400, e.getMessage());
        }
    }

    /**
     * 生成链路写章：按章号落位，不是无条件插一行。
     *
     * <p>作者在新建章节里留空排下的「待写占位」就是这一条要填的那一行；同号已有正文时报错而不是
     * 覆盖——续写的语义是只往后追加，撞上有字的章说明库里的进度和这一轮的判断不一致，
     * 静默改写会把正典断言的出处换成一份不再存在的正文。
     */
    @PostMapping("/internal/books/{bookId}/chapters")
    public Result<BookChapter> putChapter(HttpServletRequest http,
            @PathVariable Long bookId,
            @RequestBody(required = false) ChapterRequest request) {
        Result<BookChapter> denied = denyUnlessInternal(http);
        if (denied != null) {
            return denied;
        }
        if (request == null) {
            return Result.error(400, "请求体缺失");
        }
        final Long actor;
        try {
            actor = actorUid(http);
        } catch (IllegalArgumentException e) {
            return Result.error(400, e.getMessage());
        }
        try {
            return Result.success(chapterService.putByIndex(bookId, request, actor));
        } catch (RuntimeException e) {
            return Result.error(400, e.getMessage());
        }
    }

    @PostMapping("/internal/books/{bookId}/characters")
    public Result<BookCharacter> createCharacter(HttpServletRequest http,
            @PathVariable Long bookId,
            @RequestBody(required = false) CharacterRequest request) {
        Result<BookCharacter> denied = denyUnlessInternal(http);
        if (denied != null) {
            return denied;
        }
        if (request == null) {
            return Result.error(400, "请求体缺失");
        }
        try {
            return Result.success(characterService.create(bookId, request));
        } catch (RuntimeException e) {
            return Result.error(400, e.getMessage());
        }
    }

    /** 令牌校验：通过返回 null，否则返回可直接回给调用方的 403 信封（业务失败仍是 HTTP 200） */
    private <T> Result<T> denyUnlessInternal(HttpServletRequest http) {
        String token = http.getHeader(INTERNAL_HEADER);
        if (internalToken.isBlank() || !internalToken.equals(token)) {
            log.warn("拒绝未授权的内部调用：{} {}（令牌{}）",
                    http.getMethod(), http.getRequestURI(), internalToken.isBlank() ? "未配置" : "不匹配");
            return Result.error(403, "内部令牌无效");
        }
        return null;
    }

    /**
     * 作者作用域（§15.13-12 的读面收口）：带 {@code X-Actor-Uid} 的读只能读自己名下的书。
     *
     * <p>按「带了才校验」而不是「没带就拒」：同一条内网通道有两类调用方——对话面板的读有作者
     * 在场（越界必须拒），生成链路读的是本轮自己刚归档的书（此刻没有终端用户身份可带）。
     * 一刀切拒掉会打断生成链路，一刀切放行等于没修那个缺口。
     *
     * <p>「带不带」本身不是客户端能选的：chat 只在握手票据经
     * {@code /internal/chat-ticket/verify} 验过之后才发这个头，所以头在这里出现就意味着
     * 身份已由签名方确认过。
     */
    private <T> Result<T> denyUnlessActorOwns(HttpServletRequest http, Long bookId) {
        final Long actor;
        try {
            actor = actorUid(http);
        } catch (IllegalArgumentException e) {
            return Result.error(400, e.getMessage());
        }
        if (actor == null) {
            return null;
        }
        final Book book;
        try {
            book = bookService.getById(bookId);
        } catch (RuntimeException e) {
            // 书不存在与「书不属于你」给同一个回：前者同样不该把内容吐出去，也不泄漏它存在过
            log.warn("拒绝越界的正典读：actor={} bookId={}（读回失败：{}）", actor, bookId, e.getMessage());
            return Result.error(403, "无权读取该书的正典");
        }
        if (book == null || !actor.equals(book.getAuthorId())) {
            log.warn("拒绝越界的正典读：actor={} bookId={}", actor, bookId);
            return Result.error(403, "无权读取该书的正典");
        }
        return null;
    }

    /** 读请求所代表的作者；缺省返回 {@code null}（生成链路那一类没有终端用户在场的读） */
    private static Long actorUid(HttpServletRequest http) {
        String raw = http.getHeader(ACTOR_HEADER);
        if (raw == null || raw.isBlank()) {
            return null;
        }
        try {
            return Long.valueOf(raw.trim());
        } catch (NumberFormatException e) {
            throw new IllegalArgumentException(ACTOR_HEADER + " 不是合法的用户 id");
        }
    }

    private static List<String> split(String csv) {
        if (csv == null || csv.isBlank()) {
            return List.of();
        }
        return Arrays.stream(csv.split(",")).map(String::trim).filter(s -> !s.isEmpty()).toList();
    }
}
