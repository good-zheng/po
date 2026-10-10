# po-agent-novel

小说创作垂直 Agent：经 `po-agent-core` 插槽接入 supervisor，一句话想法 → 完整书稿归档。

## 链路

```
conceive（构思：标题/摘要/类型）
  → worldbuild（书级圣经：世界规则/人物/关系/缺口 → 转成种子正典，只攒不写）
  → outline（大纲：章标题+章梗概+弧名）
  → plan_scene（场景卡：本章实体/待补新实体/场景与在场名单/要收的伏笔/字数带）
  → gate_plan（计划闸门：规则 + 计划裁判 → pass/replan/escalate）
       ├─ replan ─────────→ 回 plan_scene（退回意见逐字进提示词，最多 2 轮）
       ├─ escalate ───────→ 本节点内 interrupt：作者按 yes 继续（本章记进 plan_unreviewed）
       │                    其他回复 → 定 halted_at 停笔，直接进 archive
       └─ pass → write（L1 按卡上 entities 收窄 → 初稿）
                   → extract（抽本章候选正典 + 场景/章级摘要，只攒不写）
                   → gate_text（正文闸门：规则引擎 + 语义裁判 → pass/patch/rewrite/freeze）
                        ├─ 有可定位的 blocker → revise（定向修补 / 整章重写）→ 回 extract 重抽 → 回 gate 重检
                        └─ 放行或冻结 → commit_and_next（定稿 + 推进游标，零 LLM）
                             ├─ 还有下一章 → 回 plan_scene
                             └─ 全书写完 → archive
  → archive（interrupt 人工确认 → yes：抽角色 → 成稿入库 → 圣经种子 append（as_of=1）
            → 逐章【冲突台账 → 正典 → 层级摘要】→ 按弧合成弧级摘要）
```

四条回环互不缠绕：计划回环（`plan_scene ⇄ gate_plan`）判「这张卡能不能照着写」，
正文回环（`gate_text ⇄ revise`）判「闸门点出的那一处改掉没有」，
章节推进（`commit_and_next → plan_scene`）判「全书写完没有」，
人工口只有两处（`gate_plan` 的 escalate、`archive` 的归档确认）。
**extract 只跑在闸门之前、定稿之后**：未定稿的稿子必然还要被改写，
从它身上抽出的事实会污染正典，而闸门又要拿抽取产物做判定。
摘要与抽取同理，且不新增节点（见「层级摘要树」）。
`gate_text` 排在 extract 之后、走向判定之前；修补回环回到 extract 而非直连 gate，
是为了让新正文重抽一遍候选——逐字证据是旧正文的坐标，留着它闸门会拿旧偏移去检新稿
（见「放行策略」）。

计划闸门排在正文之前是整条链路最便宜的一道保险：死者出现在在场名单里，
正文要烧一千二百字才发现，而在卡上只需改一行 `present`。

- 领域状态全部放在 `CoreState.artifacts["novel"]` 命名空间，supervisor 不解释；
- 子图不挂 checkpointer，由父图统一供给（interrupt 依赖父图线程 checkpoint）；
- 领域进度经 `get_stream_writer` 发布 THINKING/PLAN 事件，AgentRunner 以
  `subgraphs=True` 透传到 WS/A2A 等传输层；
- **所有写库都排在最后一个 interrupt 之后**：resume 会让 `archive` 节点从头重放，
  写侧不幂等就会把正典写成双份（幂等兜底见「正典闸门」）。
  `commit_and_next` 因此刻意做成纯状态搬运——放行到下一章之间没有任何副作用，
  重放它只是把游标再推一次。

## L1 记忆装配（`context.compile_context`）

每章**两次**装配，同一套预算与过滤，只是收窄范围不同：

| 时机 | stage 事件 | `entities` | 为什么 |
| --- | --- | --- | --- |
| `plan_scene` 之前 | `plan_compiled` | `None`（全量 as-of 快照） | 计划闸门要「看得见全量事实」才判得出未登记实体与死人在场 |
| `write` 之前 | `context_compiled` | 场景卡的 `entities`；卡上没填则退回全量 | 正文只需要本章相关的那部分，收窄是为了压预算 |

两次共用一份预算表（PRD §6），与书长无关：

| 层 | 内容 | 默认预算 |
| --- | --- | --- |
| Tier-0 常驻 | 世界观与主线 + 文风契约 + 最新一段弧摘要（进度线） | ~800 |
| Tier-1 检索 | 本章实体截至 as-of 的断言 + 未收伏笔 | ~1500 |
| Tier-2 近因 | 前 3 章场景摘要（缺场景摘要的章退用章级）+ 上一章末尾 300 字原文 | ~1000 |
| 任务区 | 本章大纲与写作要求 | ~700 |

四条不可让的性质，各有对应测试锁住（`test_context.py`）：

- **as-of = 正在写章的 0 基下标**：回溯重写第 12 章时读不到第 30 章的事实。
  断言按区间**相交**过滤（那条事实在第 N 章仍成立就该看见），摘要按**整段已知**
  过滤——摘要是有损总结，区间相交就意味着它写了 as-of 之后的剧情，注入即剧透；
- **注入即编号**：`[canon#N]` / `[fsh#N]` 共用一条序列，`CompiledContext.refs` 留着
  回指来源（`source_id` 带 `pending:` 前缀者表示还没入库），两道闸门与后续引用都靠它；
- **超预算从尾部裁剪**，且上一章末尾原文最后才动（续写的衔接比一条设定更贵）。
  `counts["dropped"]` 与 `tokens` 随两个 `*_compiled` 事件上浮，N6 的成本门禁读它——
  注意每章现在是两次装配，统计口径要按 stage 分开。
- **文风契约只有一个来源**：`compile_context` 先取装配侧的派生契约（题材 + 圣经的
  人称/时态），再让 `CanonStore.load_style_profile` 读回的**作者手改契约**逐项盖上去
  （`None` 字段 = 作者没表态，保留派生值；空数组 = 明确清空）。盖完的那份存在
  `CompiledContext.style` 里，注入块、两道闸门的词表与字数带、计划提示词的 `pov` 全部
  读它。契约读只在 `book_id` 已归档后发生，所以新书第一轮用的是派生值。
- **对话与生成共用这一台编译器**（§10.3-②「同一份上下文」）：右栏把任意章设为「当前
  参照章」，`NovelStore.load_book` 只读回书目元数据 + 点名那一章的正文（整本正文不过网，
  一次对话的开销才不随书长增长），再由 `compile_context(task_chapter=…)` 用它改写任务区
  与近因尾段两处。as-of 仍是同一个支点：参照章号晚于 as-of 时直接 `ValueError`，
  不做过滤——晚于它的正文只能算后文。生成链路永不传 `task_chapter`。

`world_rows`（圣经行）只有 `status == "confirmed"` 才进快照，所以离线/降级的那本
「全是缺口」的圣经不会把任何编造规则喂给后续章节，也因此离线链路里计划闸门的
登记表是空的（见「计划闸门」的 `no_registry`）。

