"""测试夹具与假模型。

关键点一：清空 ``AGENT_CORE_*`` / ``COOKING_*`` 环境变量。agent-core 的
semantic-router 路径会调 ``load_dotenv()``，它会沿调用栈向上找到
``services/chat/.env`` 并把里面的密钥灌进 ``os.environ``——开发者本机
那份 ``.env`` 一旦被读到，测试就会偷偷连上真实模型，既慢又不稳定。
本包不依赖 semantic-router，但同一个 venv 里它已被加载，所以仍需防御。

关键点二：:class:`ScriptedChatModel`。LangChain 自带的 ``GenericFakeChatModel``
不支持 ``bind_tools``（基类默认抛 NotImplementedError），而本 Agent 的
子图一定会绑定工具，所以自备一个「按脚本返回 + 记录收到的提示」的假模型。
"""

from __future__ import annotations

import asyncio
import os
from typing import Any, Callable

import pytest
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage
from langchain_core.outputs import ChatGeneration, ChatResult

_ENV_PREFIXES = ("AGENT_CORE_", "COOKING_")


@pytest.fixture(autouse=True)
def _isolate_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in list(os.environ):
        if key.startswith(_ENV_PREFIXES):
            monkeypatch.delenv(key, raising=False)


class ScriptedChatModel(BaseChatModel):
    """按脚本逐轮返回消息的假模型。

    ``replies`` 用尽后重复最后一条，方便「一直回答同一句」的用例；
    ``seen`` 记录每次调用收到的完整提示，用于断言系统提示注入与窗口裁剪。
    """

    replies: list[AIMessage]
    seen: list[list[Any]] = []

    @property
    def _llm_type(self) -> str:
        return "scripted-test-model"

    def bind_tools(self, tools: Any, **kwargs: Any) -> "ScriptedChatModel":
        # 不改变返回值：脚本里写什么就返回什么，工具绑定对断言无影响
        return self

    def _generate(
        self,
        messages: list[Any],
        stop: list[str] | None = None,
        run_manager: Any = None,
        **kwargs: Any,
    ) -> ChatResult:
        self.seen.append(list(messages))
        index = min(len(self.seen) - 1, len(self.replies) - 1)
        return ChatResult(generations=[ChatGeneration(message=self.replies[index])])

    async def _agenerate(
        self,
        messages: list[Any],
        stop: list[str] | None = None,
        run_manager: Any = None,
        **kwargs: Any,
    ) -> ChatResult:
        return self._generate(messages, stop, run_manager, **kwargs)


@pytest.fixture
def make_scripted_model() -> Callable[[list[AIMessage]], ScriptedChatModel]:
    """工厂夹具：``make_scripted_model([AIMessage(content="...")])``。"""

    def _make(replies: list[AIMessage]) -> ScriptedChatModel:
        return ScriptedChatModel(replies=replies, seen=[])

    return _make


def run(coro: Any) -> Any:
    """跑一个协程（子图节点是 async 的，只能用 ainvoke/astream 驱动）。"""
    return asyncio.run(coro)
