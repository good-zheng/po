export type GenreOption = {
  value: string;
  label: string;
};

export type Book = {
  id: number;
  authorId: number;
  title: string;
  description?: string | null;
  coverImage?: string | null;
  genre?: string | null;
  status: string;
  wordCount: number;
  author?: string | null;
  /** Tier-0 常驻注入的世界观摘要 + 主线进度，不是对外简介文案（那是 description） */
  summary?: string | null;
  createdAt?: string;
  updatedAt?: string;
};

export type BookRequest = {
  title: string;
  description?: string;
  coverImage?: string;
  genre?: string;
  author?: string;
  status?: string;
  /** Tier-0 常驻注入的世界观摘要；省略时服务端保留原值，不会清空 */
  summary?: string | null;
};

export type BookChapter = {
  id: number;
  bookId: number;
  chapterIndex: number;
  title: string;
  content?: string | null;
  wordCount: number;
  /** draft 草稿 / pending_review 待复核 / committed 已定稿 */
  status: string;
  /** 版本号只跟着正文走：改标题不加版，否则台账会对上从未存在过的内容 */
  revision: number;
  createdAt?: string;
  updatedAt?: string;
};

export type ChapterRequest = {
  /** 可留空：服务端统一落成「第 N 章」，落库的 title 永不为空 */
  title?: string;
  content?: string;
  chapterIndex?: number;
};

export type BookCharacter = {
  id: number;
  bookId: number;
  name: string;
  description?: string | null;
  avatar?: string | null;
  createdAt?: string;
  updatedAt?: string;
};

export type CharacterRequest = {
  name: string;
  description?: string;
  avatar?: string;
};

export type BookListParams = {
  current?: number;
  pageSize?: number;
  keyword?: string;
  genre?: string;
  status?: string;
};

// ── 正典层（L0，NOVEL_AGENT_PRD §5） ──────────────────────────────────────────

/** world_rule/character/relation/location/item/theme/style */
export type CanonKind =
  | 'world_rule'
  | 'character'
  | 'relation'
  | 'location'
  | 'item'
  | 'theme'
  | 'style';

/** confirmed/disputed/todo(缺口)/rejected */
export type CanonStatus = 'confirmed' | 'disputed' | 'todo' | 'rejected';

/** author 作者裁定 / text 原文抽取 / model 模型自证；优先级不可逆 */
export type CanonAuthority = 'author' | 'text' | 'model';

export type CanonEntry = {
  id: number;
  bookId: number;
  kind: string;
  /** 别名归一后的实体键，如 char:shenqing */
  subjectKey: string;
  predicate: string;
  objectText: string;
  restatement?: string | null;
  authority: string;
  /** BigDecimal 序列化成 JSON 数字（author 恒 1.00） */
  confidence: number;
  establishedChapter?: number | null;
  validFromChapter: number;
  /** null 表示至今有效 */
  validUntilChapter?: number | null;
  supersedesId?: number | null;
  status: string;
  sourceChapterId?: number | null;
  sourceStart?: number | null;
  sourceEnd?: number | null;
  evidenceQuote?: string | null;
  promptVersion?: string | null;
  model?: string | null;
  decidedBy?: number | null;
  decidedAt?: string | null;
  createdAt?: string;
  updatedAt?: string;
};

/**
 * 正典手改入参。
 *
 * 这里刻意没有 authority 字段：权威级由服务端判定，前端连「想传」的入口都不该有（§10.5-②）。
 */
export type CanonRequest = {
  kind?: string;
  subjectKey?: string;
  predicate?: string;
  objectText?: string;
  restatement?: string;
  establishedChapter?: number;
  validFromChapter?: number;
  validUntilChapter?: number;
  status?: string;
};

export type CanonRetireRequest = {
  /** 最后一个仍然成立的章号；留空由服务端取当前最大章号 */
  untilChapter?: number;
  reason?: string;
};

export type AliasItem = {
  id: number;
  bookId: number;
  entityKey: string;
  aliasText: string;
  firstSeenChapter?: number | null;
  isPrimary: boolean;
};

export type AliasRequest = {
  entityKey?: string;
  isPrimary?: boolean;
};

export type ForeshadowItem = {
  id: number;
  bookId: number;
  plantedChapter: number;
  content: string;
  dueByArc?: number | null;
  payoffChapter?: number | null;
  /** opened/paid/abandoned */
  status: string;
  createdAt?: string;
};

export type ForeshadowRequest = {
  content?: string;
  plantedChapter?: number;
  dueByArc?: number;
  payoffChapter?: number;
  status?: string;
};

