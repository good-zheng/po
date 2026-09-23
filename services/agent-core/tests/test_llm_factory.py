"""LLM / Embedding 工厂测试（仅构造解析，不发起网络请求）。"""

from __future__ import annotations

import pytest

from po_agent_core.config import AgentCoreSettings, ModelRole
from po_agent_core.errors import AgentCoreConfigError
from po_agent_core.llm.factory import (
    PROVIDER_PRESETS,
    create_chat_model,
    create_embeddings,
    resolve_llm,
)


def make(**kwargs) -> AgentCoreSettings:
    return AgentCoreSettings(_env_file=None, **kwargs)


class TestResolveLLM:
    def test_qwen_preset_resolution(self) -> None:
        resolved = resolve_llm(make(llm_api_key="sk-test"))
        assert resolved.model == "qwen-plus"
        assert resolved.base_url == "https://dashscope.aliyuncs.com/compatible-mode/v1"
        assert resolved.api_key == "sk-test"

    def test_deepseek_preset_resolution(self) -> None:
        resolved = resolve_llm(make(llm_provider="deepseek", llm_api_key="sk-test"))
        assert resolved.model == "deepseek-chat"
        assert resolved.base_url == "https://api.deepseek.com/v1"

    def test_explicit_params_win_over_env(self) -> None:
        settings = make(llm_provider="qwen", llm_api_key="sk-env", llm_model="qwen-turbo")
        resolved = resolve_llm(settings, model="qwen-max", api_key="sk-explicit")
        assert resolved.model == "qwen-max"
        assert resolved.api_key == "sk-explicit"

    def test_env_model_overrides_preset(self) -> None:
        resolved = resolve_llm(make(llm_api_key="sk-test", llm_model="qwen-max"))
        assert resolved.model == "qwen-max"

    def test_base_url_override(self) -> None:
        resolved = resolve_llm(
            make(llm_api_key="sk-test", llm_base_url="http://localhost:11434/v1")
        )
        assert resolved.base_url == "http://localhost:11434/v1"

    def test_missing_api_key_raises_with_hint(self) -> None:
        with pytest.raises(AgentCoreConfigError, match="AGENT_CORE_LLM_API_KEY"):
            resolve_llm(make(llm_api_key=""))

    def test_custom_provider_without_model_raises(self) -> None:
        with pytest.raises(AgentCoreConfigError, match="模型名"):
            resolve_llm(make(llm_provider="custom", llm_api_key="sk-test"))
    # 未知 provider 由 settings 层的 Literal 校验拦截（见 test_config.py），不到达工厂层


class TestCreateChatModel:
    def test_constructs_without_network(self) -> None:
        model = create_chat_model(make(llm_api_key="sk-test"))
        name = getattr(model, "model_name", None) or getattr(model, "model", "")
        assert name == "qwen-plus"

    def test_constructs_role_model_without_network(self) -> None:
        settings = make(llm_api_key="sk-test", llm_roles={"write": {"model": "qwen-max"}})
        model = create_chat_model(settings, role=ModelRole.WRITE)
        name = getattr(model, "model_name", None) or getattr(model, "model", "")
        assert name == "qwen-max"


