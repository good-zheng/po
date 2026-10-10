import { request } from '@umijs/max';
import type {
  AffectedChapter,
  AliasItem,
  AliasRequest,
  Book,
  BookChapter,
  BookCharacter,
  BookRequest,
  CanonEntry,
  CanonProposal,
  CanonRequest,
  CanonRetireRequest,
  ChapterImpact,
  ChapterRequest,
  ChapterRevision,
  CharacterRequest,
  ChatTicket,
  Finding,
  FindingAdjudicationRequest,
  FindingAdjudicationResult,
  ForeshadowItem,
  ForeshadowRequest,
  GenreOption,
  NovelProgress,
  OrphanedAssertion,
  PageResponse,
  ProposalDecision,
  ProposalDecisionRequest,
  ProposalRequest,
  Result,
  SearchResults,
  SearchScope,
  StyleProfile,
  StyleProfileRequest,
} from '@po/types';

export type {
  AffectedChapter,
  AliasItem,
  AliasRequest,
  Book,
  BookChapter,
  BookCharacter,
  BookListParams,
  BookRequest,
  CanonEntry,
  CanonKind,
  CanonProposal,
  CanonRequest,
  CanonRetireRequest,
  ChapterImpact,
  ChapterRequest,
  ChapterRevision,
  CharacterRequest,
  Finding,
  FindingAdjudicationRequest,
  FindingAdjudicationResult,
  ForeshadowItem,
  ForeshadowRequest,
  GenreOption,
  NovelProgress,
  OrphanedAssertion,
  ProposalDecision,
  ProposalRequest,
  ProposalStatus,
  SearchCanonHit,
  SearchResults,
  SearchScope,
  StyleProfile,
  StyleProfileRequest,
} from '@po/types';

// ── Genres ───────────────────────────────────────────────────────────────────

/** 获取小说类型字典 */
export async function getBookGenres(options?: Record<string, unknown>) {
  return request<Result<GenreOption[]>>('/api/books/genres', {
    method: 'GET',
    ...(options || {}),
  });
}

// ── Books ────────────────────────────────────────────────────────────────────

/** 分页获取书籍列表 */
export async function getBooks(
  params: {
    page?: number;
    size?: number;
    keyword?: string;
    genre?: string;
    status?: string;
  },
  options?: Record<string, unknown>,
) {
  return request<Result<PageResponse<Book>>>('/api/books', {
    method: 'GET',
    params,
    ...(options || {}),
  });
}

/** 获取单个书籍详情 */
export async function getBook(id: number, options?: Record<string, unknown>) {
  return request<Result<Book>>(`/api/books/${id}`, {
    method: 'GET',
    ...(options || {}),
  });
}

/** 创建书籍 */
export async function createBook(body: BookRequest, options?: Record<string, unknown>) {
  return request<Result<Book>>('/api/books', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    data: body,
    ...(options || {}),
  });
}

