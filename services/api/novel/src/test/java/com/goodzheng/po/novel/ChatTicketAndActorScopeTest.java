package com.goodzheng.po.novel;

import com.goodzheng.po.identity.security.AuthUser;
import com.goodzheng.po.identity.security.JwtUtil;
import com.goodzheng.po.novel.controller.NovelInternalController;
import com.goodzheng.po.novel.dto.ChapterRequest;
import com.goodzheng.po.novel.dto.InternalActorView;
import com.goodzheng.po.novel.dto.InternalBookView;
import com.goodzheng.po.novel.dto.InternalChatTicketRequest;
import com.goodzheng.po.novel.entity.Book;
import com.goodzheng.po.novel.entity.CanonEntry;
import com.goodzheng.po.novel.repository.AliasMapper;
import com.goodzheng.po.novel.service.BookChapterService;
import com.goodzheng.po.novel.service.BookCharacterService;
import com.goodzheng.po.novel.service.BookService;
import com.goodzheng.po.novel.service.CanonInternalService;
import com.goodzheng.po.novel.service.ChatTicketService;
import com.goodzheng.po.novel.service.StyleProfileService;
import com.goodzheng.po.shared.dto.Result;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.test.util.ReflectionTestUtils;

import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyLong;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

/**
 * §15.13-12 那个缺口的两条收口：握手票据（谁能建立 novel-chat 连接）与作者作用域
 * （这个连接能读谁的书）。
 *
 * <p>票据用<b>真的</b> {@link JwtUtil} 而不是替身：这一层的价值全在签名与 {@code typ} 声明
 * 的耦合上，mock 掉 JwtUtil 就只剩「方法被调用了一次」，测不到「用户 JWT 不能当票据用」
 * 「票据不能当会话令牌用」这两条真正的边界。
 *
 * <p>Service 层是 mock：这里验的是 Controller 的守门顺序（令牌 → 归属 → 取数），
 * 正典内容本身已在 {@code CanonAuthorityAndAdjudicationTest} 那侧验过。
 */
@ExtendWith(MockitoExtension.class)
class ChatTicketAndActorScopeTest {

    /** 与 .env.example / ci.yml 的开发占位密钥同值（Base64 解出来 43 字节，够 HS256 用） */
    private static final String DEV_SECRET =
            "cG8tbG9jYWwtZGV2LWp3dC1zZWNyZXQtY2hhbmdlLW1lLTAxMjM0NTY3ODlhYmNkZWY=";

    private static final String INTERNAL_TOKEN = "ci-internal-token";
    private static final Long OWNER = 1L;
    private static final Long FOREIGNER = 2L;
    private static final Long BOOK_ID = 7L;

    private final JwtUtil jwtUtil = new JwtUtil(DEV_SECRET, 86_400_000L);
    private final ChatTicketService ticketService = new ChatTicketService(jwtUtil);

    @Mock
    private CanonInternalService canonService;
    @Mock
    private BookService bookService;
    @Mock
    private BookChapterService chapterService;
    @Mock
    private BookCharacterService characterService;
    @Mock
    private AliasMapper aliasMapper;
    @Mock
    private StyleProfileService styleService;

    private NovelInternalController controller;

    @BeforeEach
    void setUp() {
        controller = new NovelInternalController(canonService, bookService, chapterService,
                characterService, aliasMapper, styleService, ticketService);
        // @Value 字段在单测里没有容器来填
        ReflectionTestUtils.setField(controller, "internalToken", INTERNAL_TOKEN);
    }

    // ── 票据本身 ──────────────────────────────────────────

    @Test
    void issuedTicketResolvesTheAuthorUid() {
        Long uid = ticketService.consume(ticketService.issue(OWNER));
        assertEquals(OWNER, uid);
        assertEquals(60, ticketService.expiresIn());
    }

    /** 用户 JWT 与 ASR 票据都签着同一把密钥，但 typ 不对就不是 chat 票据 */
    @Test
    void otherTypedTokensAreNotAcceptedAsChatTickets() {
        String userJwt = jwtUtil.generateToken(OWNER, "admin", "SUPER_ADMIN", "active", "admin-web");
        String asrTicket = jwtUtil.generateAsrTicket(OWNER, 9L, 60_000L);
        assertNull(ticketService.consume(userJwt));
        assertNull(ticketService.consume(asrTicket));
    }