归档前 `book_id` 是空串，此时**一次库读都不发生**：本轮已定稿章的事实走 `overlay`
（候选断言）与 `digests`（层级摘要）两条内存通道补齐。它们与库读走**同一套**过滤
条件，否则「本轮视图」会比库内视图更宽松，后文事实就绕过 as-of 从这条缝漏进上下文。

`approx_tokens` 是近似计数（CJK 一字计 1、其余 `ceil(len/4)`），不是分词器结果：
tiktoken 的词表是运行时从外网拉的。所以预算与 P95 都要按同一口径比较，换计数器必须重跑基线。

## 层级摘要树（scene → chapter → arc）

摘要只往下读一层，绝不套娃（§6-4）：场景摘要吃正文、章级吃场景、弧级只吃章级。

| 层级 | 产出时机 | 落库键 |
| --- | --- | --- |
| `scene` | extract 节点内，随本章定稿 | `(chapter_id, level, scene_no)`，序号从 1 起 |
| `chapter` | 同上 | 同键，**`scene_no` 恒 0**（NULL 与 NULL 在 MySQL 唯一索引里不算重复，写 NULL 等于把约束从库层让给代码层） |
| `arc` | archive 入库后，按 `_arc_spans` 切分 | `(book_id, level='arc', scene_no=弧号)`，同弧号重写按覆盖处理 |

弧的切分优先认**大纲点名的弧名**（`ChapterOutline.arc`）：连续同名即一段弧，
作者换了弧名就是换了一段剧情，这时不再受 `arc_chapters`（默认 10）跨度约束——
把明确的分组硬切成两半，Tier-0 的进度线会告诉他「弧在中间断了」，那是假信息。
弧名为空的章视作延续当前弧（模型常常只在弧的第一章写名字）；整本都没点名才退回
按 `arc_chapters` 等分。`save_arc_summary` 没有承载弧名的列，所以标题只影响切分、
不落库。

摘要入库失败**不进** `canon_failed` 待重驱清单：它缺的是近因质量，不是事实一致性，
重驱正典时不该把已经写好的断言再推一遍。弧级同理，单段失败只记日志并继续下一段。
`arc_chapters<=0` 即关闭弧级（Tier-0 宁可不显示进度线，也不拿半截弧充数）。

## 分阶段模型

节点按用途声明模型角色（`graph.NODE_MODEL_ROLES`，改这张表即改阶段归属）：

| 阶段 | 角色 | 可选覆盖 |
| --- | --- | --- |
| conceive / worldbuild / outline / plan_scene | `plan` | `AGENT_CORE_LLM_ROLES__PLAN__MODEL` |
| write（初稿） | `write` | `AGENT_CORE_LLM_ROLES__WRITE__MODEL`、`__WRITE__TEMPERATURE` |
| revise（定向修补 / 整章重写） | `write` | 同 `write` 槽位 |
| gate_plan（计划裁判） | `judge` | `AGENT_CORE_LLM_ROLES__JUDGE__*` |
| gate_text（正文裁判） | `judge` | 同 `judge` 槽位 |
| extract（正典抽取 + 场景/章级摘要） | `plan` | 同 `plan` 槽位 |
| archive（角色抽取） | `judge` | 同 `judge` 槽位 |
| archive 末尾的弧级摘要 | `plan` | 同 `plan` 槽位 |

`commit_and_next` 刻意不在这张表里：它是纯状态搬运（定稿、推进游标），一次 LLM 调用
都没有。声明一个用不上的角色只会在装配期多建一颗模型，并让人以为定稿有模型参与。

extract 刻意用规划脑而非审稿脑：抽取者与被审者同源会有盲区一致性——自己写歪的
事实自己抽不出问题，所以与两道裁判分角色（见 `graph.NODE_MODEL_ROLES` 注释）。
摘要与抽取同颗脑也是同一理由：两者都是「读正文 → 结构化压缩」，都不做判定，
交给审稿脑只会让它和闸门抢活。
计划裁判与 `plan_scene`/`write` 异源是 §7 的硬约束：它审的是「照这张卡写会不会出事」，
与写作那颗脑的判断维度重叠时，两道闸门会一起瞎。

未配置的角色回落 `AGENT_CORE_LLM_*` 默认槽位（不配就是单模型）；角色可跨 provider
（此时必须自带 `API_KEY`）。任一角色解析失败则**整体**降级为 `OfflineNovelModel`
——部分降级会得到「真模型正文 + 占位审稿」的混合链路，比统一离线更难排查。
`build_novel_agent(..., chat_model=...)` 传入即所有阶段共用该实例，跳过角色解析。

## 降级

`AGENT_CORE_LLM_API_KEY` 缺失时 `build_novel_agent` 自动切换 `OfflineNovelModel`：
确定性占位构思 / 大纲 / 圣经 / 场景卡 / 正文，正文显式标注 `【离线模式】`，
绝不冒充真实生成。未知 structured schema 抛 `ValueError`。

离线降级在**每个写入语义上**都保持「如实」而不是「通过」：

- 圣经占位只含一条 `status="todo"` 的规则和若干 `openQuestions`，人物/关系/禁用词全空
  ——它是「设定全是缺口」的诚实表达，读侧只注入 confirmed 所以不污染上下文；
- 场景卡占位 `entities=[]`（一个 key 都不挑），于是装配退回全量快照；字数带按提示词里的
  `本章目标字数` 放宽到 0.6~1.6 倍，无该字段时用默认 1200 的带；
- 裁判占位对 `FindingList` 恒返空集，且 `judge_failed=False`、`model_tag` 标出「占位模型审的」
  ——占位正文里没有真实剧情，编一条冲突与编一条「没问题」同样是无据判定；
- 正典抽取产一条 `status="todo"` 的缺口而非「事实」；层级摘要同样各产一行
  （scene 1 + 章级 + 弧级），内容一律带 `【离线模式】` 前缀。

于是离线基线是一组可直接断言的数字：**3 章、有且仅有一次归档 interrupt、
`release=pass`、台账 3 条 `length_out_of_band`（`checker="rule"`、NULL span）、
`judge:0`、书目 `character_count=1`**。计划闸门在这条基线里是**惰性的**——
没有登记表时 `check_plan_entities` 走 `no_registry` 跳过（见「计划闸门」），
这也是它能接进已有链路而不改语义的前提。

真实模型下的 `worldbuild` 另有自己的降级路径（问两次仍失败 → `gap_bible`：
一本只含一条 `todo` 缺口的圣经 + `degraded: true` 事件），与离线占位形状一致，
区别只在 `restatement` 写的是**真实失败原因**——归档卡片要能告诉作者
「这本书的世界没定下来，是因为 X」，而不是留一个看不出缘由的空。

## 数据层（两个协议，两类数据）

| 协议 | 管什么 | 进程内实现 | 生产实现 |
| --- | --- | --- | --- |
| `NovelStore` | 成稿本体：书 / 章 / 角色 | `MockNovelStore` | `HttpNovelStore` |
| `CanonStore` | L0 正典层：断言 / 状态 / 称谓 / 伏笔 / Finding / 摘要 | `InMemoryCanonStore` | `HttpCanonStore` |

