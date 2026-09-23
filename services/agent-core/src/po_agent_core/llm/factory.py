"""LLM / Embedding 工厂。

参考实现（novel_server）的教训：`QwenLlm()` 在 4 个文件各实例化一次、
env 读取与客户端构建散落各处、provider 切换靠注释代码。这里收敛为唯一入口：

- provider 预设（base_url / 默认模型 / embedding 预设）集中声明；
- 解析优先级：显式参数 > 角色槽位（``llm_roles``） > 环境配置（``AGENT_CORE_*``）
  > provider 预设；
- 多模型按「角色」而非按调用点解析：调用方只说自己是哪类用途
  （plan / write / judge…），由配置决定该用途落到哪个模型；未配置的角色
  一律回落默认槽位，即「不配就是单模型」；
- API Key 缺失立即抛错并指明环境变量名，绝不静默降级、绝不记录密钥。
"""

from __future__ import annotations

from dataclasses import dataclass

from langchain_core.embeddings import Embeddings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from po_agent_core.config import AgentCoreSettings
from po_agent_core.errors import AgentCoreConfigError

# provider 预设是「默认值」而不是「唯一来源」：任何一项都可以被显式参数或
# AGENT_CORE_* 环境变量覆盖。新增 provider 只需在这里加一行。
PROVIDER_PRESETS: dict[str, dict[str, str]] = {
    "qwen": {
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "model": "qwen-plus",
        "embedding_model": "text-embedding-v4",
    },
    "deepseek": {
        "base_url": "https://api.deepseek.com/v1",
        "model": "deepseek-chat",
        "embedding_model": "",  # DeepSeek 无 embedding 接口，需单独配置其他 provider
    },
    "openai": {
        "base_url": "",
        "model": "gpt-4o-mini",
        "embedding_model": "text-embedding-3-small",
    },
    "custom": {
        "base_url": "",
        "model": "",
        "embedding_model": "",
    },
}


@dataclass(frozen=True, slots=True)
class ResolvedLLM:
    model: str
    api_key: str
    base_url: str
    temperature: float
    timeout_seconds: float
    max_retries: int


def _preset(provider: str, *, role: str = "") -> dict[str, str]:
    """取 provider 预设；未知 provider 立即报错。

    ``role`` 仅用于报错上下文：角色槽位里的 provider 是自由字符串（不像
    settings.llm_provider 受 Literal 约束），点明角色能直接定位到那行配置。
    """
    preset = PROVIDER_PRESETS.get(provider)
    if preset is None:
        where = f"角色 {role!r} 声明的 provider" if role else "llm_provider"
        raise AgentCoreConfigError(
            f"未知的 {where}: {provider!r}，可选：{', '.join(sorted(PROVIDER_PRESETS))}"
        )
    return preset


def _normalize_role(role: str | None) -> str:
    """角色名归一化：大小写不敏感。

    环境变量形式（``AGENT_CORE_LLM_ROLES__WRITE__MODEL``）经 pydantic-settings
    解析后键已是小写，这里再归一化一次是为了兼容直接构造 settings 或传
    ``ModelRole`` 枚举的场景。
    """
    return role.strip().lower() if role else ""


def _role_env(role: str, field: str) -> str:
    """拼出角色槽位对应的环境变量名，让报错直接告诉用户「该配哪个变量」。"""
    return f"AGENT_CORE_LLM_ROLES__{role.upper()}__{field}"


