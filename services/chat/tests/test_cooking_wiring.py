"""cooking 插槽在 chat 宿主的登记与端到端接线。

覆盖两件事：

1. ``_builtin_agents`` 的登记契约——装上 po-agent-cooking 时恰好登记一个
   ``cooking`` 插槽；包缺失或装配抛错时只跳过本插槽，宿主照常启动（用户
   仍能拿到 chitchat 兜底），这是「垂直 Agent 起不来不该拖垮聊天服务」
   这条降级策略的验证点；
2. 从 WS 帧到菜谱工具的完整链路——用户原话命中 Layer1 语料 → supervisor
   委托 cooking 子图 → ReAct 调工具 → 工具结果以 ``tool_call_result`` 帧
   下发 → 模型把结果转成最终答复。

无 Key 环境下 ``create_intent_router`` 会降级为 ``KeywordIntentRouter``
（bigram 覆盖率），因此这里用「与语料逐字相同」的输入锁定路由结果，
不依赖 embedding 服务，测试完全离线。
"""

from __future__ import annotations

import asyncio
import json
import sys

import pytest
from fastapi.testclient import TestClient
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.outputs import ChatGeneration, ChatResult

from app.agent import _builtin_agents, build_orchestrator
from app.main import create_app
from po_agent_core import AgentCoreSettings
from po_agent_cooking import (
    COOKING_AGENT_NAME,
    COOKING_UTTERANCES,
    MockRecipeStore,
    build_cooking_agent,
)

# 与 COOKING_UTTERANCES 逐字相同：KeywordIntentRouter 对原文命中给满分，
# 保证这条用例在任何 embedding 配置下都稳定路由到 cooking。
ROUTABLE_TEXT = "番茄炒蛋要放多少盐"


def offline_settings() -> AgentCoreSettings:
    """无 Key / 内存 checkpointer 的隔离配置：不读 .env、不连 redis。"""
    return AgentCoreSettings(
        _env_file=None, checkpointer="memory", llm_api_key="", router_threshold=1.0
    )


# ---------- 插槽登记 ----------


def test_builtin_agents_registers_cooking() -> None:
    agents = _builtin_agents(offline_settings())

    assert [agent.name for agent in agents] == [COOKING_AGENT_NAME]
    cooking = agents[0]
    assert cooking.utterances == COOKING_UTTERANCES
    assert cooking.description, "description 是 AgentCard 与路由语料的共同来源，不能为空"


def test_builtin_agents_skips_missing_package(monkeypatch: pytest.MonkeyPatch) -> None:
    # sys.modules 里置 None 是 CPython 表达「该模块不可导入」的标准手法，
    # 比真的卸载包更干净：函数内的延迟导入会抛 ImportError。
    monkeypatch.setitem(sys.modules, "po_agent_cooking", None)

    assert _builtin_agents(offline_settings()) == []


def test_builtin_agents_skips_failed_assembly(monkeypatch: pytest.MonkeyPatch) -> None:
    def boom(*args, **kwargs):
        raise RuntimeError("模拟插槽装配失败")

    monkeypatch.setattr("po_agent_cooking.build_cooking_agent", boom)

    # 装配异常被吞掉并记日志：返回空列表而非上抛，宿主启动不受影响
    assert _builtin_agents(offline_settings()) == []


def test_slot_registration_is_importable_by_default() -> None:
    """默认配置（无任何 Key）下登记也不能抛错——离线模型负责兜底。"""
    agents = _builtin_agents(AgentCoreSettings(_env_file=None, llm_api_key=""))
    assert len(agents) == 1


# ---------- 端到端：WS 帧 → 路由 → 子图 → 工具 → 帧 ----------


def _chat_result(message: AIMessage) -> ChatResult:
    return ChatResult(generations=[ChatGeneration(message=message)])


class RecipeToolModel(BaseChatModel):
    """两轮脚本模型：第一轮订菜谱检索工具，第二轮把工具结果转成口头答复。

    ``bind_tools`` 必须返回自身（基类默认抛 NotImplementedError），这是
    与真实 ChatOpenAI 行为对齐的最小替身。
    """

    @property
    def _llm_type(self) -> str:
        return "recipe-tool-model"

    def bind_tools(self, tools, **kwargs):  # noqa: ANN001, ANN003 - 对齐基类签名
        return self

    def _reply(self, messages: list) -> ChatResult:
        if isinstance(messages[-1], ToolMessage):
            return _chat_result(AIMessage(content="给你推荐番茄炒蛋"))
        return _chat_result(
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "search_recipes",
                        "args": {"keyword": "番茄"},
                        "id": "call-recipe-1",
                        "type": "tool_call",
                    }
                ],
            )
        )

    def _generate(self, messages, stop=None, run_manager=None, **kwargs) -> ChatResult:
        return self._reply(messages)

    async def _agenerate(self, messages, stop=None, run_manager=None, **kwargs) -> ChatResult:
        return self._reply(messages)