/** blocker/major/minor */
export type FindingSeverity = 'blocker' | 'major' | 'minor';

/** open/adopted/rejected/waived/orphaned */
export type FindingStatus =
  | 'open'
  | 'adopted'
  | 'rejected'
  | 'waived'
  | 'orphaned';

export type Finding = {
  id: number;
  bookId: number;
  chapterId: number;
  revision: number;
  /** 冲突编码，取值见 Python 侧 schemas.FindingCode（attribute_conflict / death_speaks …） */
  code: string;
  severity: string;
  /** rule 规则引擎 / judge 语义裁判 */
  checker: string;
  /** 被违反的 canon 编号列表，JSON 数组文本 */
  canonRefs?: string | null;
  textStart?: number | null;
  textEnd?: number | null;
  evidenceQuote?: string | null;
  explanation?: string | null;
  fixInstruction?: string | null;
  status: string;
  decidedBy?: number | null;
  decidedAt?: string | null;
  basis?: string | null;
  createdAt?: string;
  chapterIndex?: number | null;
  chapterTitle?: string | null;
  chapterWords?: number | null;
  chapterStatus?: string | null;
};

export type FindingAdjudicationRequest = {
  action: 'adopt' | 'reject' | 'waive' | 'rewrite';
  /** reject/waive 必填 */
  basis?: string;
  /** adopt 必填：作者认定的事实 */
  assertion?: CanonRequest;
  /** adopt 时要闭区间的老断言，缺省取该 Finding 的 canonRefs */
  closeAssertionIds?: number[];
};

export type FindingAdjudicationResult = {
  findingId: number;
  status: string;
  assertionId?: number | null;
  closedAssertionIds: number[];
  chapterBackToDraft: boolean;
  fixInstruction?: string | null;
};

export type NovelProgress = {
  bookId: number;
  chapterCount: number;
  wordCount: number;
  chaptersByStatus: Record<string, number>;
  canonByStatus: Record<string, number>;
  canonByAuthority: Record<string, number>;
  findingsByStatus: Record<string, number>;
  openFindingsBySeverity: Record<string, number>;
  openForeshadows: number;
  jobsByStage: Record<string, number>;
};

// ── 章节版本与改稿影响（§10.5-③） ────────────────────────────────────────────────

export type ChapterRevision = {
  chapterId: number;
  revision: number;
  content?: string | null;
  /** 正文的 sha256，与 Python 侧 gen_job 幂等键同算法 */
  contentHash?: string | null;
  /** 手改的作者 ID，Agent 写库为 null；当前版本无此痕迹 */
  createdBy?: number | null;
  createdAt?: string | null;
  /** true 表示这条就是 book_chapter.content，不是历史 */
  current: boolean;
};

/** 仍会读到「出处在本章」的后续章 */
export type AffectedChapter = {
  chapterId: number;
  chapterIndex: number;
  title?: string | null;
  status: string;
  canonIds: number[];
  /** 命中的前几条断言主-谓，给作者的一句话提示 */
  brief?: string | null;
};

/** 出处引文已不在当前正文里的断言 */
export type OrphanedAssertion = {
  canonId: number;
  subjectKey: string;
  predicate: string;
  objectText: string;
  evidenceQuote?: string | null;
  /** 台账里那条未裁定的 source_orphaned，可从清单直接跳到裁定 */
  findingId?: number | null;
};

export type ChapterImpact = {
  chapterId: number;
  chapterIndex?: number | null;
  revision: number;
  status: string;
  affectedChapters: AffectedChapter[];
  orphanedAssertions: OrphanedAssertion[];
  orphanedFindings: number;
};

// ── 统一检索：左栏（§10.3） ────────────────────────────────────────────────────

/** 检索范围；缺省三样都查 */
export type SearchScope = 'chapter' | 'canon' | 'alias';

export type SearchChapterHit = {
  chapterId: number;
  chapterIndex?: number | null;
  title?: string | null;
  status: string;
  revision?: number | null;
  /** 命中处前后各截一段；正文没命中而标题命中时给正文起头 */
  excerpt?: string | null;
};

export type SearchCanonHit = {
  canonId: number;
  kind: string;
  subjectKey: string;
  predicate: string;
  objectText: string;
  authority: string;
  status: string;
  validFromChapter?: number | null;
  validUntilChapter?: number | null;
  /** true 表示只因「这个称谓属于该实体」才被搜出来，文本本身不含查询词 */
  matchedViaAlias: boolean;
};