分开是因为写入语义不同：正典**只追加、靠闭区间演进、读侧必须带 as-of 章号**，
塞进同一个协议就丢掉这三个性质。`NovelStore.save_chapters` 返回各章 id 是正典的
前提——断言溯源 `source_chapter_id` 与幂等键都要引用它，而它只在落库之后才存在。

`InMemoryCanonStore` 刻意复刻四处 Java 库约束（幂等键重放不重复入库、
`(book, aliasText)` 唯一、as-of 区间过滤、台账按内容键去重），否则会出现「测试过了线上照样错」。
台账那条尤其容易写歪：Java 的查重条件是 `(chapter_id, revision, code, checker, text_start)`，
`idempotencyKey` 随请求带上但**服务端不看**，且 `text_start` 为 NULL 时走 `isNull` 而不是
忽略该条件——所以整章级冲突（字数越带）在同一章只会留一行。内存实现照抄这个后果，
不去「修好」它：两处一致，单测才预判得了线上的台账形态（代价见 PRD §15.3）。

协议是 `typing.Protocol`（结构性子类型）：实现方无需继承，签名匹配即可被子图使用；
方法全为 async，让 HTTP 与内存实现在调用侧完全同形。

## 书级圣经与种子正典（`worldbuild` + `graph.bible_extraction`）

书级圣经（`WorldBible`：规则 / 人物 / 关系 / 禁用词 / `openQuestions`）在动笔之前
就把「作者约定」写进正典，靠的是复用 `append_assertions`——**没有新的库接口**。
三条映射口径都有刻意的理由，改任何一条要回来看 `bible_extraction` 的 docstring：

- 规则行原样转断言，`evidenceQuote` 用「书级圣经：{restatement}」。机制② 的
  「必须逐字摘自正文」约束的是**抽取**；设定此刻还没有正文可引，硬要它自证出处
  等于要求作者先写一章才能定设定。`status` 原样透传，`todo` 不许在这里被替他确认；
- 人物 → 一条 `anchor` 断言 + 一条主别名（正文里的中文名 ↔ 实体键，
  `plan_scene` 挑实体与生死规则认人都只靠别名表）；
  **只有 `alive=False` 才额外写 `is_alive`**：漏记活人不造成任何违规，
  漏记死人则让死者在全书每一章合法地开口——这种不对称就是只写一边的理由；
- 关系 → 复合主语键 `rel:{from}:{to}` + 谓词 `relation_to`，一条关系一行。
  挂在人物键上会让同一个人的两条关系在闸门侧撞成「同一谓词两个值」，
  那是我们自己造的假冲突。

种子行全部挂在**第 1 章**（`established_chapter=1`），出处哈希取
`content_hash(bible.model_dump_json())`，所以重放安全走的是同一条幂等键机制⑦。
`forbidden` 不进正典而是进 `GateRules`（装配期由本轮圣经生成）——禁用词是判定口径，
不是一条事实。`openQuestions` 也不入库，它上浮进 `worldbuilt` 事件与归档卡片：
缺口要看得见才算机制③，静默补全是这套系统失败的主要方式之一。

## 正典闸门（三条硬机制）

| 机制 | 落点 | 不满足时 |
| --- | --- | --- |
| ② 证据强制 | `gates.evidence_verbatim`：`evidenceQuote` 必须逐字出现在本章正文（抽取侧 `filter_extraction` 与规则闸门共用这一份实现） | 整条丢弃，且发 `extract_filtered` 事件（静默丢弃等于没有闸门） |
| ③ 未知即缺口 | 抽取提示词登记 `status="todo"`，`load_snapshot` 不注入 todo/disputed | 不替模型填空，留给人工补录 |
| ⑦ 幂等 | `ExtractionSource.idempotency_key = chapter_id:content_hash[:16]:prompt_version:model` | 命中已提交键时回 `applied=False`，什么都不写 |

证据校验只归一化空白，不做大小写/标点/省略号等宽松匹配——一旦放宽，这条闸门就
退化成又一个软措辞，而它是「正文里确实写了」与「模型觉得应该如此」之间唯一的硬分界。
抽出来的幻觉断言因此到不了正典，但**不阻塞归档**：解析失败（模型违约/网络异常）时
本章记为 `None`，发 `extract_failed` 事件并落 `logger.error`，其余章照常入库。

## 规则闸门（`gates.run_rules`，零 LLM 零网络）

§9 双闸门的确定性一半：只拿「本章文本」与「已登记事实」做机器可判定的比对，
所以语义裁判自己幻读出来的「冲突」不可能从这条通道进台账。判不了的那部分
（动机、世界规则、腔调漂移）由 `judge.run_judge` 承担（见「语义裁判」）
——**规则没命中不代表没问题**。同一套机制在计划侧还有一份，见「计划闸门」。

| 规则 | 编码 | 严重度 | 判据要点 |
| --- | --- | --- | --- |
| `check_length` | `length_out_of_band` | 空章 `blocker`／越硬带 `major`／其余 `minor` | 非空白字符数；带 = `target_words × 0.6~1.6`，硬带 = `0.35~2.2`。用比值而非绝对值：目标 3000 字的章要同一套判据 |
| `check_forbidden_words` | `forbidden_word` | `blocker` | 子串命中，**引号内也算**——违禁词是平台红线，出现在台词里一样过不了审 |
| `check_pov` | `style_drift` | 零星 `minor`，≥3 处 `major` | 契约要求第三人称时叙述层的「我/俺/咱」；`mask_quotes` 先把引号内容遮蔽——对话里的「我」是人物发言，不是叙述者 |
| `check_attribute_conflict` | `attribute_conflict` | `blocker` | 本章 `confirmed` 候选 vs as-of 已确立断言，同 `(subject_key, predicate)` 而取值不相抵 |
| `check_alive_conflicts` | `death_speaks` / `resurrection` | `blocker` | 姓名与发言动词在 ±12 字窗口内共现才算「发言」，只出现名字是旁人提及；`is_alive` false→true 才是复活，true→false 是正常死亡 |
| `check_alias_drift` | `alias_drift` | `major` | 一个称谓指向 ≥2 个实体；反向（一人多称谓）是正常写法，不报 |
| `check_citations` | `foreshadow_missing` / `unknown_ref` | `blocker` / `major` | 正文引用了 `refs` 全集里不存在的 `[fsh#N]` / `[canon#N]`（凭空编号＝认领一条不存在的设定） |

三条贯穿全模块的口径：

- **逐字证据**：带 span 的 Finding，其 `evidenceQuote` 必须逐字等于 `text[start:end]`
  （只容忍空白差异）。规则引擎按 span 取原文生成证据，因此天然成立；
  `validate_findings` 真正守的是裁判产物——两种 checker 走同一个验收口。
- **引用即编号**：`canonRefs` 用 L1 注入的 `[canon#N]` 而非库主键，本轮 overlay 行按
  `pending:{subject}:{predicate}` 复合键解析（那些行没有 id）。引不出编号的命中
  **不静默丢弃**，计入 `GateReport.skipped`（`no_ref` / `no_name` / `no_quote`）——
  静默等于没有闸门。
