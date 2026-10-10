"""把结构化结果回写 Spring Boot（chat 服务 → API 的内网回调）。

链路与 agent-cooking 调菜谱接口同构：Python 侧持有内网地址与令牌，
Java 侧的 ``/talk/internal/suggestions`` 由 ``X-Internal-Token`` 保护。

**落库失败不抛异常**：建议已经发给用户了，回写失败只影响「历史里能不能
再看到」，不应该让整轮对话在 WS 层变成 error 帧。这里统一记日志返回 bool，
由调用方决定是否告警。
"""

from __future__ import annotations

import logging
from typing import Any

import httpx

from po_agent_talk.config import TalkSettings
from po_agent_talk.schema import TalkAnalysis

logger = logging.getLogger(__name__)


async def persist_suggestion(
    analysis: TalkAnalysis,
    *,
    utterance_id: int | str | None = None,
    thread_id: str | None = None,
    model: str = "",
    latency_ms: int | None = None,
    settings: TalkSettings | None = None,
    client: httpx.AsyncClient | None = None,
) -> bool:
    """回写一轮建议；返回是否成功。

    :param analysis: 已解析通过的结构化结果
    :param utterance_id: 目标话语 id（优先定位方式）
    :param thread_id: 会话 thread_id；utterance_id 缺失时的兜底定位
    :param model: 模型标识，用于事后归因
    :param latency_ms: 端到端耗时，落库便于观测
    :param settings: 落库配置；缺省读取环境变量
    :param client: 可注入的 httpx 客户端（测试用）
    """
    config = settings or TalkSettings()
    if not config.persist_enabled:
        logger.info("言外建议落库已关闭（TALK_PERSIST_ENABLED=false），跳过回写")
        return False
    if not config.internal_token:
        logger.info("未配置 TALK_INTERNAL_TOKEN，跳过建议落库")
        return False
    if utterance_id is None and not thread_id:
        logger.info("缺少 utterance_id 与 thread_id，跳过建议落库")
        return False

    payload: dict[str, Any] = analysis.to_dict()
    payload["utteranceId"] = utterance_id
    payload["threadId"] = thread_id
    payload["model"] = model
    payload["latencyMs"] = latency_ms

    url = f"{config.api_base_url.rstrip('/')}/talk/internal/suggestions"
    headers = {
        "Content-Type": "application/json",
        "X-Internal-Token": config.internal_token,
    }

    own_client = client is None
    http = client or httpx.AsyncClient(timeout=config.request_timeout_seconds)
    try:
        response = await http.post(url, json=payload, headers=headers)
        if response.status_code >= 400:
            logger.warning(
                "言外建议落库失败：HTTP %s %s", response.status_code, response.text[:200]
            )
            return False
        return True
    except httpx.HTTPError as exc:
        # 网络类异常（后端未启动、DNS、超时）：只记日志，不阻断对话
        logger.warning("言外建议落库异常（已忽略）：%s", exc)
        return False
    finally:
        if own_client:
            await http.aclose()
