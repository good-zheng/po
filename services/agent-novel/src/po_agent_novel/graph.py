"""小说创作子图：conceive → outline → generate ⇄ reflect → archive。

领域状态全部放在 ``artifacts["novel"]`` 命名空间（supervisor 不解释），
子图状态 schema 直接复用 CoreState——禁止向 CoreState 添加领域字段。

生成循环（对齐参考实现 generate_agent 的 should_continue 语义）：
审稿评分 ≥ target_score 定稿并进入下一章；未达标且修订次数未用尽则
带审稿意见重写本章；修订次数用尽强制定稿，避免无限循环。

归档前 ``interrupt`` 挂起等待用户确认，确认后经 NovelStore 写入数据层
（当前为 mock，协议粒度对齐 Java novel 模块的 REST 资源划分）。
节点进度经 ``get_stream_writer`` 发布 thinking / plan 领域事件，
由 AgentRunner 的 custom 流翻译透传。

分阶段模型：节点在**装配期**按 ``NODE_MODEL_ROLES`` 声明的角色从
``stage_models`` 取模型——构思与大纲用规划脑（plan），正文用写作脑（write），
审稿与归档抽取用审稿脑（judge）。三者可以是同一个模型实例（单模型部署），
也可以各配各的（见 agent-core 的 ``AGENT_CORE_LLM_ROLES__*``）。

运行位置与状态归属（两处易错点）：
- 本图被 ``supervisor.build_supervisor_graph`` 以 ``builder.add_node(name, graph)``
  的方式挂为子图节点，因此运行时是「父图内的一个节点」；
- 本图的 checkpointer 由父图统一供给（compile() 不挂 saver）：interrupt 的挂起
  状态与 resume 计数都写在父图线程的 checkpoint 上，thread_id 即 conversation_id。
  若子图自行挂 saver，反倒会在父图 checkpoint 之外产生第二份状态，破坏恢复语义。
"""

from __future__ import annotations

import logging
from collections.abc import Mapping
from typing import Any

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.config import get_stream_writer
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import interrupt

from po_agent_core.config import ModelRole
from po_agent_core.events import EventType
from po_agent_core.supervisor.state import CoreState
from po_agent_novel.prompts import (
    conceive_prompt,
    extract_characters_prompt,
    outline_prompt,
    reflect_prompt,
    revise_prompt,
    write_chapter_prompt,
)
from po_agent_novel.schemas import (
    BookDraft,
    BookIdea,
    ChapterDraft,
    ChapterOutline,
    CharacterList,
    Outline,
    Reflection,
)
from po_agent_novel.store import NovelStore

logger = logging.getLogger(__name__)

# artifacts 命名空间键：必须与插槽名 agent.NOVEL_AGENT_NAME 一致，
# 否则宿主/其他垂直 Agent 无法按名定位本 Agent 的领域数据。
NOVEL_KEY = "novel"

# 节点名常量：同时会作为 Runner STEP 事件 payload 的 ``node`` 字段上浮，
# 前端按此展示节点级进度，改动即影响前端展示口径。
CONCEIVE_NODE = "conceive"
OUTLINE_NODE = "outline"
GENERATE_NODE = "generate"
REFLECT_NODE = "reflect"
ARCHIVE_NODE = "archive"

# 归档确认的「肯定」词表：WS 上行帧里 resume 值是用户输入的字符串（如 yes），
# 因此需要做字符串归一化；小写化 + strip 以兼容 "Yes" / " 确认 "。
_APPROVE_WORDS = {"yes", "true", "1", "ok", "确认", "同意", "是"}

