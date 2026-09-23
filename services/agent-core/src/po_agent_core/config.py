"""agent-core 全局配置。

配置按用途分五组：LLM 连接、embedding（决策层用）、记忆（checkpointer）、
路由阈值、运行时超时。环境变量前缀 ``AGENT_CORE_``，与宿主自身配置
（如 chat 的 ``PY_SERVER_*``）共用同一个 ``.env`` 文件、互不干扰。

多模型：``AGENT_CORE_LLM_*`` 是「默认槽位」，所有未被角色覆盖的调用都落在
它上面；需要按阶段换模型时用 ``AGENT_CORE_LLM_ROLES__<角色>__<字段>``
声明覆盖槽位（见 :class:`ModelSlot`）。未声明的角色一律回落默认槽位，
于是「不配就是单模型」——多模型是增量配置，不是必答题。

设计取舍：配置只描述「用户想怎么配」，不负责校验连通性；
缺 key / 连不上等失败一律留给调用方（宿主装配层）决定降级策略。
"""

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class ModelRole(StrEnum):
    """模型角色：一次 LLM 调用的「用途」标签，也是 ``llm_roles`` 的键。

    这是推荐词汇而非封闭集合——``llm_roles`` 接受任意小写角色名，
    垂直 Agent 可声明自己的角色；列在这里的几个是核心与内置 Agent 实际
    用到的，写成常量是为了让环境变量名有据可查、避免各处硬编码字符串。
    """

    CHAT = "chat"  # 闲聊兜底、轻量问答
    PLAN = "plan"  # 构思、大纲、任务拆解等规划类调用
    WRITE = "write"  # 长文本正文生成
    JUDGE = "judge"  # 评审、打分、结构化抽取等判定类调用


class ModelSlot(BaseModel):
    """单个角色槽位的模型覆盖项：未填的字段回落默认槽位。

    环境变量写法（``ROLES`` 与角色、角色与字段之间用双下划线分隔）::

        AGENT_CORE_LLM_ROLES__WRITE__MODEL=qwen-max
        AGENT_CORE_LLM_ROLES__JUDGE__PROVIDER=deepseek
        AGENT_CORE_LLM_ROLES__JUDGE__API_KEY=...

    角色名不区分大小写（pydantic-settings 统一转小写后作键）。
    例外：跨 provider 时 ``api_key`` 不回落默认槽位——把 A 家的密钥发往
    B 家是错误而非便利，缺角色密钥会直接报错并指明该配哪个变量。
    """

    provider: str = ""  # 空 = 沿用默认槽位的 provider
    model: str = ""  # 空 = 该 provider 的预设模型
    api_key: str = ""  # 空 = 同 provider 时复用默认槽位密钥
    base_url: str = ""  # 空 = 该 provider 的预设 base_url
    temperature: float | None = None  # None = 沿用默认槽位的温度


class AgentCoreSettings(BaseSettings):
    """agent-core 全局配置。

    环境变量前缀 ``AGENT_CORE_``，亦从宿主工作目录的 ``.env`` 读取
    （与 chat 服务的 ``PY_SERVER_*`` 共用同一文件）。
    核心 API 以显式参数接收 settings，不读全局单例；本类的便捷性
    实例化只发生在宿主装配层。
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="AGENT_CORE_",
        extra="ignore",
        # dict 型字段（llm_roles）无法用单个扁平变量表达，双下划线是
        # pydantic-settings 约定的层级分隔符：``AGENT_CORE_LLM_ROLES__WRITE__MODEL``
        # 即解析为 llm_roles["write"].model。现有扁平变量无 ``__``，不受影响。
        env_nested_delimiter="__",
    )

    # ---------- LLM（OpenAI 兼容协议） ----------
    # 以下为「默认槽位」：所有未被 llm_roles 覆盖的角色调用都走这里，
    # 单模型部署只需配这一段。
    llm_provider: Literal["qwen", "deepseek", "openai", "custom"] = "qwen"
    llm_model: str = ""  # 空 = provider 预设
    llm_api_key: str = ""
    llm_base_url: str = ""  # 空 = provider 预设
    llm_temperature: float = 0.7
    # 超时与重试属传输层参数，对所有角色统一生效，不做分角色配置
    llm_timeout_seconds: float = 120.0
    llm_max_retries: int = 2
    # 角色槽位覆盖（键为角色名，见 ModelRole）。空 = 全部角色走默认槽位。
    llm_roles: dict[str, ModelSlot] = {}

    # ---------- Embedding（semantic-router 决策层用） ----------
    embedding_model: str = ""  # 空 = provider 预设；仍为空则路由层降级
    embedding_api_key: str = ""  # 空 = 回退 llm_api_key
    embedding_base_url: str = ""  # 空 = 回退 llm_base_url → provider 预设
    embedding_dimensions: int = 1024

    # ---------- 记忆 ----------
    checkpointer: Literal["redis", "sqlite", "memory"] = "redis"
    redis_url: str = "redis://localhost:6379"
    sqlite_path: str = ".agent-core/checkpoints.sqlite"

    # ---------- 路由 ----------
    # HybridRouter 分数 = 稠密余弦(≈0~1) + BM25 稀疏分(关键词命中可达 3+)，
    # 故默认阈值取 1.0：强命中通过，弱相关/无关落兜底
    router_threshold: float = 1.0

    # ---------- 运行时 ----------
    # 单次 AgentRunner 运行的总预算：超时由 runner 翻译成 RUN_ERROR 事件，
    # 避免前端一直等不到 done
    run_timeout_seconds: float = 300.0
