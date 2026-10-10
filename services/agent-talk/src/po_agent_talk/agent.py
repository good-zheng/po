"""talk 垂直 Agent 的装配入口。

对外只暴露一个工厂 :func:`build_talk_agent`：宿主（chat 服务）在
``_builtin_agents`` 里调它，拿到 :class:`VerticalAgent` 即完成插槽登记。

装配顺序与失败策略与 cooking 插槽保持一致：

1. 取 ``talk`` 角色的聊天模型 —— 未配置时回落 agent-core 的默认槽位；
2. 取模型失败 → 用 :class:`OfflineTalkModel` 顶上，宿主照常启动，
   用户拿到规则版卡片而不是 500；
3. 落库回调是「尽力而为」：只在收到结果后 POST，失败仅记日志。
"""

from __future__ import annotations

import logging

from langchain_core.language_models.chat_models import BaseChatModel

from po_agent_core import (
    AgentCoreSettings,
    VerticalAgent,
    create_chat_model,
)
from po_agent_core.errors import AgentCoreError

from po_agent_talk.config import TalkSettings
from po_agent_talk.graph import build_talk_graph
from po_agent_talk.offline import OfflineTalkModel

logger = logging.getLogger(__name__)

# 插槽名：必须与 Layer1 路由的 Route.name 一致；小程序也可用 WSInFrame.agent 直连
TALK_AGENT_NAME = "talk"

# 模型角色：独立于 chat/cooking 的自定义角色，
# 可用 AGENT_CORE_LLM_ROLES__TALK__MODEL 单独指定（如更便宜、更快的小模型）
TALK_ROLE = "talk"

TALK_DESCRIPTION = (
    "沟通助手：分析对方刚才那句话的真实意图、潜台词与情绪，"
    "给出可以直接照着说的回复"
)

# Layer1 意图路由语料：覆盖「他什么意思 / 我怎么回 / 帮我分析」三类说法。
# 注意语料要像用户真的会说出口的话，而不是关键词列表——语义路由靠相似度命中。
TALK_UTTERANCES: tuple[str, ...] = (
    "他这话什么意思",
    "我该怎么回",
    "帮我分析一下这句话",
    "怎么回答比较好",
    "他是不是在暗示什么",
    "这句话的潜台词是什么",
    "我该怎么接话",
    "对方是不是生气了",
    "这样说合适吗",
    "帮我想想怎么回复",
)


def _create_model(settings: AgentCoreSettings) -> BaseChatModel:
    """按 ``talk`` 角色取模型；失败即降级到离线模型（含原因日志）。"""
    try:
        return create_chat_model(settings, role=TALK_ROLE)
    except AgentCoreError as exc:
        logger.warning("talk 角色模型不可用，降级为离线模型：%s", exc)
        return OfflineTalkModel()


def build_talk_agent(
    settings: AgentCoreSettings | None = None,
    *,
    chat_model: BaseChatModel | None = None,
    talk_settings: TalkSettings | None = None,
) -> VerticalAgent:
    """构建 talk 垂直 Agent 插槽。

    :param settings: agent-core 配置（决定模型怎么连）
    :param chat_model: 聊天模型；不给则按 ``talk`` 角色解析，失败降级离线
    :param talk_settings: 落库配置（回调地址与内部令牌）
    """
    core_settings = settings or AgentCoreSettings()
    talk_config = talk_settings or TalkSettings()
    model = chat_model or _create_model(core_settings)
    return VerticalAgent(
        name=TALK_AGENT_NAME,
        description=TALK_DESCRIPTION,
        graph=build_talk_graph(model, history_limit=talk_config.history_limit),
        utterances=TALK_UTTERANCES,
        metadata={"role": TALK_ROLE, "api_base_url": talk_config.api_base_url},
    )