# 节点 → 模型角色：阶段换模型的唯一维护点。
# 节点在装配期按这张表从传入的 stage_models 里取模型，因此「哪个阶段用哪个模型」
# 是子图自己声明的领域知识，配置侧（AGENT_CORE_LLM_ROLES__*）只需按角色名覆盖，
# 无需知道子图内部有哪些节点。改这张表即改阶段归属，记得同步 STAGE_ROLES 的调用方说明。
NODE_MODEL_ROLES: dict[str, ModelRole] = {
    CONCEIVE_NODE: ModelRole.PLAN,  # 构思：结构化抽取，属规划类
    OUTLINE_NODE: ModelRole.PLAN,  # 大纲：与构思同角色（同一颗「规划脑」）
    GENERATE_NODE: ModelRole.WRITE,  # 正文与修订：长文生成，成本与质量的主战场
    REFLECT_NODE: ModelRole.JUDGE,  # 审稿打分：判定类，用便宜/快的模型即可
    ARCHIVE_NODE: ModelRole.JUDGE,  # 归档内的角色抽取：同为结构化判定类
}

# 本图需要的全部角色（去重、保持声明顺序，取字符串形态即 stage_models 的键）：
# 装配层据此逐个建模型，也是「缺哪个角色就报哪个名字」的校验清单。
STAGE_ROLES: tuple[str, ...] = tuple(dict.fromkeys(NODE_MODEL_ROLES.values()))


def _ns(state: CoreState) -> dict[str, Any]:
    """读取本 Agent 的领域命名空间，返回浅拷贝副本。"""
    # 返回副本而非原引用：节点在副本上就地修改后整体回写，
    # 避免直接改写父图传入 state 中的同一 dict 造成隐式共享写。
    artifacts = state.get("artifacts") or {}
    namespace = artifacts.get(NOVEL_KEY)
    # 首次进入（conceive 之前）命名空间不存在，此时按空字典处理。
    return dict(namespace) if isinstance(namespace, dict) else {}


def _update(ns: dict[str, Any]) -> dict[str, Any]:
    """节点返回值：整体替换 novel 命名空间（merge_artifacts 后写胜出）。

    CoreState.artifacts 以 merge_artifacts 归并（浅合并、同名顶层键整体替换），
    因此每次回写都必须给出全量领域数据，且必须带 NOVEL_KEY 这一层——
    只返回子字段的「补丁式」更新既会丢字段也无法被合并。
    """
    return {"artifacts": {NOVEL_KEY: ns}}


def _emit(event_type: EventType, content: str, payload: dict[str, Any] | None = None) -> None:
    """发布一条领域进度事件（custom 流），由宿主 AgentRunner 翻译为前端帧。

    :param event_type: 事件类型，本图只用 THINKING / PLAN 两种进度语义
    :param content: 面向用户的一句话进度描述
    :param payload: 结构化附加信息，约定含 ``stage`` 字段供前端区分阶段
    """
    try:
        writer = get_stream_writer()
    except RuntimeError:  # 无流上下文（节点被直接调用）时静默跳过
        return
    # 帧结构须与 AgentRunner.translate_custom 的解析约定一致（type/content/payload）：
    # type 合法才会被原样透传为对应事件，否则会被包成 STEP 兜底。
    writer({"type": event_type.value, "content": content, "payload": payload or {}})


def _last_user_text(state: CoreState) -> str:
    """取最近一条用户消息文本，作为本轮委托的原始需求（构思输入）。"""
    # supervisor 是单轮委托语义、messages 由 add_messages 满载归并，
    # 因此逆序遇到的第一条 HumanMessage 即本轮输入；
    # content 可能是多模态列表，统一转 str 才能安全拼进提示词。
    for message in reversed(state.get("messages") or []):
        if isinstance(message, HumanMessage):
            content = message.content
            return content if isinstance(content, str) else str(content)
    return ""


def _approved(value: Any) -> bool:
    """归档确认：resume 值为 WS 字符串（如 ``yes``），也兼容布尔。

    interrupt 恢复时本节点会从头重放，``interrupt(...)`` 的返回值即宿主
    ``Command(resume=value)`` 传入的值——经 WS 上行帧到达时是 str，
    直连调用/测试时可以是 bool，故这里统一归一化。
    """
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in _APPROVE_WORDS
    return bool(value)


