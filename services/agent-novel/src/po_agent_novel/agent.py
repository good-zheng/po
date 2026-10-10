"""VerticalAgent 工厂：把小说子图装配为可注册进 supervisor 的插槽。

调用方是宿主装配层（services/chat 的内置插槽装配经由
``from po_agent_novel import build_novel_agent`` 调用本模块），产物交给
``po_agent_core.supervisor.build_supervisor_graph`` 作为子图节点挂载。

插槽契约（定义见 ``po_agent_core.agents.slots``）三要素：
- ``name`` 必须与 Layer1 路由的 ``Route.name`` 一致，命中即委托本子图；
- ``utterances`` 是意图路由的匹配语料，宿主据此派生 Route 列表；
- ``graph`` 必须是已编译的 ``CompiledStateGraph``（由 build_novel_graph 产出）。

降级铁律：LLM 未配置（缺 API Key）时使用 OfflineNovelModel 确定性占位，
链路完整可走通（占位场景卡不自报实体、占位裁判不给冲突，因此不进任何回环），
绝不冒充真实生成——占位文本自带【离线模式】标注，用户可一眼识别这不是真实生成内容。

多模型：子图各阶段按角色（plan / write / judge，声明见 graph.NODE_MODEL_ROLES）
分别取模型，配置项形如 ``AGENT_CORE_LLM_ROLES__WRITE__MODEL``；
全部角色都未配置时即单模型（都走 ``AGENT_CORE_LLM_*`` 默认槽位）。
只要有任一角色解析失败就整体降级为离线模型——部分降级会得到
「真模型正文 + 占位审稿」的混合链路，比统一离线更难排查。
"""

from __future__ import annotations

import logging

from langchain_core.language_models.chat_models import BaseChatModel

from po_agent_core import AgentCoreSettings, VerticalAgent, create_chat_model
from po_agent_core.errors import AgentCoreError
from po_agent_novel.config import NovelStoreSettings
from po_agent_novel.graph import STAGE_ROLES, build_novel_graph
from po_agent_novel.http_store import HttpCanonStore, HttpNovelStore
from po_agent_novel.offline import OfflineNovelModel
from po_agent_novel.store import (
    CanonStore,
    InMemoryCanonStore,
    MockNovelStore,
    NovelStore,
)

logger = logging.getLogger(__name__)

# 路由名：与 supervisor 的节点名、Layer1 路由的 Route.name 三者必须一致；
# 同时与 graph.NOVEL_KEY 取值相同，即领域状态在 artifacts 中的命名空间键。
NOVEL_AGENT_NAME = "novel"

# Layer1 意图路由语料（典型用户说法）：覆盖不同题材与说法以扩大召回，
# 语义路由走 embedding 相似度、无 embedding 时降级为关键词（bigram）匹配。
NOVEL_UTTERANCES: tuple[str, ...] = (
    "帮我写一本小说",
    "我想创作一部玄幻小说",
    "写一章关于江湖恩怨的小说",
    "帮我把这个想法扩展成完整的小说",
    "构思一个悬疑故事并写出开头几章",
    "以深夜便利店为背景写个故事",
    "开一本新书，题材你来定",
    "创作一篇都市异闻小说",
)


def _build_stage_models(settings: AgentCoreSettings) -> dict[str, BaseChatModel]:
    """按角色装配各阶段模型；任一角色不可用即整体降级为离线模型。

    不做「部分降级」：只补上能解析的角色会得到混合链路（例如真实模型写正文、
    占位模型打分），用户读到的内容真假参半，比统一离线更难识别与排查。
    """
    models: dict[str, BaseChatModel] = {}
    for role in STAGE_ROLES:
        try:
            models[role] = create_chat_model(settings, role=role)
        except AgentCoreError as exc:
            # 缺 API Key 属预期路径而非异常状态：降级为离线模型，
            # 保证「服务能起、全链路能跑通」，只是内容标注为占位。
            logger.warning("角色 %s 的模型不可用，小说 Agent 降级为离线模式：%s", role, exc)
            return dict.fromkeys(STAGE_ROLES, OfflineNovelModel())
    # 只记模型名（不带 base_url / 密钥）：多模型下「哪个阶段用了哪个模型」
    # 是最常被问到的信息，日志里留一行省去翻配置。
    logger.info(
        "小说 Agent 阶段模型：%s",
        "，".join(f"{role}={getattr(m, 'model_name', type(m).__name__)}" for role, m in models.items()),
    )
    return models