/** 更新书籍 */
export async function updateBook(
  id: number,
  body: BookRequest,
  options?: Record<string, unknown>,
) {
  return request<Result<Book>>(`/api/books/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    data: body,
    ...(options || {}),
  });
}

/** 删除书籍（软删除，级联删除章节与角色） */
export async function deleteBook(id: number, options?: Record<string, unknown>) {
  return request<Result<string>>(`/api/books/${id}`, {
    method: 'DELETE',
    ...(options || {}),
  });
}

// ── Chapters ─────────────────────────────────────────────────────────────────

/** 获取书籍章节列表 */
export async function getChapters(bookId: number, options?: Record<string, unknown>) {
  return request<Result<BookChapter[]>>(`/api/books/${bookId}/chapters`, {
    method: 'GET',
    ...(options || {}),
  });
}

/** 获取单个章节 */
export async function getChapter(
  bookId: number,
  chapterId: number,
  options?: Record<string, unknown>,
) {
  return request<Result<BookChapter>>(
    `/api/books/${bookId}/chapters/${chapterId}`,
    { method: 'GET', ...(options || {}) },
  );
}

/** 创建章节 */
export async function createChapter(
  bookId: number,
  body: ChapterRequest,
  options?: Record<string, unknown>,
) {
  return request<Result<BookChapter>>(`/api/books/${bookId}/chapters`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    data: body,
    ...(options || {}),
  });
}

/** 更新章节 */
export async function updateChapter(
  bookId: number,
  chapterId: number,
  body: ChapterRequest,
  options?: Record<string, unknown>,
) {
  return request<Result<BookChapter>>(
    `/api/books/${bookId}/chapters/${chapterId}`,
    {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      data: body,
      ...(options || {}),
    },
  );
}

/** 删除章节（软删除） */
export async function deleteChapter(
  bookId: number,
  chapterId: number,
  options?: Record<string, unknown>,
) {
  return request<Result<string>>(`/api/books/${bookId}/chapters/${chapterId}`, {
    method: 'DELETE',
    ...(options || {}),
  });
}

// ── Characters ───────────────────────────────────────────────────────────────

/** 获取书籍角色列表 */
export async function getCharacters(bookId: number, options?: Record<string, unknown>) {
  return request<Result<BookCharacter[]>>(`/api/books/${bookId}/characters`, {
    method: 'GET',
    ...(options || {}),
  });
}

/** 创建角色 */
export async function createCharacter(
  bookId: number,
  body: CharacterRequest,
  options?: Record<string, unknown>,
) {
  return request<Result<BookCharacter>>(`/api/books/${bookId}/characters`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    data: body,
    ...(options || {}),
  });
}

/** 更新角色 */
export async function updateCharacter(
  bookId: number,
  characterId: number,
  body: CharacterRequest,
  options?: Record<string, unknown>,
) {
  return request<Result<BookCharacter>>(
    `/api/books/${bookId}/characters/${characterId}`,
    {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      data: body,
      ...(options || {}),
    },
  );
}

/** 删除角色（软删除） */
export async function deleteCharacter(
  bookId: number,
  characterId: number,
  options?: Record<string, unknown>,
) {
  return request<Result<string>>(`/api/books/${bookId}/characters/${characterId}`, {
    method: 'DELETE',
    ...(options || {}),
  });
}

// ── 创作工作台：正典 / 别名 / 伏笔 / 台账 / 进度 ──────────────────────────────
// 这一组走 /api/novel/**：读写都要管理端 JWT（SecurityConfig 里 /novel/** → ADMIN_CLIENT）。
// 与上面 /api/books/** 的读者端公开面刻意分开——正典与台账不是给读者看的东西。

/** 分页取正典断言 */
export async function getCanon(
  bookId: number,
  params: {
    page?: number;
    size?: number;
    subjectKey?: string;
    kind?: string;
    status?: string;
    authority?: string;
    keyword?: string;
  },
  options?: Record<string, unknown>,
) {
  return request<Result<PageResponse<CanonEntry>>>(
    `/api/novel/books/${bookId}/canon`,
    { method: 'GET', params, ...(options || {}) },
  );
}

/** 写入前的确定性冲突预览：同主同谓且值不同的已生效断言 */
export async function getCanonConflicts(
  bookId: number,
  params: { subjectKey?: string; predicate?: string; objectText?: string; asOfChapter?: number },
  options?: Record<string, unknown>,
) {
  return request<Result<CanonEntry[]>>(
    `/api/novel/books/${bookId}/canon/conflicts`,
    { method: 'GET', params, ...(options || {}) },
  );
}

/** 新增作者级断言（authority 由服务端写死 author） */
export async function createCanon(
  bookId: number,
  body: CanonRequest,
  options?: Record<string, unknown>,
) {
  return request<Result<CanonEntry>>(`/api/novel/books/${bookId}/canon`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    data: body,
    ...(options || {}),
  });
}

/** 修改断言：手改即裁定，服务端把这一条升级为 author 级 */
export async function updateCanon(
  id: number,
  body: CanonRequest,
  options?: Record<string, unknown>,
) {
  return request<Result<CanonEntry>>(`/api/novel/canon/${id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    data: body,
    ...(options || {}),
  });
}

/** 停用断言：闭有效期而非物理删除，历史章节的 as-of 视图才不会失真 */
export async function retireCanon(
  id: number,
  body: CanonRetireRequest,
  options?: Record<string, unknown>,
) {
  return request<Result<CanonEntry>>(`/api/novel/canon/${id}/retire`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    data: body,
    ...(options || {}),
  });
}

/** 别名表 */
export async function getAliases(bookId: number, options?: Record<string, unknown>) {
  return request<Result<AliasItem[]>>(`/api/novel/books/${bookId}/aliases`, {
    method: 'GET',
    ...(options || {}),
  });
}

