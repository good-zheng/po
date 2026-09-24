"""离线降级模型。

「LLM 或网络依赖必须保留离线或失败降级路径」——装配期若拿不到 cooking
角色的模型（缺 key、provider 配错等），整个垂直 Agent 不能因此让宿主
起不来。这里用一个确定性模型顶上：它不发网络请求，靠输入文本的哈希
在预置话术里取样，保证同样的提问得到同样的回答（可测试、可复现）。

能力上是真·降级：**不做工具调用**（``bind_tools`` 直接返回自身），
所以 ReAct 循环会在 ``agent_node`` 一步收尾，用户会看到一句明确的
「当前为离线模式」而不是一个假装在查菜谱的空壳。
"""

from __future__ import annotations

import hashlib
from typing import Any, Sequence

from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.outputs import ChatGeneration, ChatResult

OFFLINE_TAG = "【离线模式】"

# 预置话术：都指向「去找真模型」这一件事，不给用户「它答不上来」的错觉
_OFFLINE_REPLIES: tuple[str, ...] = (
    "我现在处于离线模式，接不上菜谱库也连不上大模型，暂时没法帮你挑菜或讲做法。"
    "等网络或模型配置恢复后我就能正常推荐了。",
    "当前是离线模式，查菜谱的能力没有启用。你可以先到菜谱页按分类逛逛，"
    "等我这边的模型接上再回来问我。",
    "离线模式下的我没法检索菜谱。配置好 AGENT_CORE_LLM_API_KEY 后重启聊天服务，"
    "我就能按口味、食材和时长帮你推荐了。",
)


def _message_text(message: BaseMessage) -> str:
    """取一条消息的纯文本：content 可能是 str，也可能是多模态片段列表。"""
    content = message.content
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and isinstance(block.get("text"), str):
                parts.append(block["text"])
        return "\n".join(parts)
    return str(content)


class OfflineCookingModel(BaseChatModel):
    """离线占位模型：确定性应答，不发起任何网络调用。"""

    @property
    def _llm_type(self) -> str:
        return "offline-cooking-model"

    def bind_tools(self, tools: Sequence[Any], **kwargs: Any) -> "OfflineCookingModel":
        """返回自身：不产生 tool_calls，ReAct 循环一步到 END。

        方法签名对齐 BaseChatModel，``tools`` 无需拆包——离线模式本就不调工具。
        """
        return self

    def _reply_for(self, messages: list[BaseMessage]) -> str:
        """按最后一条消息的内容哈希确定性选话术。"""
        text = _message_text(messages[-1]) if messages else ""
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        reply = _OFFLINE_REPLIES[digest[0] % len(_OFFLINE_REPLIES)]
        return f"{OFFLINE_TAG}{reply}"

    def _generate(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager: CallbackManagerForLLMRun | None = None,
        **kwargs: Any,
    ) -> ChatResult:
        return ChatResult(
            generations=[ChatGeneration(message=AIMessage(content=self._reply_for(messages)))]
        )

    async def _agenerate(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager: CallbackManagerForLLMRun | None = None,
        **kwargs: Any,
    ) -> ChatResult:
        # 无 IO，直接复用同步实现；覆盖它以避开基类默认的线程池包装
        return self._generate(messages, stop, run_manager, **kwargs)
