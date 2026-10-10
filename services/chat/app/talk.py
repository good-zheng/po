"""言外（talk 插槽）结果的回写钩子。

职责边界：:mod:`app.routers.ws` 只做协议翻译，不该知道「talk 的输出是 JSON、
要回写到哪个地址」。这里把这部分领域知识收在一处：判断本轮是不是 talk、
把模型输出解析成 :class:`TalkAnalysis`、再交给 ``po_agent_talk.persist_suggestion``。

**任何失败都只记日志**：建议已经随 token 帧发给用户了，回写失败只影响
「历史里能不能再看到」，绝不能让本轮对话在 WS 上以 error 收尾。
"""

from __future__ import annotations

import logging
from typing import Any

from po_agent_core import AgentCoreSettings

logger = logging.getLogger(__name__)

# 与 po_agent_talk.TALK_AGENT_NAME 保持一致；这里不直接 import 该包，
# 因为未安装 agent-talk 时（纯 chitchat 部署）本模块仍需可导入
TALK_AGENT = "talk"


def _model_name(settings: AgentCoreSettings | None) -> str:
    """取当前模型标识用于事后归因；拿不到就留空。"""
    llm = getattr(settings, "llm", None)
    return str(getattr(llm, "model", "") or "")


async def persist_talk_result(
    *,
    agent: str | None,
    context: dict[str, Any] | None,
    conversation_id: str,
    output: str,
    settings: AgentCoreSettings | None = None,
    latency_ms: int | None = None,
) -> None:
    """把 talk 插槽本轮的结构化结果回写 Spring Boot。

    :param agent: 本轮实际使用的插槽名；不是 ``talk`` 直接返回
    :param context: 入站帧携带的上下文，其中 ``utteranceId`` 用于定位话语
    :param conversation_id: thread_id，作为 utteranceId 缺失时的兜底定位
    :param output: 本轮 token 拼接后的完整模型输出
    """
    if agent != TALK_AGENT:
        return
    try:
        from po_agent_talk import parse_analysis, persist_suggestion
    except ImportError as exc:
        logger.info("未安装 po-agent-talk，跳过建议落库：%s", exc)
        return

    analysis = parse_analysis(output)
    if analysis is None:
        logger.warning("言外输出不是合法 JSON，跳过落库：%.120s", output)
        return

    ctx = context or {}
    try:
        ok = await persist_suggestion(
            analysis,
            utterance_id=ctx.get("utteranceId"),
            thread_id=conversation_id,
            model=_model_name(settings),
            latency_ms=latency_ms,
        )
        if not ok:
            logger.info("言外建议落库未成功（详见 po_agent_talk 日志）")
    except Exception as exc:  # 兜住所有意外，落库失败绝不能影响对话本身
        logger.warning("言外建议落库异常（已忽略）：%s", exc)
