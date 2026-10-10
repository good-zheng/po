"""po-agent-talk：po 的言外（EchoTalk）沟通助手垂直 Agent。

对外入口：

- :func:`build_talk_agent` —— 宿主（``services/chat``）在 ``_builtin_agents``
  里调用它并登记返回的 :class:`VerticalAgent`；
- :func:`parse_analysis` —— 把模型输出的 JSON 落成 :class:`TalkAnalysis`，
  宿主用它决定是否值得回写；
- :func:`persist_suggestion` —— 把结果回调给 Spring Boot 落库（尽力而为）。

模型走 agent-core 的 ``talk`` 角色槽位，未配置时自动降级为离线规则模型，
与 cooking 插槽的降级策略一致。
"""

__version__ = "0.1.0"

from po_agent_talk.agent import (
    TALK_AGENT_NAME,
    TALK_DESCRIPTION,
    TALK_ROLE,
    TALK_UTTERANCES,
    build_talk_agent,
)
from po_agent_talk.config import TalkSettings
from po_agent_talk.graph import build_talk_graph
from po_agent_talk.offline import OFFLINE_TAG, OfflineTalkModel
from po_agent_talk.persist import persist_suggestion
from po_agent_talk.schema import (
    SUGGESTION_STYLES,
    SuggestionItem,
    TalkAnalysis,
    parse_analysis,
)

__all__ = [
    "__version__",
    # 装配入口
    "build_talk_agent",
    "TALK_AGENT_NAME",
    "TALK_ROLE",
    "TALK_DESCRIPTION",
    "TALK_UTTERANCES",
    # 配置
    "TalkSettings",
    # 子图
    "build_talk_graph",
    # 结构化输出
    "TalkAnalysis",
    "SuggestionItem",
    "SUGGESTION_STYLES",
    "parse_analysis",
    # 落库
    "persist_suggestion",
    # 离线降级
    "OfflineTalkModel",
    "OFFLINE_TAG",
]
