"""cooking 垂直 Agent 的装配入口。

对外只暴露一个工厂 :func:`build_cooking_agent`：宿主（chat 服务）在
``_builtin_agents`` 里调它，拿到 :class:`VerticalAgent` 就完成了插槽登记。

装配顺序与失败策略：

1. 取 ``cooking`` 角色的聊天模型 —— 该角色是开放词汇里的一个普通角色，
   未配置时自动回落 agent-core 的默认槽位，即「不配就是单模型」；
2. 取模型失败（缺 key / provider 非法）→ 用 :class:`OfflineCookingModel`
   顶上，宿主照常启动，用户看到诚实的「离线模式」而非 500；
3. 数据源默认走 Java 菜谱接口，装配期不探活——后端没起时工具会返回
   可读错误，前端表现为「暂时查不到」，优于让整个 chat 服务启动失败。
"""

from __future__ import annotations

import logging

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.tools import BaseTool

from po_agent_core import (
    AgentCoreSettings,
    VerticalAgent,
    create_chat_model,
)
from po_agent_core.errors import AgentCoreError

from po_agent_cooking.config import CookingSettings
from po_agent_cooking.graph import build_cooking_graph
from po_agent_cooking.offline import OfflineCookingModel
from po_agent_cooking.recipes import HttpRecipeStore, RecipeStore
from po_agent_cooking.tools import build_recipe_tools

logger = logging.getLogger(__name__)

# 插槽名：必须与 Layer1 路由的 Route.name 一致，命中后 supervisor 才委托过来
COOKING_AGENT_NAME = "cooking"

# 模型角色：独立于 chat/plan/write/judge 的自定义角色，
# 可用 AGENT_CORE_LLM_ROLES__COOKING__MODEL 单独指定模型（如更便宜的小模型）
COOKING_ROLE = "cooking"

COOKING_DESCRIPTION = (
    "烹饪助手：按口味、食材、菜系或难度推荐菜谱，并讲解用料与做法步骤"
)

# Layer1 意图路由语料：语义路由用它们与用户输入算相似度，命中即委托本 Agent。
# 覆盖「找菜」「问做法」「问食材」「按条件筛」四类典型说法；
# 语料为空会导致该 Agent 完全不参与路由，所以宁可多写几条同义表达。
COOKING_UTTERANCES: tuple[str, ...] = (
    "今天吃什么",
    "有什么好吃的推荐",
    "推荐几个家常菜",
    "我想吃川菜",
    "用鸡蛋能做什么菜",
    "这道菜怎么做",
    "红烧肉的做法是什么",
    "宫保鸡丁需要哪些食材",
    "番茄炒蛋要放多少盐",
    "有没有适合新手的简单菜谱",
    "做一道低脂的菜",
    "半小时能做完的菜有哪些",
    "这个菜要煮多久",
    "帮我看看这个菜谱的步骤",
)


def _create_model(settings: AgentCoreSettings) -> BaseChatModel:
    """按 ``cooking`` 角色取模型；失败即降级到离线模型（含原因日志）。"""
    try:
        return create_chat_model(settings, role=COOKING_ROLE)
    except AgentCoreError as exc:
        # 只记原因不记密钥：异常信息由 agent-core 生成，本身已做脱敏
        logger.warning("cooking 角色模型不可用，降级为离线模型：%s", exc)
        return OfflineCookingModel()


def build_cooking_agent(
    settings: AgentCoreSettings | None = None,
    *,
    chat_model: BaseChatModel | None = None,
    store: RecipeStore | None = None,
    tools: list[BaseTool] | None = None,
    cooking_settings: CookingSettings | None = None,
) -> VerticalAgent:
    """构建 cooking 垂直 Agent 插槽。

    各依赖都可显式注入，便于宿主与测试替换实现：

    :param settings: agent-core 配置（决定模型怎么连）
    :param chat_model: 聊天模型；不给则按 ``cooking`` 角色解析，失败降级离线
    :param store: 菜谱数据源；不给则走 HTTP（Java API）
    :param tools: 工具集；不给则由 store 装配三个菜谱工具
    :param cooking_settings: 菜谱数据源配置（接口地址、超时、条数上限）
    """
    core_settings = settings or AgentCoreSettings()
    cooking_config = cooking_settings or CookingSettings()
    model = chat_model or _create_model(core_settings)
    recipe_store = store or HttpRecipeStore(cooking_config)
    tool_list = tools if tools is not None else build_recipe_tools(recipe_store, cooking_config)
    return VerticalAgent(
        name=COOKING_AGENT_NAME,
        description=COOKING_DESCRIPTION,
        graph=build_cooking_graph(model, tool_list),
        utterances=COOKING_UTTERANCES,
        metadata={"role": COOKING_ROLE, "api_base_url": cooking_config.api_base_url},
    )