/** 改判称谓归属（C3 一人多名 / 多名同人的作者裁定） */
export async function updateAlias(
  bookId: number,
  aliasId: number,
  body: AliasRequest,
  options?: Record<string, unknown>,
) {
  return request<Result<AliasItem>>(
    `/api/novel/books/${bookId}/aliases/${aliasId}`,
    {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      data: body,
      ...(options || {}),
    },
  );
}

/** 伏笔台账 */
export async function getForeshadows(
  bookId: number,
  status?: string,
  options?: Record<string, unknown>,
) {
  return request<Result<ForeshadowItem[]>>(
    `/api/novel/books/${bookId}/foreshadows`,
    { method: 'GET', params: status ? { status } : {}, ...(options || {}) },
  );
}

export async function createForeshadow(
  bookId: number,
  body: ForeshadowRequest,
  options?: Record<string, unknown>,
) {
  return request<Result<ForeshadowItem>>(
    `/api/novel/books/${bookId}/foreshadows`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      data: body,
      ...(options || {}),
    },
  );
}

export async function updateForeshadow(
  bookId: number,
  foreshadowId: number,
  body: ForeshadowRequest,
  options?: Record<string, unknown>,
) {
  return request<Result<ForeshadowItem>>(
    `/api/novel/books/${bookId}/foreshadows/${foreshadowId}`,
    {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      data: body,
      ...(options || {}),
    },
  );
}

/** 冲突台账：bookId 省略即跨书 */
export async function getFindings(
  params: {
    bookId?: number;
    severity?: string;
    status?: string;
    checker?: string;
    code?: string;
    page?: number;
    size?: number;
  },
  options?: Record<string, unknown>,
) {
  return request<Result<PageResponse<Finding>>>('/api/novel/reviews', {
    method: 'GET',
    params,
    ...(options || {}),
  });
}

/** 裁定一条 Finding（adopt 是四步单事务，任一失败整体回滚） */
export async function adjudicateFinding(
  findingId: number,
  body: FindingAdjudicationRequest,
  options?: Record<string, unknown>,
) {
  return request<Result<FindingAdjudicationResult>>(
    `/api/novel/reviews/${findingId}`,
    {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      data: body,
      ...(options || {}),
    },
  );
}

/** 进度看板（只读） */
export async function getNovelProgress(
  bookId: number,
  options?: Record<string, unknown>,
) {
  return request<Result<NovelProgress>>('/api/novel/progress', {
    method: 'GET',
    params: { bookId },
    ...(options || {}),
  });
}

// ── 章节版本与改稿影响（§10.5-③） ─────────────────────────────────────────────

/**
 * 本章的正文版本历史，当前版本在第一位（中栏 diff 取两条即可）。
 *
 * <p>读的是 /novel 面而不是读者面的 /books：历史正文里可能含未定稿的伏笔与被改掉的事实。
 */
export async function getChapterRevisions(
  bookId: number,
  chapterId: number,
  options?: Record<string, unknown>,
) {
  return request<Result<ChapterRevision[]>>(
    `/api/novel/books/${bookId}/chapters/${chapterId}/revisions`,
    {
      method: 'GET',
      ...(options || {}),
    },
  );
}

/** 改这一章会波及谁：受影响的后章清单 + 出处已失效的断言。保存前看风险，保存后看新失效的 */
export async function getChapterImpact(
  bookId: number,
  chapterId: number,
  options?: Record<string, unknown>,
) {
  return request<Result<ChapterImpact>>(
    `/api/novel/books/${bookId}/chapters/${chapterId}/impact`,
    {
      method: 'GET',
      ...(options || {}),
    },
  );
}

// ── 统一检索：左栏（§10.3） ───────────────────────────────────────────────────

/**
 * 章题、正文、正典断言、别名一起搜。
 *
 * 结果按 scope 分节返回、分页对每节分别生效，所以 UI 不该把它们拼成一个「相关度」列表——
 * 一期是 MySQL LIKE，跨表没有可比打分。空 q 服务端直接返回空节（不查库），调用方不必自己拦。
 */
