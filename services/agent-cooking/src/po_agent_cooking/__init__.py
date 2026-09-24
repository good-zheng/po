"""po-agent-cooking：po 的烹饪助手垂直 Agent。

对外只有一个入口 :func:`build_cooking_agent`——宿主（``services/chat``）
在 ``_builtin_agents`` 里调用它并登记返回的 :class:`VerticalAgent`，
之后由 supervisor 按 Layer1 意图路由决定是否委托。

菜谱数据来自 Java 菜谱接口（``GET /recipes`` 系列为 permitAll 公开读），
模型走 agent-core 的 ``cooking`` 角色槽位；两者都可在装配时替换，
见 :mod:`po_agent_cooking.agent`。
"""

__version__ = "0.1.0"

from po_agent_cooking.agent import (
    COOKING_AGENT_NAME,
    COOKING_DESCRIPTION,
    COOKING_ROLE,
    COOKING_UTTERANCES,
    build_cooking_agent,
)
from po_agent_cooking.config import CookingSettings
from po_agent_cooking.graph import build_cooking_graph
from po_agent_cooking.offline import OFFLINE_TAG, OfflineCookingModel
from po_agent_cooking.recipes import (
    HttpRecipeStore,
    MockRecipeStore,
    RecipeBrief,
    RecipeCategory,
    RecipeDetail,
    RecipeIngredient,
    RecipeStep,
    RecipeStore,
    RecipeStoreError,
)
from po_agent_cooking.tools import build_recipe_tools

__all__ = [
    "__version__",
    # 装配入口
    "build_cooking_agent",
    "COOKING_AGENT_NAME",
    "COOKING_ROLE",
    "COOKING_DESCRIPTION",
    "COOKING_UTTERANCES",
    # 配置
    "CookingSettings",
    # 子图
    "build_cooking_graph",
    # 离线降级
    "OfflineCookingModel",
    "OFFLINE_TAG",
    # 数据层
    "RecipeStore",
    "RecipeStoreError",
    "HttpRecipeStore",
    "MockRecipeStore",
    "RecipeBrief",
    "RecipeDetail",
    "RecipeIngredient",
    "RecipeStep",
    "RecipeCategory",
    # 工具
    "build_recipe_tools",
]