    @Test
    void BlankTicketIsRejectedWithoutCallingTheParser() {
        assertNull(ticketService.consume(null));
        assertNull(ticketService.consume("   "));
    }

    /**
     * 票据不能反过来当会话令牌：它只带 uid，所以 {@code parse} 还原出的主体既没有角色
     * 也没有状态，{@code isActive()} 为假——授权规则因此不会把它认成登录用户。
     */
    @Test
    void chatTicketIsNotUsableAsSessionToken() {
        AuthUser user = jwtUtil.parse(ticketService.issue(OWNER));
        assertEquals(OWNER, user.id());
        assertFalse(user.isActive());
        assertNull(user.role());
        assertNull(user.client());
    }

    @Test
    void expiredTicketIsRejected() {
        assertNull(jwtUtil.parseChatTicket(jwtUtil.generateChatTicket(OWNER, -1_000L)));
    }

    // ── 校验端点 ──────────────────────────────────────────

    @Test
    void verifyRequiresTheInternalTokenFirst() {
        Result<InternalActorView> result = controller.verifyChatTicket(
                request(List.of()), body(ticketService.issue(OWNER)));
        assertEquals(403, result.getCode());
        assertFalse(result.getSuccess());
    }

    @Test
    void verifyRejectsGarbageTicket() {
        Result<InternalActorView> result = controller.verifyChatTicket(
                internalRequest(List.of()), body("not-a-jwt"));
        assertEquals(403, result.getCode());
    }

    @Test
    void verifyReturnsTheUidForAValidTicket() {
        Result<InternalActorView> result = controller.verifyChatTicket(
                internalRequest(List.of()), body(ticketService.issue(OWNER)));
        assertTrue(result.getSuccess());
        assertEquals(OWNER, result.getData().getUid());
    }

    @Test
    void verifyRejectsMissingBody() {
        assertEquals(403, controller.verifyChatTicket(internalRequest(List.of()), null).getCode());
    }

    // ── 作者作用域 ────────────────────────────────────────

    @Test
    void snapshotAllowsTheOwner() {
        when(bookService.getById(BOOK_ID)).thenReturn(book(OWNER));
        when(canonService.snapshot(any(), any(), any(), any())).thenReturn(List.of(new CanonEntry()));

        Result<List<CanonEntry>> result = controller.snapshot(
                internalRequest(List.of("X-Actor-Uid", String.valueOf(OWNER))),
                BOOK_ID, 12, null, null);

        assertTrue(result.getSuccess());
        assertEquals(1, result.getData().size());
    }

    @Test
    void snapshotRejectsAForeignActorBeforeReadingCanon() {
        when(bookService.getById(BOOK_ID)).thenReturn(book(OWNER));

        Result<List<CanonEntry>> result = controller.snapshot(
                internalRequest(List.of("X-Actor-Uid", String.valueOf(FOREIGNER))),
                BOOK_ID, 12, null, null);

        assertEquals(403, result.getCode());
        verify(canonService, never()).snapshot(any(), any(), any(), any());
    }

    /** 生成链路那一类读没有终端用户在场：不带该头时行为与修缺口之前完全一致 */
    @Test
    void snapshotWithoutActorHeaderStaysPermissive() {
        when(canonService.snapshot(any(), any(), any(), any())).thenReturn(List.of());

        assertTrue(controller.snapshot(internalRequest(List.of()), BOOK_ID, 12, null, null)
                .getSuccess());
    }

    @Test
    void snapshotRejectsMalformedActorHeader() {
        Result<List<CanonEntry>> result = controller.snapshot(
                internalRequest(List.of("X-Actor-Uid", "1;2")), BOOK_ID, 12, null, null);
        assertEquals(400, result.getCode());
        verify(canonService, never()).snapshot(any(), any(), any(), any());
    }

    /** 书读不回（不存在/已删）与「不是你的书」同一个回：都不该把内容吐出去 */
    @Test
    void snapshotRejectsWhenTheBookCannotBeRead() {
        when(bookService.getById(BOOK_ID)).thenThrow(new IllegalStateException("书籍不存在"));

        Result<List<CanonEntry>> result = controller.snapshot(
                internalRequest(List.of("X-Actor-Uid", String.valueOf(FOREIGNER))),
                BOOK_ID, 12, null, null);

        assertEquals(403, result.getCode());
    }