- **区间可空**：整章级规则（字数越带、状态翻转、登记了但本章未写过的冲突称谓）没有
  可指向的片段，`textStart` / `textEnd` 留空。Java `review_finding.text_start` 允许 NULL
  且服务层按「NULL 也算重复」显式查重，重放不会写双份。

取值比对只在**同一谓词**上放宽到「互为包含」（「黑发」vs「黑」不报，「黑」vs「白」照报），
不动证据那条硬线。可变属性（位置、情绪、持有、知晓、伤势、境界……见
`_MUTABLE_PREDICATES`）不参与冲突判定：它们的「新旧不一致」是剧情推进，该由断言区间
`valid_from/valid_until` 表达，拿它报冲突会把每一次正常改写都报成 bug。
`per_code_limit`（默认 3）按严重度优先取舍：一处系统性漂移会在同一章命中十几条，
台账被同一件事刷屏之后就没人看，宁可在报告里如实记数。

严重度按 §9.3 的**处置能力**分配，不按「问题严重程度」：`blocker` = 改文本就能解决且不
解决就不能 commit；`major` = 机器无权判定谁对，要作者裁定；`minor` = 记录不阻断。
所以字数越带只有空章才是 `blocker`（非空的越带只能整章重写，而定向修补喂不出「整章都错」
的上下文，给 blocker 等于让两条路径互相抵消）。空章没有片段可指，于是走整章重写那一支。

`gate_text` 节点调它（`gates.run_rules`），紧跟着 `judge.run_judge` 的语义裁判，两路产物
在同一个节点里合并后挂在本章的 extract 条目上，再交给 `policy.decide_release` 定放行结论
（见「放行策略」）：有 blocker 就进 `revise` 回环，两轮不过即冻结转人工。装配层用
`GateRules` 按书覆盖口径（字数带、禁用词、视角代词、每编码上限），`build_novel_graph`
用 `chapter_words` 生成它，禁用词与字数带则由 `merge_gate_rules` 按「装配默认 ← 本轮圣经
← 作者手改的 `style_profile`」合并——**两道闸门共用同一份词表**，各读一份就会出现
「计划里没禁、正文里被禁」这种无法归因的分裂。

## 计划闸门（`gates.run_plan_rules`，零 LLM 零网络）

同一套双闸门提前到**还没写第一个字**的那张场景卡上：规则（`run_plan_rules`）+
计划裁判（`run_plan_judge`）+ 策略（`decide_plan_release`）。它与正文闸门的三点不同：

| 维度 | 正文闸门 | 计划闸门 |
| --- | --- | --- |
| 坐标系 | 章节正文的字符区间 | `scene_card_text(card, chapter)` 的**稳定渲染** |
| 处置 | `pass` / `patch` / `rewrite` / `freeze` | `pass` / `replan` / `escalate`（交作者） |
| 产物去向 | 落 `review_finding` 台账 | **不落库**：只进 `plan_gated` 事件、`ns["plan_stats"]` 与归档卡片 |

不落库的理由是那张表的 span 语义就是「正文字符区间」：把卡文本坐标写进去，
作者在工作台点过去会落在正文的别处——**悬空出处比少一条记录更有害**（PRD §15.6 #7）。
`scene_card_text` 因此是规则、裁判、escalate 卡片三方共用的唯一渲染：
坐标只有一份才谈得上复核。

| 规则 | 编码 | 严重度 | 判据要点 |
| --- | --- | --- | --- |
| `check_plan_deaths` | `death_speaks` | `blocker` | 已死人物出现在某场景的 `present` 在场名单里。这条就是计划闸门存在的理由：正文里死者发言要烧一整章 token 才发现，卡上只改一行 |
| `check_plan_entities` | `unregistered_entity` | `major` | `entities ∪ 各场景 present ∪ locationKey` 里出现了 as-of 快照没有的 key。显式写进 `newEntities` 的不算违规（那是作者可见的待补清单）；登记表为空时整条跳过并计 `no_registry`——新书一章事实都没有，报出来就是把开篇每章都判成违规 |
| `check_plan_payoffs` | `foreshadow_missing` | `blocker` | 卡的 `payoffs` 里有不在未收伏笔编号全集里的 `[fsh#N]`：收一条没埋过的线，落进正文就是悬空引用 |
| `check_plan_length` | `length_out_of_band` | `minor` | 卡的字数带容不下 `target_words`（只看带与目标是否相交）。只记录：字数带偏了不违反任何已确立事实，为重排一轮换来的收益抵不上开销 |

`run_plan_rules` 与正文闸门**共用** `validate_findings` 与 `_cap_per_code`：
两道闸门产的是同一种记录（同一套编码、同一份逐字证据要求），分两套校验就有两套松紧，
而「计划闸门的证据标准更松」正是假冲突进台账的入口。带 span 的证据取**整行**
（`sentence_span`）而不是只取那个 key——`fixInstruction` 要落到「改这一行」，
片段没有上下文等于让作者再去猜。编号来自结构化字段而卡文本里找不到时，
退回整章级记录（空 span），不许静默丢弃。

`escalate` 在 `gate_plan` 节点内 `interrupt`（`stage="plan_approval"`，载荷带完整卡文本与
blockers）：按 yes 继续写并把章号记进 `plan_unreviewed`（**批准 ≠ 通过**，归档卡片
用 `unreviewed_note` 交代「这章按计划写了，而那张卡没走完审查」）；
按其他回复则 `halted_at` 定章、直接进 `archive`——强制停，不是强制过。
`_approved` 词表与归档确认共用。因为 interrupt 排在 `_emit` 之前，resume 会重放
本节点的计算段（规则 + 裁判都是只读的），第二次 run 才带出 `plan_gated` 的
`approved` 帧——这是全图唯一一处「重放有代价但可接受」的节点，其余写点都在最后。

一章都没能定稿时（开篇那张卡就被判停），`archive` 不发确认卡也不建空书：
0 章的书目会占住 `book_id` 并让后续 as-of 查询从一条空区间起步。

## 正文闸门的合并口径（`graph.gate_text_node`）

规则在前、裁判在后，两个理由：规则命中即事实，不必再让模型判一遍；规则零成本、裁判烧
token（§9.1/§9.2 的分工本来就是按成本切的）。合并只有一条规则：

- **同 `(code, textStart, textEnd)` 视为同一处**，留规则那条（来源标 `rule`，它更便宜且
  不会变），裁判重复报出的条数进 `duplicated` 计数。不合并的代价是台账里同一件事两行、
  `per_code_limit` 白烧，作者会怀疑闸门坏了。
- 跨来源**不**去重：同一处规则说 `attribute_conflict`、裁判说 `world_rule_break` 是两条
  不同的指控，都留。库侧的去重键含 `checker`，与此一致。

