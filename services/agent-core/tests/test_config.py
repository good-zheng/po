"""配置解析测试（hermetic：禁用 .env 文件，隔离宿主环境）。"""

from __future__ import annotations

import pytest

from po_agent_core.config import AgentCoreSettings


def make(**kwargs) -> AgentCoreSettings:
    return AgentCoreSettings(_env_file=None, **kwargs)


def test_defaults() -> None:
    settings = make()
    assert settings.llm_provider == "qwen"
    assert settings.llm_model == ""  # 空 = 走预设
    assert settings.checkpointer == "redis"  # 本地开发默认 Redis
    assert settings.redis_url == "redis://localhost:6379"
    assert settings.router_threshold == 1.0  # 稠密余弦 + BM25 稀疏分求和
    assert settings.embedding_dimensions == 1024
    assert settings.llm_roles == {}  # 空 = 全部角色走默认槽位（单模型）


def test_llm_roles_default_slot_shape() -> None:
    """槽位字段默认值即「什么都不覆盖」，这是回落逻辑的基石。"""
    slot = make(llm_roles={"write": {}}).llm_roles["write"]
    assert slot.provider == ""
    assert slot.model == ""
    assert slot.api_key == ""
    assert slot.base_url == ""
    assert slot.temperature is None


def test_env_overrides(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AGENT_CORE_LLM_PROVIDER", "deepseek")
    monkeypatch.setenv("AGENT_CORE_LLM_MODEL", "deepseek-reasoner")
    monkeypatch.setenv("AGENT_CORE_CHECKPOINTER", "sqlite")
    monkeypatch.setenv("AGENT_CORE_SQLITE_PATH", "tmp/checkpoints.sqlite")
    settings = AgentCoreSettings(_env_file=None)
    assert settings.llm_provider == "deepseek"
    assert settings.llm_model == "deepseek-reasoner"
    assert settings.checkpointer == "sqlite"
    assert settings.sqlite_path == "tmp/checkpoints.sqlite"


def test_invalid_provider_rejected() -> None:
    with pytest.raises(Exception):
        AgentCoreSettings(_env_file=None, llm_provider="nonexistent")


def test_llm_roles_from_nested_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """角色槽位靠 env_nested_delimiter 从扁平变量还原成 dict 结构。"""
    monkeypatch.setenv("AGENT_CORE_LLM_ROLES__WRITE__MODEL", "qwen-max")
    monkeypatch.setenv("AGENT_CORE_LLM_ROLES__JUDGE__PROVIDER", "deepseek")
    monkeypatch.setenv("AGENT_CORE_LLM_ROLES__JUDGE__TEMPERATURE", "0.2")
    settings = AgentCoreSettings(_env_file=None)
    assert set(settings.llm_roles) == {"write", "judge"}  # 角色名统一小写
    assert settings.llm_roles["write"].model == "qwen-max"
    assert settings.llm_roles["judge"].provider == "deepseek"
    assert settings.llm_roles["judge"].temperature == 0.2
    # 未在角色里声明的项仍取默认槽位（这里是环境默认值）
    assert settings.llm_roles["write"].api_key == ""


def test_extra_env_vars_ignored(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AGENT_CORE_UNKNOWN_VAR", "whatever")
    monkeypatch.setenv("PY_SERVER_PORT", "1234")
    settings = AgentCoreSettings(_env_file=None)
    assert not hasattr(settings, "port")