    @Test
    void bookDetailRejectsForeignActorWithoutCountingChapters() {
        when(bookService.getById(BOOK_ID)).thenReturn(book(OWNER));

        Result<InternalBookView> result = controller.bookDetail(
                internalRequest(List.of("X-Actor-Uid", String.valueOf(FOREIGNER))), BOOK_ID, null);

        assertEquals(403, result.getCode());
        verify(chapterService, never()).countWrittenByBook(anyLong());
    }

    /**
     * 读回的章数必须是「有正文的章数」：它是续写链路的游标，而作者可以留一行空章节排期。
     * 空行进游标 = 续写跳过它往后写，那一章永久空着、衔接尾段读成空串。
     */
    @Test
    void bookDetailCarriesTheWrittenCountNotTheRowCount() {
        when(bookService.getById(BOOK_ID)).thenReturn(book(OWNER));
        when(chapterService.countWrittenByBook(BOOK_ID)).thenReturn(3);

        Result<InternalBookView> result = controller.bookDetail(
                internalRequest(List.of("X-Actor-Uid", String.valueOf(OWNER))), BOOK_ID, null);

        assertEquals(3, result.getData().getChapterCount().intValue());
        verify(chapterService, never()).countByBook(anyLong());
    }

    @Test
    void aliasesAndStyleAndSummariesAreAllScoped() {
        when(bookService.getById(BOOK_ID)).thenReturn(book(OWNER));

        assertEquals(403, controller.aliases(
                internalRequest(List.of("X-Actor-Uid", String.valueOf(FOREIGNER))), BOOK_ID).getCode());
        assertEquals(403, controller.style(
                internalRequest(List.of("X-Actor-Uid", String.valueOf(FOREIGNER))), BOOK_ID).getCode());
        assertEquals(403, controller.summaries(
                internalRequest(List.of("X-Actor-Uid", String.valueOf(FOREIGNER))),
                BOOK_ID, 12, null, null).getCode());
        assertEquals(403, controller.openForeshadows(
                internalRequest(List.of("X-Actor-Uid", String.valueOf(FOREIGNER))),
                BOOK_ID, 12).getCode());
        verify(canonService, never()).summaries(any(), any(), any(), any());
        verify(canonService, never()).openForeshadows(any(), any());
    }

    /** 写通道不受作者作用域影响：生成链路写的就是它自己刚建的书，不带该头 */
    @Test
    void writeChannelDoesNotCheckTheActor() {
        ChapterRequest body = new ChapterRequest();
        controller.putChapter(
                internalRequest(List.of("X-Actor-Uid", String.valueOf(FOREIGNER))),
                BOOK_ID, body);
        // 断言的方式是「不查库」：写口没有 denyUnlessActorOwns，所以 bookService 一次都不该被调
        verify(bookService, never()).getById(any());
        // 身份只作为 revision 的记账人传下去，不参与授权判定
        verify(chapterService).putByIndex(BOOK_ID, body, FOREIGNER);
    }

    // ── 夹具 ──────────────────────────────────────────────

    private static Book book(Long authorId) {
        Book book = new Book();
        book.setId(BOOK_ID);
        book.setAuthorId(authorId);
        book.setTitle("长夜灯火");
        return book;
    }

    private static InternalChatTicketRequest body(String ticket) {
        InternalChatTicketRequest request = new InternalChatTicketRequest();
        request.setTicket(ticket);
        return request;
    }

    /** 带内网令牌的请求；参数是成对的 header 名与值 */
    private static MockHttpServletRequest internalRequest(List<String> extraHeaders) {
        MockHttpServletRequest request = request(extraHeaders);
        request.addHeader("X-Internal-Token", INTERNAL_TOKEN);
        return request;
    }

    private static MockHttpServletRequest request(List<String> extraHeaders) {
        MockHttpServletRequest request = new MockHttpServletRequest();
        for (int i = 0; i + 1 < extraHeaders.size(); i += 2) {
            request.addHeader(extraHeaders.get(i), extraHeaders.get(i + 1));
        }
        return request;
    }
}