闸门视图取自**本章最后一次 L1 装配**（`CompiledContext.snapshot/refs/style` 存进
`ns["gate_view"]`），不是让节点自己再读一遍库：两份视图之间的差值会被当成冲突报出来，
出问题无法归因。装配失败时 `gate_view` 为 `None`，依赖设定的规则各自计入 `skipped`、
裁判的证据全部定位失败——这是「记为不可判定」而不是「记为通过」，见下条。

`gated` 事件每章一条，带 `rule` / `judge` / `duplicated` / `dropped` / `skipped` / `words` /
`judge_failed` / `blockers` / `majors` / `disputed` / `release` / `unreviewed` 全部计数。
一条修补回环会产出同章的多条 `gated`（章号重复是刻意的：每一轮都是独立判定）。
放行策略与 N6 的 CI 门禁读这一条。

## 语义裁判（`judge.run_judge`，一次 LLM 调用）

规则判不了的那一半（世界规则被无代价违反、动机矛盾、叙述腔调漂移）只能交给模型，
但模型自己也会幻读，所以裁判的输出不比抽取宽松：产物走 `gates.validate_findings`
**同一个**验收口。在 §9.2 的字面要求之外收紧三条，都是为了让「台账里每一条都能跳到
正文的一处」：

| 收紧 | 落点 | 理由 |
| --- | --- | --- |
| `checker` 强制归位 `judge` | `prepare_findings` | 模型自报成 `rule` 就能绕开「裁判必须引编号」那条判定；来源标签不该由被检查的一方填写 |
| 无证据即丢弃 | `prepare_findings`（`no_evidence`） | 一条既无片段又无引文的「动机矛盾」到了工作台就是无法复核的指控，留着等于教作者不信任闸门 |
| span 由证据反推 | `gates.locate_quote` → `text[start:end]` | LLM 数中文字符不可靠，而「证据逐字出现在正文」是它擅长的；偏移错了就把好判定整条扔掉是白丢证据。反推条数进 `relocated`，偏高即提示词该改 |

丢弃都计数（`no_evidence` / `unlocatable` / `invalid_finding` / `judge_failed`），
静默丢弃等于没有闸门。

**裁判失败 ≠ 没有冲突**：`with_structured_output` 报错、返回类型不是 `FindingList`
都记 `failed=True` 且 `dropped={"judge_failed": 1}`，`findings` 为空但绝不带「通过」结论
（§8-⑧ 不静默降级、⑨ 禁自评通过）。离线链路里 `OfflineNovelModel` 对 `FindingList`
恒返空列表，此时 `judge_failed=False`、`model_tag` 标出「这章是占位模型审的」——
消费方要读这两个字段，别把「没有 findings」当成「审查通过」。

裁判只被喂 L1 的**编号清单**（`ref_lines` 渲染成与注入块逐字同构的 `[canon#N]` /
`[fsh#N]`），不给全库：裁判也会被淹，且它引出的编号必须与作者在工作台看到的那一份
指向同一条事实。`rule_codes` 会写进提示词要求「这些编码不要再重复报」。

### 计划侧：`judge.run_plan_judge`

同一次调用的形状、同一个验收口、同一套丢弃计数，唯一的区别是**被检对象**：
它审 `scene_card_text` 渲染出的那张卡，提示词里写死了「场景卡（你唯一的被检对象）」，
就是为了把裁判从「顺着大纲去正文找证据」拉回来——卡上定位不到的证据照样进
`unlocatable`，span 反推落在卡文本坐标上。它拿到的编号清单同样是全量视图那份
（`plan_compiled` 的 `refs`），所以它引的 `[canon#N]` 与规则闸门引的是同一个序列。
调用失败同样记 `failed=True` 且不带任何结论，在计划侧被 `decide_plan_release`
读成 escalate（不可判定 ≠ 这张卡没问题）。

## 放行策略（`policy.decide_release`，零 LLM 零网络）

双闸门只负责「发现」，负责「怎么办」的是这张纯函数表（§9.3）：不烧 token、不读库，
同样输入恒得同样结论，所以它能被直接单测，也能被 N6 的 CI 门禁复算。

| 结论 | 触发条件 | 链路动作 |
| --- | --- | --- |
| `pass` | 没有 blocker（major 只降级事实，minor 只记账） | 照常推进下一章 |
| `patch` | 每条 blocker 都指得出片段（`textStart`/`textEnd` 非空） | 进 `revise`：逐片段定向修补 → 回 `extract` 重抽 → 回闸门重检 |
| `rewrite` | 至少一条 blocker 没有片段（空章、整章级冲突） | 进 `revise` 的整章重写一支，其余同上 |
| `freeze` | 裁判失败（不可判定）**或**修补轮数用尽仍有 blocker | 本章事实与场景/章级摘要作废、台账照记、链路继续推进 |

四个判据各自的理由：

- **major 不拦章节，只把冲突引用的候选降为 `disputed`**：读侧不注入 disputed，于是「被怀疑
  的事实」不会污染后面几章，而作者仍能在台账里看到它。降级条数进 `disputed`。降级只作用
  于本轮内存候选，库里已确认的行不许被一次未裁定的判定改掉。
- **修补回环回到 `extract` 而不是直连 `gate_text`**：正文换了，旧候选的逐字证据可能已经不
  在新正文里。`extract` 按章号**覆盖**条目（`_put_entry`），闸门与入库读的永远是同一份。
- **`judge_failed` 优先于一切**：不可判定不是绿灯，且没有判定就没有可执行的修补，所以冻结
  且不进 `revise`（`repaired` 事件为零）。
- **冻结不中断链路**：50 章的书不能因为第 7 章判不出来就整本报废。冻结章正文照常入库，
  作废的是「事实 + 摘要」，归档卡片用 `frozen` / `frozen_note` 点明哪几章待人工裁定。

`patch_plan` 的三条护栏：片段按 `textStart` **降序**修补（先改前面会让后面的偏移整体失效）；
一次最多 `max_patches`（默认 3）个，多余计入 `overflow`；每个片段带 `patch_context_chars`
（默认 160）字的前后文，只够接语气与指代。`splice_patch` 拒收空返回、与原文一致的返回，
以及长度超过 `max(3×片段长, 60)+40` 的返回——那是模型把整章重写了一遍，收下它等于用
「假装修好了」换掉一段没问题的正文。拒收计入 `rejected`，同一处会在下一轮闸门再次命中。

### 计划侧：`policy.decide_plan_release`（三态）

| 结论 | 触发条件 | 链路动作 |
| --- | --- | --- |
| `pass` | 没有 blocker **也没有 major**（`minor` 一律只记录） | 进 `write` |
| `replan` | 还有硬命中且轮数未用尽 | 回 `plan_scene`，退回意见逐字进提示词的 instruction 段（不新设 replan 节点：两条路径都是「出一张卡」） |
| `escalate` | 轮数用尽 **或** 计划裁判失败 | `gate_plan` 节点内 interrupt 交作者拍板（见「计划闸门」） |

两条与正文侧**刻意相反**的取向，都是成本不对称的结果：

- **major 在计划侧是必修**（正文侧只降级 `disputed`）：卡是作者自己签的东西，
  「以后再说」在这里没有代价，只有改卡有代价；而正文的 major 针对的是「已确认事实可疑」，
  那是人的裁定域，不是机器的。