def resolve_llm(
    settings: AgentCoreSettings | None = None,
    *,
    role: str | None = None,
    model: str | None = None,
    api_key: str | None = None,
    base_url: str | None = None,
    temperature: float | None = None,
) -> ResolvedLLM:
    """解析 LLM 连接参数（纯函数，不做网络请求）。

    优先级统一为「显式参数 > 角色槽位 > 环境配置 > provider 预设」，
    缺 key / 缺模型名时立刻抛 :class:`AgentCoreConfigError`——
    由调用方（宿主装配层）决定是降级还是中断启动。

    :param role: 模型角色（见 ``config.ModelRole``）。传 None 或该角色未配
        槽位时完全等价于单模型（全部字段取自默认槽位）。角色槽位声明了
        **不同** provider 时，默认槽位的模型名 / 网关 / 密钥一概不继承
        ——把 A 家的密钥发往 B 家是错误而非便利，此时缺 key 会报错并
        指明该配哪个角色专属变量。
    """
    settings = settings or AgentCoreSettings()
    role_name = _normalize_role(role)
    slot = settings.llm_roles.get(role_name) if role_name else None
    # provider 决定预设与「能否继承默认槽位」：槽位没写 provider 即沿用默认槽位。
    provider = (slot.provider or settings.llm_provider) if slot else settings.llm_provider
    preset = _preset(provider, role=role_name)
    inherits_default = provider == settings.llm_provider
    slot_model = slot.model if slot else ""
    slot_base_url = slot.base_url if slot else ""
    slot_key = slot.api_key if slot else ""
    # 跨 provider 时默认槽位的三项都是「另一套凭证」，用空串表达「不继承」，
    # 交给预设 / 报错分支收口，避免这里出现 if 分支爆炸。
    inherited_model = settings.llm_model if inherits_default else ""
    inherited_base_url = settings.llm_base_url if inherits_default else ""
    inherited_key = settings.llm_api_key if inherits_default else ""
    resolved_model = model or slot_model or inherited_model or preset["model"]
    resolved_base_url = base_url or slot_base_url or inherited_base_url or preset["base_url"]
    resolved_key = api_key or slot_key or inherited_key
    if not resolved_key:
        if role_name and not inherits_default:
            raise AgentCoreConfigError(
                f"角色 {role_name!r} 使用 provider {provider!r}，与默认槽位 "
                f"{settings.llm_provider!r} 不同，不能复用默认槽位的密钥；"
                f"请设置环境变量 {_role_env(role_name, 'API_KEY')}"
            )
        raise AgentCoreConfigError(
            "缺少 LLM API Key，请设置环境变量 AGENT_CORE_LLM_API_KEY"
        )
    if not resolved_model:
        if role_name:
            raise AgentCoreConfigError(
                f"角色 {role_name!r}（provider {provider!r}）缺少模型名，"
                f"请设置环境变量 {_role_env(role_name, 'MODEL')} 或更换 provider"
            )
        raise AgentCoreConfigError(
            "缺少模型名，请设置 AGENT_CORE_LLM_MODEL 或更换 llm_provider"
        )
    # 温度是「风格参数」，跟着槽位走而不是跟着 provider 走：同一家 provider
    # 换模型时温度通常也要一起换（长文写作偏低、评审偏高）。
    if temperature is not None:
        resolved_temperature = temperature
    elif slot is not None and slot.temperature is not None:
        resolved_temperature = slot.temperature
    else:
        resolved_temperature = settings.llm_temperature
    return ResolvedLLM(
        model=resolved_model,
        api_key=resolved_key,
        base_url=resolved_base_url,
        temperature=resolved_temperature,
        # 超时与重试属传输层参数，对所有角色统一生效（见 config 注释）。
        timeout_seconds=settings.llm_timeout_seconds,
        max_retries=settings.llm_max_retries,
    )


def create_chat_model(
    settings: AgentCoreSettings | None = None,
    *,
    role: str | None = None,
    model: str | None = None,
    api_key: str | None = None,
    base_url: str | None = None,
    temperature: float | None = None,
) -> ChatOpenAI:
    """创建聊天模型客户端（仅构造，无网络副作用）。

    :param role: 模型角色；传入即按 ``llm_roles`` 的对应槽位解析（语义见 resolve_llm）
    """
    resolved = resolve_llm(
        settings,
        role=role,
        model=model,
        api_key=api_key,
        base_url=base_url,
        temperature=temperature,
    )
    kwargs: dict[str, object] = {
        "model": resolved.model,
        "api_key": resolved.api_key,
        "temperature": resolved.temperature,
        "timeout": resolved.timeout_seconds,
        "max_retries": resolved.max_retries,
    }
    if resolved.base_url:
        kwargs["base_url"] = resolved.base_url
    return ChatOpenAI(**kwargs)  # type: ignore[arg-type]


def create_embeddings(
    settings: AgentCoreSettings | None = None,
    *,
    model: str | None = None,
    api_key: str | None = None,
    base_url: str | None = None,
    dimensions: int | None = None,
) -> Embeddings:
    """创建 embedding 客户端（semantic-router 决策层用）。

    embedding 与 LLM 允许不同 provider：优先级为
    显式参数 > ``AGENT_CORE_EMBEDDING_*`` > ``AGENT_CORE_LLM_*`` > provider 预设。
    不参与角色槽位：路由层只要一个稠密编码器实例，按阶段换 embedding
    没有意义（换了还会让同一条语料在不同阶段落到不同向量空间）。
    """
    settings = settings or AgentCoreSettings()
    preset = _preset(settings.llm_provider)
    resolved_model = model or settings.embedding_model or preset["embedding_model"]
    resolved_key = api_key or settings.embedding_api_key or settings.llm_api_key
    resolved_base_url = (
        base_url or settings.embedding_base_url or settings.llm_base_url or preset["base_url"]
    )
    if not resolved_model:
        raise AgentCoreConfigError(
            f"provider {settings.llm_provider!r} 无 embedding 预设，"
            "请设置 AGENT_CORE_EMBEDDING_MODEL 与 AGENT_CORE_EMBEDDING_BASE_URL"
        )
    if not resolved_key:
        raise AgentCoreConfigError(
            "缺少 embedding API Key，请设置 AGENT_CORE_EMBEDDING_API_KEY "
            "或 AGENT_CORE_LLM_API_KEY"
        )
    kwargs: dict[str, object] = {
        "model": resolved_model,
        "api_key": resolved_key,
        "dimensions": settings.embedding_dimensions if dimensions is None else dimensions,
    }
    if resolved_base_url:
        kwargs["base_url"] = resolved_base_url
    return OpenAIEmbeddings(**kwargs)  # type: ignore[arg-type]
