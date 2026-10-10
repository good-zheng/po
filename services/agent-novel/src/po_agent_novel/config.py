"""小说垂直 Agent 的数据层配置。

与 agent-core 的配置分离：agent-core 管「模型怎么连」，这里管
「成稿与正典写到哪里」。前缀 ``NOVEL_``，与 ``AGENT_CORE_*``、``TALK_*``、
``COOKING_*`` 共用同一个 ``.env`` 但互不干扰。

不放 LLM 字段：阶段模型走 agent-core 的角色槽位（plan / write / judge）。
"""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class NovelStoreSettings(BaseSettings):
    """内网通道落库配置。

    ``api_base_url`` 指向 Spring Boot（含 /api 前缀）；容器部署时由
    ``NOVEL_API_BASE_URL`` 覆盖为内部服务名（compose 里是 http://api:8080/api）。
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="NOVEL_",
        extra="ignore",
    )

    api_base_url: str = "http://localhost:8080/api"
    # 与 Spring 侧 app.internal-token 一致；两端不一致时写入会被 403 拒绝
    internal_token: str = ""
    # 内部通道建书要落到某个用户名下（book.author_id NOT NULL）。
    # 归档发起人此刻还进不到这条链路（对话面板传 author 上下文是 N5c 的事），
    # 先用配置兜底，别让「写不进去」伪装成「模型没产出」。
    author_id: int = 1
    request_timeout_seconds: float = 30.0
    # 写库失败必须重试且有终态：整本成稿只落一次库，一次网络抖动就丢书是不可接受的
    max_retries: int = 3
    retry_backoff_seconds: float = 1.5
    # 关闭后走进程内内存实现（本地无后端时便于自测与跑离线回归）
    persist_enabled: bool = True