- **裁判失败 → escalate 而不是 freeze**：这里冻结的是「计划」，作者一句「照这张卡写」
  就能放行；正文侧冻结作废的是已经写成的稿子，没有轻处置可言。`unreviewed=True`
  只在这一支出现——轮数用尽的 escalate 带的是「改不平」而不是「没审动」。

正文修补与计划重排各数各的轮（`gate_repairs` 与 `plan_repairs`），且各自在闸门给出终态
时归零（正文侧 `pass`/`freeze`，计划侧 `pass`/`escalate`）：合并计数会造出「这张卡只改
十几行，所以便宜得多烧一轮」这种分支，而两者的成本不对称不等于判据可以互相豁免——
旧图里的 `revisions`（审稿重写轮数）随 `reflect` 节点一并删除，主观分数不再有任何
豁免权。

## 落库配置（`NOVEL_*`，`config.NovelStoreSettings`）

| 变量 | 默认 | 说明 |
| --- | --- | --- |
| `NOVEL_PERSIST_ENABLED` | `true` | `false` 时成稿与正典都只留进程内（本地无后端 / 离线回归） |
| `NOVEL_API_BASE_URL` | `http://localhost:8080/api` | 容器里覆盖成 `http://api:8080/api` |
| `NOVEL_INTERNAL_TOKEN` | 空 | **必须等于** Spring 侧 `app.internal-token`，否则写入 403 |
| `NOVEL_AUTHOR_ID` | `1` | 内部通道建书要落到某个用户名下（`book.author_id NOT NULL`） |
| `NOVEL_MAX_RETRIES` / `NOVEL_RETRY_BACKOFF_SECONDS` | `3` / `1.5` | 整本成稿只落一次库，一次抖动就丢书不可接受；有终态 `NovelStoreError` |

成稿与正典**同源切换**（要么都打 Java，要么都留内存）是刻意的：一半持久一半内存会
得到「书目在库里、约束这本书的事实只在某个进程内存里」的分裂状态，重启后书还在、
正典没了，比整体不落库更难察觉。写库路径是 `services/api` 的 `/novel/internal/**`
（无用户 JWT 的内部通道，只 `authority=model`），验证脚本见
`scripts/novel-internal-smoke.mjs`。

## 对话面板插槽（`chat.build_novel_chat_agent`）

§10.3 三栏工作台的右栏：读正典与已定稿正文回答设定问题，**只谈不写**。它是与 `novel`
并存的第二个插槽，插槽名 = `artifacts` 键 = 前端 `WSInFrame.agent` 取值，三处同为
`"novel-chat"`：

```
prepare（L1 装配，见「L1 记忆装配」末条）
  → answer（plan 槽出答复）
       ├─ 命中代写守门 / 本轮没有 bookId ──→ END
       └─ propose（judge 槽出提议卡，逐张校验依据后上浮）→ END
```

写面在这里是**字面为空**的，不只是「没被调用」——`test_chat_cannot_write_canon` 用一对
敌对替身（任何写方法一调即抛）跑通整轮讨论，这才是 §12.4-1 不变式的证法：
不调 `save_book` / `save_chapters` / `save_characters`，不调 `append_assertions` /
`close_assertion_range`，不产小说正文，也不触发生成。提议卡只上浮 `PROPOSAL` 事件，
落库由作者在管理端 `POST /novel/proposals` → `PUT /novel/proposals/{id}/adopt` 完成。

三条实现取向：

- **代写守门确定、且刻意窄**：命中「动词 + 近距离宾语」或「强动词 + 宾语任意位置」
  （后者专门收「把下一章生成出来」这种前置说法）才拒；句中带讨论标记
  （怎么 / 为什么 / 对不对 / 梗概…）或出现问号即让位给模型。PRD 自己举的那句
  「把第 3 章那段改冷一点的说法」必须能问到模型，所以守门宁可漏判不可误判，
  答复侧还有提示词的第二道约束。命中即回固定话术并上浮 `chat_prose_refused`，一次模型都不调。
- **出卡前逐张校验依据逐字**（复用机制② 的 `gates.evidence_verbatim`）：依据不在这轮答复里的
  卡直接丢弃并计数上浮。一张作者复核不了的卡会让他「采纳」一个模型凭空编的结论，
  而 §10.5-④ 的冲突预览对这种卡无能为力。`validFromChapter` 由出卡时的参照章决定，
  不让模型自报章号（§10.3 约定 1）。
- **`artifacts["novel-chat"]` 只放原始类型**：实测 msgpack 检查点序列化对未注册的领域
  dataclass 只告警不报错（`BookSnapshot` 会打印「unregistered type」并将在未来版本被阻断），
  于是提示词需要的书目字段由 `_book_of_ns()` 就地重建，参照章正文只活在注入块里、不进命名空间。

降级三段各自可见（§12.2 断链可见性）：`chat_context_failed`（书目或正典读不回，答复明说
不引用任何已登记设定）、`chat_proposal_failed`（抽取失败，本轮无卡）、`chat_prose_refused`
（守门命中，未调模型）。模型侧全有或全无——`plan` / `judge` 任一角色不可用即两个槽一起换
`OfflineNovelChatModel`：部分降级会得到「真模型讨论 + 占位模型出卡」，而占位模型恒不出卡，
作者看到的是一轮看着正常、永远没有提议卡的讨论。

装配阶段发 `chat_context_compiled`（`path: "chat"`，带 `as_of` / `tokens` / `counts`），与生成侧的
`context_compiled` **刻意不同名**：同一台编译器、两条装配路径，N6 的注入 token P95 要分开统计。

插槽 `utterances=()`，因此**不注册 Layer1 意图路由**（`routes_from_agents` 对空语料不建 Route）。
讨论语料与生成语料高度重叠，误命中的代价是「作者想生成却被当成讨论」，
所以唯一正确入口是工作台右栏显式发 `agent:"novel-chat"` + `context:{bookId,chapterId}`。
那两个定位键走 `config.configurable.context`，由 `_context_of` 白名单读取，其余键一概不读。

`PROPOSAL` 帧的 payload 与 Java `ProposalRequest` 字段一一对应（9 键，无 `status`、无 `authority`），
由 `test_proposal_payload_matches_java_request_fields` 钉住；改字段必须 Python 事件 /
WS 帧映射 / Java DTO 三处同改。

**正典读口的作者作用域（N5c-5，PRD §15.16）**：`bookId` 由客户端提供，而 `/ws/chat` 的握手
现在带一次性票据（浏览器与两个小程序都给不了握手 header，沿用 ASR 的先例）。
票据由 Spring Boot 签、也由它验——本包与 chat 宿主都不持 `jwt.secret`。宿主验出的 uid 经
`po_agent_novel.actor` 的 contextvar 传给 `_HttpChannel._headers`，正典读口因此多一个
`X-Actor-Uid`，Java 侧按 `book.author_id` 判归属。**只强制 `novel-chat`**：
cooking / talk / chitchat 仍可匿名连接（已发布小程序没有换票流程），
生成用的 `novel` 插槽不带头（那条链路没有终端用户在场的概念），Java 对「没带头」跳过校验。

