"""言外（EchoTalk）垂直 Agent 的配置。

与 agent-core 的配置分离：agent-core 管「模型怎么连」，这里管
「结构化结果回写到哪里」。前缀 ``TALK_``，与 ``AGENT_CORE_*``、
``COOKING_*``、宿主 ``PY_SERVER_*`` 共用同一个 ``.env`` 文件但互不干扰。

不在这里放 LLM 相关字段：模型走 agent-core 的角色槽位机制
（本 Agent 用 ``talk`` 角色，见 agent.py），避免两套模型配置并存。
"""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class TalkSettings(BaseSettings):
    """建议落库与降级行为的配置。

    ``api_base_url`` 指向 Spring Boot（含 /api 前缀）。容器部署时由
    ``TALK_API_BASE_URL`` 覆盖为内部服务名（compose 里是 http://api:8080/api）。
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="TALK_",
        extra="ignore",
    )

    # 回调落库地址：POST {api_base_url}/talk/internal/suggestions
    api_base_url: str = "http://localhost:8080/api"
    # 与 Spring 侧 app.internal-token 一致；两端不一致时落库会被 403 拒绝
    internal_token: str = ""
    request_timeout_seconds: float = 5.0
    # 关闭后只在内存里跑分析、不回写（本地无后端时便于自测）
    persist_enabled: bool = True
    # 每次调模型回灌的历史条数上限（段级触发下不需要很长）
    history_limit: int = 12