class TestRoleSlots:
    """角色槽位解析：未配置即回落默认槽位，跨 provider 不复用密钥。"""

    def test_unconfigured_role_falls_back_to_default_slot(self) -> None:
        resolved = resolve_llm(make(llm_api_key="sk-test", llm_model="qwen-turbo"), role="write")
        assert resolved.model == "qwen-turbo"
        assert resolved.api_key == "sk-test"
        assert resolved.base_url == PROVIDER_PRESETS["qwen"]["base_url"]

    def test_formal_role_enum_accepted(self) -> None:
        settings = make(llm_api_key="sk-test", llm_roles={ModelRole.WRITE: {"model": "qwen-max"}})
        assert resolve_llm(settings, role=ModelRole.WRITE).model == "qwen-max"

    def test_role_name_case_insensitive(self) -> None:
        settings = make(llm_api_key="sk-test", llm_roles={"write": {"model": "qwen-max"}})
        assert resolve_llm(settings, role=" WRITE ").model == "qwen-max"

    def test_empty_role_means_default_slot(self) -> None:
        settings = make(llm_api_key="sk-test", llm_roles={"write": {"model": "qwen-max"}})
        assert resolve_llm(settings, role="").model == "qwen-plus"

    def test_same_provider_role_overrides_model_only(self) -> None:
        settings = make(
            llm_api_key="sk-shared",
            llm_model="qwen-turbo",
            llm_roles={"write": {"model": "qwen-max", "temperature": 0.9}},
        )
        resolved = resolve_llm(settings, role="write")
        assert resolved.model == "qwen-max"
        assert resolved.api_key == "sk-shared"  # 同 provider：复用默认槽位密钥
        assert resolved.temperature == 0.9  # 槽位温度优先于默认槽位温度
        assert resolve_llm(settings).temperature == settings.llm_temperature

    def test_cross_provider_role_uses_own_key_and_preset(self) -> None:
        settings = make(
            llm_api_key="sk-qwen",
            llm_model="qwen-turbo",
            llm_roles={"judge": {"provider": "deepseek", "api_key": "sk-deepseek"}},
        )
        resolved = resolve_llm(settings, role="judge")
        # 跨 provider 时不继承默认槽位的模型名，落到 deepseek 预设
        assert resolved.model == PROVIDER_PRESETS["deepseek"]["model"]
        assert resolved.base_url == PROVIDER_PRESETS["deepseek"]["base_url"]
        assert resolved.api_key == "sk-deepseek"

    def test_cross_provider_role_without_key_raises_with_env_hint(self) -> None:
        settings = make(
            llm_api_key="sk-qwen",
            llm_roles={"judge": {"provider": "deepseek"}},
        )
        with pytest.raises(AgentCoreConfigError, match="AGENT_CORE_LLM_ROLES__JUDGE__API_KEY"):
            resolve_llm(settings, role="judge")

    def test_custom_provider_role_without_model_raises_with_env_hint(self) -> None:
        settings = make(
            llm_api_key="sk-qwen",
            llm_roles={"write": {"provider": "custom", "api_key": "sk-custom"}},
        )
        with pytest.raises(AgentCoreConfigError, match="AGENT_CORE_LLM_ROLES__WRITE__MODEL"):
            resolve_llm(settings, role="write")

    def test_unknown_role_provider_raises_naming_role(self) -> None:
        settings = make(
            llm_api_key="sk-qwen",
            llm_roles={"judge": {"provider": "nonexistent", "api_key": "sk-x"}},
        )
        with pytest.raises(AgentCoreConfigError, match="judge"):
            resolve_llm(settings, role="judge")

    def test_explicit_params_win_over_role_slot(self) -> None:
        settings = make(llm_api_key="sk-test", llm_roles={"write": {"model": "qwen-max"}})
        resolved = resolve_llm(settings, role="write", model="qwen-plus", api_key="sk-explicit")
        assert resolved.model == "qwen-plus"
        assert resolved.api_key == "sk-explicit"

    def test_slot_base_url_override(self) -> None:
        settings = make(
            llm_api_key="sk-test",
            llm_roles={"judge": {"base_url": "http://localhost:11434/v1", "model": "local-judge"}},
        )
        resolved = resolve_llm(settings, role="judge")
        assert resolved.base_url == "http://localhost:11434/v1"
        assert resolved.model == "local-judge"


class TestCreateEmbeddings:
    def test_qwen_embedding_preset(self) -> None:
        embeddings = create_embeddings(make(llm_api_key="sk-test"))
        name = getattr(embeddings, "model", "")
        assert name == "text-embedding-v4"

    def test_deepseek_without_embedding_config_raises(self) -> None:
        with pytest.raises(AgentCoreConfigError, match="EMBEDDING"):
            create_embeddings(make(llm_provider="deepseek", llm_api_key="sk-test"))

    def test_separate_embedding_provider(self) -> None:
        settings = make(
            llm_provider="deepseek",
            llm_api_key="sk-llm",
            embedding_model="text-embedding-v4",
            embedding_base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            embedding_api_key="sk-embed",
        )
        embeddings = create_embeddings(settings)
        assert getattr(embeddings, "model", "") == "text-embedding-v4"

    def test_missing_embedding_key_raises(self) -> None:
        settings = make(
            llm_api_key="",
            embedding_model="text-embedding-v4",
            embedding_base_url="https://example.com/v1",
        )
        with pytest.raises(AgentCoreConfigError, match="embedding API Key"):
            create_embeddings(settings)


def test_provider_presets_shape() -> None:
    for provider, preset in PROVIDER_PRESETS.items():
        assert set(preset) == {"base_url", "model", "embedding_model"}, provider