## 装配

```python
from po_agent_novel import build_novel_agent

agent = build_novel_agent(settings)  # VerticalAgent(name="novel", ...)
```

数据层可在同一处覆盖：`build_novel_agent(store=..., canon_store=..., novel_settings=...)`，
显式注入的那一侧优先于 `NOVEL_*` 推导结果。

回环预算也在这里给定，三个参数各数各的：`chapter_words`（目标字数，两道闸门的字数带基准）、
`max_repairs`（正文修补轮数，用尽即冻结转人工）与 `max_plan_repairs`（场景卡重排轮数，
用尽即 escalate 交作者拍板）。分开计是必要的：重排只改十几行计划，正文修补要改一千二百字。
`arc_chapters` 控制弧级摘要跨度。N6 的长测会分别调这几个参数。

chat 宿主默认装配本插槽（`services/chat/app/agent.py`），无需手工注册；
对话面板插槽 `build_novel_chat_agent(settings)` 同样由宿主默认注册，两者**各自独立**——
`novel-chat` 起不来只跳过它自己，生成链路的插槽照常登记
（`test_cooking_wiring.py::test_novel_chat_failure_does_not_take_the_novel_slot_down`）。
意图语料由 `NOVEL_UTTERANCES`（8 条）经 `routes_from_agents` 派生进 Layer1 路由。

## 长测监控（`metrics.py`）

`RunMetrics` 是**事件消费端**，不是新的埋点：它只认领链路已经在发的六条 stage
（`plan_compiled` / `context_compiled` / `chat_context_compiled` 三条注入，
以及 `plan_context_failed` / `context_failed` / `chat_context_failed` 三条降级留痕），
不认识的事件返回 `False` 让调用方继续透传。生成链路与对话插槽都**没有** import 它——
真跑 50 章的那个 harness（N6 的后半程，待作者点头）把事件流递给它即可，
离线与真跑读同一份口径，两套数字才可比。

四条口径写在代码注释里，这里说明为什么这么定：

- **三条装配路径分开统计**。计划侧是全量 as-of 视图（要能判「这个实体登记过没有」），
  写作侧按场景卡实体收窄，对话侧还带参照章尾段——预算不同、用途不同，混在一起算
  P95 没有意义（混算的数只会是样本最多那条路径的数）。
- **上限是裁剪保证的绝对值，不是统计期望**。`Budgets` 四层相加 4000，`_fit` 从尾部
  裁剪且整行超限即丢弃，所以「P95 ≤ 4k」实际断言的是**没有任何一次装配越界**
  （`over_limit` 必须为空）。报告里 `ok` 就是这个判据。
- **`degradation_rate` 的分母是装配尝试**（失败 / (失败 + 成功)），不是全书章数：
  一次降级都对应一次本该发生的装配。
- **刻意不统计耗时与模型计费**。宿主目前没有发这两类事件，宁缺毋滥——用估算值冒充
  监控会让长测报告里那一列永远好看。真接上再补。

stage 名与发射方是**字面耦合**（改一处即指标归零且不报错），所以
`test_monitored_stages_are_the_ones_the_link_emits` 用正则扫 `graph.py` / `chat.py`
里以 `_compiled` 和 `context_failed` 结尾的 stage 字面量，与两张映射表精确相等；
改名没同步到 metrics，转红的是这条而不是那份全零报告。

离线半程实测（`InMemoryCanonStore` + 真 `compile_context`，50 章 × 3 路径 = 150 样本，
零模型、零 MySQL，token 口径 `context.approx_tokens`）：

| 装配路径 | 样本 | P50 | P95 | 最大 | 超限 | 降级 |
| --- | --- | --- | --- | --- | --- | --- |
| chat | 50 | 2029 | 2035 | 2036 | 0 | 0 |
| plan | 50 | 2044 | 2050 | 2051 | 0 | 0 |
| write | 50 | 1504 | 2056 | 2064 | 0 | 0 |

as-of 50 时快照 247 条断言。注入块随章数**增长然后贴顶走平**（write 路径逐程增量
361/339/406/19），所以用例断言的是「最后一程不再涨 + `dropped` 在涨」，
而不是凭直觉的「平坦」或「越涨越慢」——前者是 §6-1 要防的「书越长越贵」的真证据，
后者只是好看的曲线。

## 测试

```bash
pnpm agentnovel:test   # 仓库根目录；复用 services/chat/.venv，离线零网络
```

串行跑，不并发。黄金集与长测监控各另有一个独立入口（CI 里各自一条 step：红了要能立刻
分清是「判据/预算退化」还是「用例本身坏了」）：

```bash
services/chat/.venv/Scripts/python.exe -m pytest services/agent-novel/tests/test_golden.py -q
services/chat/.venv/Scripts/python.exe -m pytest services/agent-novel/tests/test_longrun_metrics.py -q
```

### 一致性黄金集（`tests/golden/`，PRD §12.1）

一部 20 章的「带毒」书《霜刃行》：C1–C6 每类至少 8 处已知违规，规则侧 57 条标注
（正文 44 / 计划 13）加 33 条只有语义裁判能判的标注，另配 20 张场景卡。三个文件分工：

- `book.py` —— 语料本体。标注用 `at = parts 下标` 指认**逐字片段**，所以「标注说正文写了
  什么」与「正文实际写了什么」不可能分家；改一句话即同时改掉判据。四个刻意的机关：
  死者第几章死决定哪一章的同一句是违规、哪一章是合法遗言（as-of 支点的活体检测）；
  禁用词故意荒诞（手机/地铁/咖啡混进玄幻稿），要的是命中位置唯一而不是像真小说；
  每章字数由 `_pad` 算进软带，只有四章显式标了越带；抽取候选里掺 5 条证据不在正文中的幻觉；
- `score.py` —— 打分器。只打三面可确定的判据（规则闸门、逐字证据闸门、别名唯一索引），
  闸门输入一律由 `compile_context` 现装配：注入视图与判定视图同源，测的才是链路真正看到的
  那一份。正文侧走 `book_id=None` 的会话 overlay（伏笔从未入库 ⇒ 任何 `[fsh#N]` 都必须报），
  计划侧真入库按章推进（回收编号来自真实未收清单）；
- `test_golden.py` —— 阈值 + 覆盖台账 + 语料自洽三组测试。基线（2026-10-03）：闸门召回
  100%、blocker 36/36、误报 0；新事实入库 32/33、误采 0、幻觉候选 100% 拦下；别名 9/9。

**什么时候必须跑**：换模型、改提示词、改 `GateRules` 任何一条阈值，或改
`gates.py` / `context.py` 的判据。CI 里它是 chat job 的独立 step（不与 agent-novel 其余
用例混成一条，红了要一眼分清是闸门退化还是用例坏了）。