def build_novel_agent(
    settings: AgentCoreSettings | None = None,
    *,
    chat_model: BaseChatModel | None = None,
    store: NovelStore | None = None,
    canon_store: CanonStore | None = None,
    novel_settings: NovelStoreSettings | None = None,
    chapter_count: int = 3,
    chapter_words: int = 1200,
    max_repairs: int = 2,
    max_plan_repairs: int = 2,
    arc_chapters: int = 10,
) -> VerticalAgent:
    """装配小说垂直 Agent 插槽。

    全流程节点（conceive → worldbuild → outline → plan_scene ⇄ gate_plan → write →
    extract → gate_text ⇄ revise → commit_and_next → archive）由 ``build_novel_graph``
    组装并编译，本函数只负责依赖注入与插槽包装。

    :param settings: agent-core 配置（含 LLM 与各阶段角色槽位解析）；缺省读取进程环境
    :param chat_model: 显式注入模型（测试桩 / 宿主复用同一模型实例时传入）：
        语义是「所有阶段共用这一个实例」——传入即跳过按角色创建，
        既不触发离线降级，也不读取 ``llm_roles``
    :param store: 成稿数据层；显式传入即优先于 ``novel_settings`` 的推导结果
    :param canon_store: 正典数据层；同上
    :param novel_settings: 数据层配置（``NOVEL_*``）：``persist_enabled`` 为真时
        两个 store 都指向 Java 的 ``/novel/internal/**``，为假时都留在进程内
    :param chapter_count: 目标章节数，透传给大纲节点
    :param chapter_words: 每章目标字数，透传给计划/正文提示词，也是两道闸门的字数带基准
    :param max_repairs: 单章最大正文修补轮数，用尽仍有 blocker 即冻结该章转人工（§9.3）
    :param max_plan_repairs: 单张场景卡最大重排轮数，用尽即升级给作者拍板。与
        ``max_repairs`` 分开计是必要的：重排只改十几行计划，正文修补要改一千二百字，
        合并计数会让计划问题挤掉正文修补的轮次预算
    :param arc_chapters: 一段剧情弧的章数（弧级摘要跨度），透传给归档后的摘要合成
    :return: 满足插槽契约的 VerticalAgent（name / description / graph / utterances）
    """
    # 显式传 None 时回落到环境配置：AgentCoreSettings 自身完成 env 解析。
    settings = settings or AgentCoreSettings()
    if chat_model is not None:
        stage_models: dict[str, BaseChatModel] = dict.fromkeys(STAGE_ROLES, chat_model)
    else:
        stage_models = _build_stage_models(settings)
    store, canon_store = _resolve_stores(store, canon_store, novel_settings)
    graph = build_novel_graph(
        stage_models,
        store,
        canon_store=canon_store,
        chapter_count=chapter_count,
        chapter_words=chapter_words,
        max_repairs=max_repairs,
        max_plan_repairs=max_plan_repairs,
        arc_chapters=arc_chapters,
    )
    # 插槽契约校验在 VerticalAgent.__post_init__（name 非空且非 __ 前缀、
    # description 非空、graph 必须为 CompiledStateGraph），此处不再重复校验。
    return VerticalAgent(
        name=NOVEL_AGENT_NAME,
        description="小说创作：从一句话想法到完整书稿（构思 → 大纲 → 逐章生成与审稿循环 → 归档确认）",
        graph=graph,
        utterances=NOVEL_UTTERANCES,
    )


def _resolve_stores(
    store: NovelStore | None,
    canon_store: CanonStore | None,
    novel_settings: NovelStoreSettings | None,
) -> tuple[NovelStore, CanonStore]:
    """按配置推导两个数据层，显式注入的那一侧原样保留。

    成稿与正典同源切换（要么都打 Java，要么都留在进程内）是刻意的：
    一半持久一半内存会得到「书目在库里、约束这本书的事实只在某个进程内存里」
    的分裂状态，重启后书还在、正典没了，比整体不落库更难察觉。
    """
    resolved = novel_settings or NovelStoreSettings()
    if resolved.persist_enabled:
        return (
            store or HttpNovelStore(resolved),
            canon_store or HttpCanonStore(resolved),
        )
    logger.info("NOVEL_PERSIST_ENABLED=false：小说与正典均只留在进程内，不落库")
    return store or MockNovelStore(), canon_store or InMemoryCanonStore()