export async function searchNovel(
  bookId: number,
  params: {
    q?: string;
    scope?: SearchScope | SearchScope[];
    page?: number;
    size?: number;
  },
  options?: Record<string, unknown>,
) {
  const { scope, ...rest } = params;
  return request<Result<SearchResults>>(`/api/novel/books/${bookId}/search`, {
    method: 'GET',
    // 逗号分隔而不是重复键：服务端两种都收，走 query string 时逗号形式不会被请求库序列化差异影响
    params: { ...rest, scope: Array.isArray(scope) ? scope.join(',') : scope },
    ...(options || {}),
  });
}

// ── 提议卡：右栏只谈不写（D8） ────────────────────────────────────────────────

/** 提议卡列表；bookId 省略即跨书，面板默认按 status=pending 过滤 */
export async function getProposals(
  params: {
    bookId?: number;
    status?: string;
    page?: number;
    size?: number;
  },
  options?: Record<string, unknown>,
) {
  return request<Result<PageResponse<CanonProposal>>>('/api/novel/proposals', {
    method: 'GET',
    params,
    ...(options || {}),
  });
}

/**
 * 把对话里的一张设定提议存入台账。
 *
 * 由工作台前端代作者提交：初始状态恒为 pending，入参类型里也没有 status/authority（§10.3 约定 3）。
 */
export async function createProposal(
  body: ProposalRequest,
  options?: Record<string, unknown>,
) {
  return request<Result<CanonProposal>>('/api/novel/proposals', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    data: body,
    ...(options || {}),
  });
}

/**
 * 采纳 → canon_entry(authority=author)。
 *
 * 撞车时服务端会拒绝且一条不落库，必须带 closeAssertionIds 显式点名覆盖哪几条；
 * 拒绝的 message 里带着 conflictIds，所以 UI 第一次点也应该先把预览摆出来。
 */
export async function adoptProposal(
  proposalId: number,
  body?: ProposalDecisionRequest,
  options?: Record<string, unknown>,
) {
  return request<Result<ProposalDecision>>(
    `/api/novel/proposals/${proposalId}/adopt`,
    {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      data: body ?? {},
      ...(options || {}),
    },
  );
}

/** 驳回：basis 必填，卡片内容留下了而「为什么不要它」没留，下一轮对话只能重新猜 */
export async function dismissProposal(
  proposalId: number,
  body: ProposalDecisionRequest,
  options?: Record<string, unknown>,
) {
  return request<Result<ProposalDecision>>(
    `/api/novel/proposals/${proposalId}/dismiss`,
    {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      data: body,
      ...(options || {}),
    },
  );
}

// ── 文风契约（§5.5） ──────────────────────────────────────────────────────────

/** 没定过契约的书返回 data=null，那是「还没有契约」，不是空契约 */
export async function getStyleProfile(
  bookId: number,
  options?: Record<string, unknown>,
) {
  return request<Result<StyleProfile | null>>(
    `/api/novel/books/${bookId}/style`,
    { method: 'GET', ...(options || {}) },
  );
}

/**
 * 整份提交：未提供的字段服务端保留原值，传空数组才是清空该项。
 *
 * 同一条 PUT 也是闸门侧读的那份契约（L1 编译器经 /internal/canon/style 读回），
 * 所以作者在这里收紧的禁用词，下一轮生成就会被规则闸门按同一份列表拦。
 */
export async function updateStyleProfile(
  bookId: number,
  body: StyleProfileRequest,
  options?: Record<string, unknown>,
) {
  return request<Result<StyleProfile>>(`/api/novel/books/${bookId}/style`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    data: body,
    ...(options || {}),
  });
}

// ── 对话握手票据（§15.13-12） ─────────────────────────────────────────────────

/**
 * 换一张一次性票据，拼进 `/ws/chat?ticket=` 用于握手鉴权。
 *
 * 不能把会话 JWT 直接拼在 WS URL 上：浏览器与小程序都握不了 WebSocket 的请求头，而 query
 * 会被网关访问日志原样留存——把 24 小时有效的令牌写进日志等于把长期凭据交给日志系统。
 * 服务端每次校验即失效，因此**每次（重）连接都要重新取一张**，不要把返回值缓存复用。
 */
export async function getChatTicket(options?: Record<string, unknown>) {
  return request<Result<ChatTicket>>('/api/novel/chat-ticket', {
    method: 'GET',
    ...(options || {}),
  });
}