**四条 judge-only 编码（`timeline_break` / `world_rule_break` / `knowledge_leak` /
`motivation_break`）不进召回分母**：CI 不调 LLM，它们只以标注形式存在，并由
`test_judge_only_codes_are_invisible_to_the_rules` 钉住「规则侧对它们应当零命中」——
哪天补了确定性规则，这条测试转红，逼着重算基线。真实召回归 N6 的 50 章长测。

| 文件 | 锁住的行为 |
| --- | --- |
| `test_store.py` | 成稿 + 正典协议语义：id 顺序、按书隔离、追加→快照 `authority=model`、重放不重复、四类计数口径、as-of 闭区间、todo 不注入、称谓唯一冲突跳过、台账内容键去重（换幂等键不翻倍、NULL span 也算重复、跨来源各留一行、缺 code/checker 硬失败、按列宽截断） |
| `test_extract.py` | 逐字证据闸门（保留/丢弃/空白容忍）、抽取失败不 commit、正典只在确认后写、实体键跨章累积、**圣经种子四条口径**（todo 原样透传 + 「书级圣经：」证据、人物 → anchor + 一条主别名、`is_alive` 只为死人写、关系落复合键 `rel:a:b`） |
| `test_gates.py` | 规则闸门：字数带与空白计数、引号遮蔽与语句 span 的坐标回归、七条规则各自的**命中与不命中**两侧（对话内的「我」、可变谓词、`todo` 候选、正常死亡、只提及姓名不发言）、`pending:` 编号解析、`skipped` 三类计数、`validate_findings` 四条作废路径、`per_code_limit` 取舍与顺序确定性；**计划闸门**四条规则各自的命中/跳过两侧（无登记表时 `no_registry`、`newEntities` 显式声明过不算违规、引不出编号时 `no_ref`、卡文本坐标落在**整行**）与 `run_plan_rules` 共用验收口 |
| `test_judge.py` | 语义裁判：编号渲染与注入块同构、span 由证据反推与 `relocated` 计数、`checker` 强制归位、三类丢弃计数、调用失败/返回类型异常都记 `failed=True`（**不当成空集**）、无编号判定被验收口作废、提示词只带编号表与已命中编码；**计划裁判**三条（定位落在卡文本而非正文、证据不在卡上即 `unlocatable`、失败在计划侧同样是不可判定） |
| `test_policy.py` | 放行策略：四条判据各自的命中侧（无 blocker 放行 / 有片段修补 / 无片段整章重写 / 轮数用尽与裁判失败冻结）、major → `disputed` 的键解析（含 `pending:` 里带冒号的实体键）、`apply_disputed` 只降 `confirmed`、`patch_plan` 降序与 `overflow` 截断、上下文窗口与设定行渲染、`splice_patch` 三种拒收形态；**计划侧三态**（major 进必修、minor 只记录、轮数用尽 → escalate 且 `unreviewed` 为假、`judge_failed` → escalate 且为真、`max_plan_repairs=0` 立即升级） |
| `test_context.py` | L1 编译器：预算硬顶与裁剪顺序、`[canon#N]` 编号可见、as-of 双向不泄漏后文、近因窗口与场景/章级二选一、overlay 覆盖库内行、`entities` 收窄 |
| `test_http_store.py` | `httpx.MockTransport` 打真实 Java DTO 线形：载荷 camelCase、幂等重放 `applied=False`、三级摘要载荷形状（scene/chapter/arc）、`upto` 与 `levels` 参数、5xx 重试到终态、业务错误快速失败、**作者作用域**（绑了才带 `X-Actor-Uid`；未绑时该头**不存在**而不是空——空头会被 Java 判成非法值 400；两个并发任务各绑一位作者互不串门） |
| `test_graph.py` | 十一节点拓扑与四条回环、离线基线（**有且仅有一次归档 interrupt**、3 章、`release=pass`）、每章的 `gated` 遥测（规则/裁判/`judge_failed` 计数）、裁判判定与规则命中合并后同批落库、台账只在归档之后写入（拒绝归档时零行）、blocker 驱动 `gate_text ⇄ revise` 回环直至冻结（冻结章正文入库、事实与摘要作废、台账照记）、裁判失败即冻结且不跑修补、空章走整章重写并被救回、`max_repairs` 装配期可调、**计划回环**（未登记实体 → replan 一轮后放行、死人在场在写第一个字之前就被拦、escalate 的 `plan_approval` 卡片带全文且 yes 后归档回执标 `plan_unreviewed`、其他回复即停笔归档、开篇即停不建空书）、**worldbuild 降级**（问两次才退化、退化后缺口在 `openQuestions` 里可见）、L1 注入进到后续章节提示词、`plan_compiled` / `context_compiled` 两段遥测、归档前零库读、归档后摘要树齐全（含 `arc_chapters<=0` 关闭弧级）、`_arc_spans` 的按名切分与等分退回 |
| `test_offline.py` | 离线模型确定性占位：圣经恒 `todo` 且缺口可见、场景卡不挑实体但把登记表带进 `newEntities`、字数带随提示词的目标字数移动、摘要与弧摘要的占位形状 |
| `test_chat.py` | §12.4-1 不变式（敌对替身：整轮讨论零写库、只有提议卡上浮；未采纳的卡永不进注入上下文）、as-of 支点（参照章决定 `as_of`、无参照章退回已归档数、尾段标签在「当前参照章结尾」与「上一章结尾」之间切换）、答复提示词带注入块、历史窗口只管连贯不带事实（且窗口起点必须落在 Human 消息上）、代写守门的双向（三条明显要正文的请求不下模型 + 四条「谈论正文」的说法正常作答）、提议卡载荷与 Java `ProposalRequest` 字段逐一对齐（9 键、无 status/authority、`asOf == validFrom`）、依据不逐字即丢弃、抽取提示词只看本轮答复、无书时照常答复但不进抽取、书目读回失败可见且仍答复、抽取失败上报不吞、离线占位模型既不出正文也不出卡、插槽契约（`utterances=()` ⇒ 只认直连） |
| `test_longrun_metrics.py` | N6 离线半程（PRD §12）：**50 章规模下三条装配路径的注入上限**（150 样本、`over_limit` 为空、每路径 P95 与最大值都 ≤ 4000）、走平形状（最后一程 P95 不再涨 +64 容差，且 `dropped` 必须比前十个章数大——否则收敛只是语料没长起来）、**as-of 回溯不泄漏后文**（在收窄路径上验：第 10 章的快照答不出第 30 章才确立的那句）、**全量重放三遍零写入**（断言 id 序列不变）、别名唯一冲突按计数可见而非静默吞掉、降级与注入分流（`degradation_rate` = 失败/(失败+成功)）、`percentile` 最近秩口径、**stage 名与发射方字面耦合**（正则扫 `graph.py`/`chat.py`，改名没同步即转红）。零模型、零 MySQL，CI 独立 step（同黄金集的理由：红了要分清是「闸门/预算退化」还是「用例本身坏了」） |

## 延伸阅读

- [链路图.md](./链路图.md) —— 启动装配 → 运行期 → 客户端往返的完整链路图（含
  interrupt/resume 时序、事件→帧映射、降级矩阵与落点索引）。