export type SearchAliasHit = {
  aliasId: number;
  entityKey: string;
  aliasText: string;
  firstSeenChapter?: number | null;
  isPrimary?: boolean | null;
};

/**
 * 一期只有 MySQL LIKE，跨三张表没有可比打分，所以按 scope 分节返回而不是混排成一条全局序。
 *
 * 分页参数对每一节分别生效，各节自带 total。空词不查（`LIKE '%%'` 等于拖库）。
 */
export type SearchResults = {
  bookId: number;
  query: string;
  scopes: SearchScope[];
  /** 查询词命中的称谓展开成的实体键；为空说明别名展开没起作用，别把它当「搜全了」 */
  expandedEntityKeys: string[];
  chapters: SearchChapterHit[];
  canon: SearchCanonHit[];
  aliases: SearchAliasHit[];
  chapterTotal: number;
  canonTotal: number;
  aliasTotal: number;
};

// ── 提议卡：右栏只谈不写，设定结论走卡片（§10.3、D8） ─────────────────────────

/** pending/adopted/dismissed */
export type ProposalStatus = 'pending' | 'adopted' | 'dismissed';

/**
 * 一张未被采纳的设定提议。
 *
 * 这张表不在注入路径上：模型与编译器都读不到它，只有 adopt 端点会把它变成
 * `canon_entry(authority=author)`。「未采纳的设定永不参与注入」是靠这条链路保证的，
 * 不是靠调用方自觉。
 */
export type CanonProposal = {
  id: number;
  bookId: number;
  /** 哪一次对话会话产出的卡，仅作回溯 */
  sessionId?: string | null;
  /** 出卡时的参照章；采纳时按它判「作者点头时看得见哪些断言」 */
  asOfChapter?: number | null;
  kind: string;
  subjectKey: string;
  predicate: string;
  objectText: string;
  validFromChapter?: number | null;
  /** 依据：对话里引用的那一句原话 */
  basisQuote?: string | null;
  status: string;
  /** 采纳后立的那条 author 级断言 */
  adoptedEntryId?: number | null;
  decidedBy?: number | null;
  decidedAt?: string | null;
  /** 驳回依据：卡片内容留下了，为什么不要它必须也留下 */
  decidedBasis?: string | null;
  createdAt?: string;
};

/**
 * 提议卡入参。
 *
 * 与 Java 侧 `ProposalRequest` 一样刻意没有 status/authority：一张新卡的初始状态只能由
 * 服务端写死为 pending，调用方若能自报 adopted，「未采纳不得注入」就从接口层漏了。
 */
export type ProposalRequest = {
  bookId: number;
  sessionId?: string;
  asOfChapter?: number;
  kind?: string;
  subjectKey?: string;
  predicate?: string;
  objectText?: string;
  /** 从第几章起成立；留空由服务端取参照章，再退回当前最大章号 */
  validFromChapter?: number;
  basisQuote?: string;
};

export type ProposalDecisionRequest = {
  /** adopt 用：撞车时要显式指定覆盖哪几条，缺省一条都不闭 */
  closeAssertionIds?: number[];
  /** adopt 用：给断言的一句自然语言复述，留空由服务端取 objectText */
  restatement?: string;
  /** dismiss 必填 */
  basis?: string;
};

export type ProposalDecision = {
  proposalId: number;
  status: string;
  /** adopt 后新立的 author 级断言 id */
  entryId?: number | null;
  /** 本次被闭掉有效区间的旧断言 */
  closedAssertionIds: number[];
  /** 撞车的既有断言 id；二次确认读的就是它 */
  conflictIds: number[];
};

// ── 文风契约（§5.5） ───────────────────────────────────────────────────────────

/**
 * 三个词表在这里是字符串数组而不是库里的 JSON 文本：注入侧与闸门侧要的都是数组。
 */
export type StyleProfile = {
  id?: number | null;
  bookId: number;
  /** 第几人称，如「第三人称限知」 */
  person?: string | null;
  tense?: string | null;
  sentenceLenMin?: number | null;
  sentenceLenMax?: number | null;
  chapterWordsMin?: number | null;
  chapterWordsMax?: number | null;
  forbiddenWords: string[];
  tics: string[];
  taboo: string[];
};

/** 字段全部可选：「没填」保留原值，「填了空数组」才是清空 */
export type StyleProfileRequest = {
  person?: string;
  tense?: string;
  sentenceLenMin?: number;
  sentenceLenMax?: number;
  chapterWordsMin?: number;
  chapterWordsMax?: number;
  forbiddenWords?: string[];
  tics?: string[];
  taboo?: string[];
};