def _chapter_heading(index: int, title: str) -> str:
    """拼装章节标题；title 已带「第N章」前缀时不重复添加。"""
    prefix = f"第{index}章"
    # 提示词要求模型只输出正文、不带标题，序号与标题在此统一生成，
    # 避免模型自拟标题导致各章标题格式不一致。
    return title if title.startswith(prefix) else f"{prefix} {title}"


def _book_text(idea: BookIdea, chapters: list[ChapterDraft]) -> str:
    """拼装「书名 + 题材 + 梗概 + 各章正文」的完整书稿文本。

    归档成功与用户选择暂不归档两种回执共用：无论是否入库，
    用户都能在本轮回复里拿到成稿全文。
    """
    parts = [f"《{idea.title}》（{idea.genre}）\n{idea.summary}"]
    parts.extend(f"\n{_chapter_heading(c.index, c.title)}\n{c.content}" for c in chapters)
    return "\n".join(parts)


def build_novel_graph(
    stage_models: Mapping[str, BaseChatModel],
    store: NovelStore,
    *,
    chapter_count: int = 3,
    chapter_words: int = 1200,
    target_score: float = 8.0,
    max_revisions: int = 2,
) -> CompiledStateGraph:
    """编译小说创作子图。

    不挂 checkpointer：作为 supervisor 子节点运行时由父图统一供给
    （interrupt 挂起 / resume 续跑依赖父图的线程 checkpoint）。
    也正因如此，本函数不接收 saver / thread_id 参数，单测可用
    ``graph.ainvoke(state, config=...)`` 直连驱动。

    拓扑：START → conceive → outline → generate → reflect，
    reflect 经条件边二选一——继续写/改写（generate）或归档（archive），
    archive → END。generate ⇄ reflect 即反思回环，回环出口只有 archive。

    :param stage_models: 角色 → 模型实例，键取 ``ModelRole``（见 NODE_MODEL_ROLES）。
        每个节点在**装配期**按角色取定模型并绑进闭包，运行期不再查表——
        因此换模型只需改配置后重启，运行中的图不会中途换脑。
    :param store: 归档数据层（NovelStore 协议），仅 archive 节点使用
    :param chapter_count: 大纲章数，写入 outline_prompt 的规划要求
    :param chapter_words: 每章目标字数，写入正文与修订提示词
    :param target_score: 定稿分数线；reflect 节点据此判定回环
    :param max_revisions: 单章最大修订轮数（回环次数的硬上限）
    :return: 已编译子图（CompiledStateGraph），状态 schema 为 CoreState
    """
    missing = [role for role in STAGE_ROLES if role not in stage_models]
    if missing:
        # 缺角色即刻报错而不是回落到某个已有模型：静默回落会得到「真模型正文 +
        # 占位审稿」这类混合链路，比整体降级更难排查（离线降级交给装配层决定）。
        names = ", ".join(missing)
        raise ValueError(f"缺少阶段模型：{names}（本图需要 {'/'.join(STAGE_ROLES)}）")
    # 四个结构化输出绑定是「LLM 调用契约」：schema 即输出约束（见 schemas 模块），
    # 与 prompts 的「输出格式」节互为双保险。此处不做任何模型差异分支——
    # 真实模型与离线模型（OfflineNovelModel.with_structured_output）接口一致。
    # method 显式指定 function calling：langchain-openai 1.x 的默认方法是发
    # json_schema 型 response_format，而 DeepSeek / DashScope 兼容端点不支持，
    # 会直接 400（This response_format type is unavailable now）；工具调用是各
    # OpenAI 兼容端点的最大公约数，OpenAI 侧同样支持。
    conceiver = stage_models[NODE_MODEL_ROLES[CONCEIVE_NODE]].with_structured_output(
        BookIdea, method="function_calling"
    )
    outliner = stage_models[NODE_MODEL_ROLES[OUTLINE_NODE]].with_structured_output(
        Outline, method="function_calling"
    )
    writer = stage_models[NODE_MODEL_ROLES[GENERATE_NODE]]
    reflector = stage_models[NODE_MODEL_ROLES[REFLECT_NODE]].with_structured_output(
        Reflection, method="function_calling"
    )
    character_extractor = stage_models[NODE_MODEL_ROLES[ARCHIVE_NODE]].with_structured_output(
        CharacterList, method="function_calling"
    )

    async def conceive_node(state: CoreState) -> dict[str, Any]:
        """构思节点（图入口）：一句话想法 → 结构化 BookIdea，并初始化领域状态。"""
        brief = _last_user_text(state)
        idea: BookIdea = await conceiver.ainvoke(conceive_prompt(brief))
        # 首次写入整个 novel 命名空间：下列字段即后续所有节点共享的状态契约。
        # index 是 0 基章节游标，revisions 是「当前章」已用修订轮数（定稿后清零）；
        # draft/feedback 是回环期临时数据，chapters 只收定稿章节。
        ns: dict[str, Any] = {
            "brief": brief,
            "idea": idea,
            "outline": [],
            "chapters": [],
            "index": 0,
            "draft": "",
            "feedback": "",
            "revisions": 0,
            "action": "",
            "book_id": "",
        }
        _emit(
            EventType.THINKING,
            f"构思完成：《{idea.title}》（{idea.genre}）",
            {"stage": "conceived", "title": idea.title, "genre": idea.genre},
        )
        return _update(ns)

    async def outline_node(state: CoreState) -> dict[str, Any]:
        """大纲节点：按 chapter_count 规划全书章节，覆写 ns["outline"]。"""
        ns = _ns(state)
        idea: BookIdea = ns["idea"]
        outline: Outline = await outliner.ainvoke(outline_prompt(idea, chapter_count))
        # 只取 chapters 列表入状态：章节序号由列表下标隐含（见 schemas.ChapterOutline），
        # 因此这里不额外存 index 字段。
        ns["outline"] = list(outline.chapters)
        titles = [chapter.title for chapter in outline.chapters]
        # PLAN 事件区别于 THINKING：前端用它渲染「全书规划」类进度卡片。
        _emit(EventType.PLAN, "大纲：" + " / ".join(titles), {"stage": "outlined", "chapters": titles})
        return _update(ns)

    async def generate_node(state: CoreState) -> dict[str, Any]:
        """写作节点：产出「当前章」正文，初稿与修订共用本节点。

        进入本节点有两条路径——outline 直连（初稿）与 reflect 回环（修订），
        用 ns["feedback"] 是否为空区分，而不是另设一个节点：
        两条路径的 LLM 调用方式相同，只是提示词模板不同。
        """
        ns = _ns(state)
        idea: BookIdea = ns["idea"]
        outline: list[ChapterOutline] = ns["outline"]
        # index 指向正在写的章；chapters 只含已定稿章节，故两者长度关系为
        # len(chapters) == index（回环重写时 index 不变）。
        index: int = ns["index"]
        chapter = outline[index]
        feedback: str = ns.get("feedback", "")
        if feedback:
            # 回环路径：带上审稿意见与当前稿重写，feedback 由 reflect 节点写入。
            prompt = revise_prompt(idea, chapter, index, ns["draft"], feedback, chapter_words)
        else:
            # 初稿路径：取上一章定稿末尾 200 字做衔接参考；开篇无上文则传空串，
            # 由提示词切换为「铺开世界观」的开篇要求。
            prev_tail = ns["chapters"][-1].content[-200:] if ns["chapters"] else ""
            prompt = write_chapter_prompt(idea, outline, index, prev_tail, chapter_words)
        # 正文走 WRITE 角色模型（初稿与修订同一条路径，故只在此处绑定一次）。
        response = await writer.ainvoke(prompt)
        # 正文提示词要求「直接输出正文」，此处不再做清洗，只做类型归一化
        # （个别模型会返回内容块列表而非纯字符串）。
        draft = response.content if isinstance(response.content, str) else str(response.content)
        # 写入 draft 但不入 chapters：只有 reflect 判定定稿才收入 chapters，
        # 未定稿的稿子下一轮会被修订结果覆盖。
        ns["draft"] = draft
        kind = "修订稿" if feedback else "初稿"
        _emit(
            EventType.THINKING,
            f"第 {index + 1} 章《{chapter.title}》{kind}完成（约 {len(draft)} 字）",
            {"stage": "drafted", "chapter": index + 1, "revised": bool(feedback)},
        )
        return _update(ns)

    async def reflect_node(state: CoreState) -> dict[str, Any]:
        """评审节点：给当前章打分并决定回环或前进（回环的唯一判定点）。

        定稿条件为二者之一：
        - ``score >= target_score``：达到分数线（默认 8 分，阈值由调用方装配时给定）；
        - ``revisions >= max_revisions``：修订轮数用尽，强制定稿。
        后一条是防死循环的兜底——评分由 LLM 给出，不能保证单调改善，
        没有这个上限就可能「不达标即重写」无限循环。
        定稿即把 draft 落成 ChapterDraft（index 转 1 基）并推进游标；
        未定稿则攒下审稿意见，供 generate 节点下一轮重写使用。
        """
        ns = _ns(state)
        outline: list[ChapterOutline] = ns["outline"]
        index: int = ns["index"]
        chapter = outline[index]
        reflection: Reflection = await reflector.ainvoke(
            reflect_prompt(chapter, index, ns["draft"], target_score)
        )
        if reflection.score >= target_score or ns["revisions"] >= max_revisions:
            ns["chapters"] = [
                *ns["chapters"],
                # ChapterDraft.index 是 1 基（对外展示口径），此处完成 0 基 → 1 基转换。
                ChapterDraft(index=index + 1, title=chapter.title, content=ns["draft"]),
            ]
            ns["draft"] = ""
            ns["feedback"] = ""
            # revisions 是「当前章」的计数，定稿后清零，下一章重新计。
            ns["revisions"] = 0
            ns["index"] = index + 1
            # action 只区分「是否收尾」：next 与 revise 都会回到 generate，
            # 由 generate 依据 feedback 是否为空选择提示词，回环条件只此一处维护。
            ns["action"] = "next" if ns["index"] < len(outline) else "archive"
            _emit(
                EventType.THINKING,
                f"第 {index + 1} 章定稿（评分 {reflection.score}）",
                {"stage": "chapter_done", "chapter": index + 1, "score": reflection.score},
            )
        else:
            ns["revisions"] += 1
            # comment 会被原样喂给 revise_prompt，故提示词要求低分意见必须具体可执行。
            ns["feedback"] = reflection.comment
            ns["action"] = "revise"
            _emit(
                EventType.THINKING,
                f"第 {index + 1} 章评分 {reflection.score}，开始第 {ns['revisions']} 轮修订",
                {"stage": "revise", "chapter": index + 1, "score": reflection.score},
            )
        return _update(ns)

    async def archive_node(state: CoreState) -> dict[str, Any]:
        """归档节点：人在环确认点——先 interrupt 等用户拍板，再决定是否落库。

        interrupt 会让整个图在此挂起（父图 checkpoint 记录断点），宿主把
        INTERRUPT 事件推给前端；用户回复后宿主以 ``Command(resume=value)``
        续跑，本节点从头重放，``interrupt(...)`` 返回 resume 值。
        因此 interrupt 之前的代码必须是无副作用的纯读取（这里只有 _ns）。
        """
        ns = _ns(state)
        idea: BookIdea = ns["idea"]
        chapters: list[ChapterDraft] = ns["chapters"]
        # 载荷即前端确认卡片的展示内容，必须可 JSON 序列化（会写进 checkpoint）；
        # question/hint 属协议约定字段：Runner 取 question 作为事件摘要，
        # hint 告知用户什么回复算「确认」（词表见 _APPROVE_WORDS）。
        approval = interrupt(
            {
                "question": f"《{idea.title}》共 {len(chapters)} 章已完稿，是否归档入库？",
                "title": idea.title,
                "genre": idea.genre,
                "chapter_count": len(chapters),
                "hint": "确认归档请回复 yes，其他回复视为暂不归档",
            }
        )
        # 无论是否归档都拼出成稿全文，两种回执都能让用户直接读到结果。
        book_text = _book_text(idea, chapters)
        if _approved(approval):
            # 先抽角色再落库；save_book 返回的 book_id 是后续两次写入的外键，
            # 三者顺序不可调换，对应 Java novel 模块 book/chapter/character 的资源划分。
            extracted: CharacterList = await character_extractor.ainvoke(
                extract_characters_prompt(idea.title, chapters)
            )
            book_id = await store.save_book(
                BookDraft(title=idea.title, genre=idea.genre, summary=idea.summary)
            )
            await store.save_chapters(book_id, chapters)
            await store.save_characters(book_id, extracted.characters)
            # book_id 回写命名空间：便于中断恢复后的观测与后续续写引用。
            ns["book_id"] = book_id
            _emit(EventType.THINKING, f"已归档：{book_id}", {"stage": "archived", "book_id": book_id})
            reply = f"{book_text}\n\n已归档入库（{book_id}，共 {len(chapters)} 章、{len(extracted.characters)} 名角色）。"
        else:
            # 暂不归档只是不落库：正文照样回给用户，作品仍留在本会话的 checkpoint 中。
            _emit(EventType.THINKING, "用户选择暂不归档", {"stage": "declined"})
            reply = f"{book_text}\n\n按你的要求暂不归档，本作保留在当前会话中。"
        # 本节点是子图中唯一向 messages 追加内容的节点（给用户最终回执），
        # 因此这里不走 _update，而是同时返回 artifacts 与 messages 两部分。
        return {"artifacts": {NOVEL_KEY: ns}, "messages": [AIMessage(content=reply)]}

    def after_reflect(state: CoreState) -> str:
        """reflect 后的条件边：只有 action == "archive" 才收尾，其余都回 generate。

        next（下一章）与 revise（重写本章）都指向 generate，由 generate
        内部按 feedback 分流，这样「继续写」的分支只需在生成侧维护一次。
        """
        return ARCHIVE_NODE if _ns(state).get("action") == "archive" else GENERATE_NODE

    builder: StateGraph = StateGraph(CoreState)
    builder.add_node(CONCEIVE_NODE, conceive_node)
    builder.add_node(OUTLINE_NODE, outline_node)
    builder.add_node(GENERATE_NODE, generate_node)
    builder.add_node(REFLECT_NODE, reflect_node)
    builder.add_node(ARCHIVE_NODE, archive_node)
    # 固定边构成主干：conceive → outline → generate → reflect 单向推进。
    builder.add_edge(START, CONCEIVE_NODE)
    builder.add_edge(CONCEIVE_NODE, OUTLINE_NODE)
    builder.add_edge(OUTLINE_NODE, GENERATE_NODE)
    builder.add_edge(GENERATE_NODE, REFLECT_NODE)
    # 唯一条件边，也是唯一的回环点：reflect 的裁决结果决定继续还是收尾。
    builder.add_conditional_edges(REFLECT_NODE, after_reflect, [GENERATE_NODE, ARCHIVE_NODE])
    builder.add_edge(ARCHIVE_NODE, END)
    return builder.compile()