class PlainReplyModel(BaseChatModel):
    """chitchat 兜底用的纯文本模型：不产生工具调用，便于断言「未委托」。"""

    @property
    def _llm_type(self) -> str:
        return "plain-reply-model"

    def _generate(self, messages, stop=None, run_manager=None, **kwargs) -> ChatResult:
        return _chat_result(AIMessage(content="今天天气不错，适合在家做饭"))

    async def _agenerate(self, messages, stop=None, run_manager=None, **kwargs) -> ChatResult:
        return _chat_result(AIMessage(content="今天天气不错，适合在家做饭"))


def build_ws_client() -> TestClient:
    """装配「脚本模型 + 内存菜谱」的宿主实例：不连 LLM、不连 Java API。

    这里显式注入插槽而不是走 ``agents=None`` 的默认路径：默认路径已由上面的
    登记用例覆盖，此处要锁定的是「路由命中后帧序列长什么样」。chitchat 与
    cooking 用两个不同的替身，未命中时才能干净地断言「没有工具帧」。
    """
    cooking_model = RecipeToolModel()
    cooking = build_cooking_agent(
        offline_settings(), chat_model=cooking_model, store=MockRecipeStore()
    )
    orchestrator = asyncio.run(
        build_orchestrator(
            offline_settings(), chat_model=PlainReplyModel(), agents=[cooking]
        )
    )
    return TestClient(create_app(orchestrator=orchestrator))


def drain_until_done(websocket) -> tuple[str, list[dict]]:  # noqa: ANN001 - TestClient ws
    """收帧直到 done：返回 (token 拼接, 全部帧)。"""
    tokens = ""
    frames: list[dict] = []
    while True:
        frame = websocket.receive_json()
        frames.append(frame)
        if frame["type"] == "token":
            tokens += frame["content"]
        elif frame["type"] == "done":
            return tokens, frames
        elif frame["type"] == "error":
            pytest.fail(f"unexpected error frame: {frame}")


def test_ws_message_routes_to_cooking_and_returns_recipe_frames() -> None:
    client = build_ws_client()

    with client.websocket_connect("/ws/chat") as websocket:
        websocket.send_json({"type": "message", "content": ROUTABLE_TEXT})
        tokens, frames = drain_until_done(websocket)

    types = [frame["type"] for frame in frames]
    assert types[0] == "run_started"
    assert types[-1] == "done"

    # 路由确实走到了垂直 Agent：step 帧的 node 出现子图名（chitchat 未参与）
    nodes = [f["payload"]["node"] for f in frames if f["type"] == "step"]
    assert "route" in nodes
    assert COOKING_AGENT_NAME in nodes
    assert "chitchat" not in nodes

    # 工具调用：start（工具名）→ result（工具输出原文）
    starts = [f for f in frames if f["type"] == "tool_call_start"]
    assert [f["payload"]["name"] for f in starts] == ["search_recipes"]

    results = [f for f in frames if f["type"] == "tool_call_result"]
    assert len(results) == 1
    assert results[0]["payload"]["name"] == "search_recipes"
    assert results[0]["payload"]["status"] == "success"
    payload = json.loads(results[0]["content"])
    assert [item["title"] for item in payload["recipes"]] == ["番茄炒蛋"]

    # 最终答复：模型读工具结果后吐字，token 帧按序拼接
    assert "番茄炒蛋" in tokens


def test_ws_chitchat_when_no_cooking_hit() -> None:
    """语料未命中时委托不发生：仍由 chitchat 兜底，且不产生工具帧。

    输入刻意选与菜谱语料零 bigram 重叠的闲聊（字面含「今天」会命中
    「今天吃什么」的覆盖率阈值，故不能用日常寒暄短句当反例）。
    """
    client = build_ws_client()

    with client.websocket_connect("/ws/chat") as websocket:
        websocket.send_json({"type": "message", "content": "讲个笑话吧"})
        tokens, frames = drain_until_done(websocket)

    tool_frames = [f["payload"]["name"] for f in frames if f["type"] == "tool_call_start"]
    assert tool_frames == []
    nodes = [f["payload"]["node"] for f in frames if f["type"] == "step"]
    assert "chitchat" in nodes
    assert COOKING_AGENT_NAME not in nodes
    assert tokens == "今天天气不错，适合在家做饭"
