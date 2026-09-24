"""cooking 垂直 Agent 的配置。

与 agent-core 的配置分离：agent-core 管「模型怎么连」，这里管
「菜谱数据从哪里读」。前缀 ``COOKING_``，与 ``AGENT_CORE_*``、
宿主 ``PY_SERVER_*`` 共用同一个 ``.env`` 文件但互不干扰。

不在这里放 LLM 相关字段：模型走 agent-core 的角色槽位机制
（本 Agent 用 ``cooking`` 角色，见 agent.py），避免两套模型配置并存。
"""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class CookingSettings(BaseSettings):
    """菜谱数据源配置。

    默认值指向本地 Spring Boot 服务（``pnpm api:start`` 的 8080），
    容器部署时由 ``COOKING_API_BASE_URL`` 覆盖为内部服务名。
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="COOKING_",
        extra="ignore",
    )

    # 菜谱接口根地址（含 /api 前缀）：Java 侧 GET /recipes 等读接口
    # 是 permitAll 的，Agent 无需持有用户令牌即可查询公开菜谱
    api_base_url: str = "http://localhost:8080/api"
    # 单次请求超时；工具失败会被翻译成可读文本回给模型，不中断整轮对话
    request_timeout_seconds: float = 10.0
    # 单次检索返回给模型的菜谱条数上限（越大上下文越长、越慢）
    search_limit: int = 5
