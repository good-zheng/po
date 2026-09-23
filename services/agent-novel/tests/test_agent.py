"""工厂单测：插槽契约 + LLM 配置两分支 + 分阶段模型装配。"""

from __future__ import annotations

from langchain_core.language_models.chat_models import BaseChatModel

from po_agent_core import AgentCoreSettings
from po_agent_core.agents import VerticalAgent
from po_agent_novel import (
    NOVEL_AGENT_NAME,
    NOVEL_UTTERANCES,
    OfflineNovelModel,
    build_novel_agent,
)
from po_agent_novel.agent import _build_stage_models
from po_agent_novel.graph import (
    ARCHIVE_NODE,
    CONCEIVE_NODE,
    GENERATE_NODE,
    NODE_MODEL_ROLES,
    OUTLINE_NODE,
    REFLECT_NODE,
    STAGE_ROLES,
)


def _offline_settings() -> AgentCoreSettings:
    return AgentCoreSettings(_env_file=None, llm_api_key="")


def _model_name(model: BaseChatModel) -> str:
    return getattr(model, "model_name", None) or getattr(model, "model", "") or type(model).__name__


def test_offline_agent_slot_contract() -> None:
    agent = build_novel_agent(_offline_settings())
    assert isinstance(agent, VerticalAgent)
    assert agent.name == NOVEL_AGENT_NAME
    assert agent.description
    assert agent.utterances == NOVEL_UTTERANCES
    assert all(u.strip() for u in agent.utterances)  # 无空白语料（插槽校验前置）


def test_graph_contains_pipeline_nodes() -> None:
    agent = build_novel_agent(_offline_settings())
    node_names = set(agent.graph.nodes)
    assert {CONCEIVE_NODE, OUTLINE_NODE, GENERATE_NODE, REFLECT_NODE, ARCHIVE_NODE} <= node_names


def test_real_model_settings_still_build_slot() -> None:
    settings = AgentCoreSettings(_env_file=None, llm_provider="qwen", llm_api_key="sk-test")
    agent = build_novel_agent(settings)
    assert agent.name == NOVEL_AGENT_NAME


class TestStageModels:
    """分阶段模型装配：角色覆盖生效、缺角色整体降级、角色与节点声明一致。"""

    def test_stage_roles_match_node_declarations(self) -> None:
        # 角色清单由节点声明推导：增删节点即自动反映到装配层的建模型清单
        assert STAGE_ROLES == ("plan", "write", "judge")
        assert set(STAGE_ROLES) == {str(role) for role in NODE_MODEL_ROLES.values()}
        # 声明的节点名必须真实存在于图内，否则该声明是死配置
        graph_nodes = set(build_novel_agent(_offline_settings()).graph.nodes)
        assert set(NODE_MODEL_ROLES) <= graph_nodes

    def test_role_override_applies_per_stage(self) -> None:
        settings = AgentCoreSettings(
            _env_file=None,
            llm_api_key="sk-test",
            llm_model="qwen-turbo",
            llm_roles={"write": {"model": "qwen-max"}},
        )
        models = _build_stage_models(settings)
        assert _model_name(models["write"]) == "qwen-max"  # 配置的角色槽位生效
        assert _model_name(models["plan"]) == "qwen-turbo"  # 未配置的角色回落默认槽位
        assert _model_name(models["judge"]) == "qwen-turbo"

    def test_any_unavailable_role_degrades_all_to_offline(self) -> None:
        # judge 声明了跨 provider 却没给密钥：预期整体离线，而非只降级 judge
        settings = AgentCoreSettings(
            _env_file=None,
            llm_api_key="sk-test",
            llm_roles={"judge": {"provider": "deepseek"}},
        )
        models = _build_stage_models(settings)
        assert set(models) == set(STAGE_ROLES)
        assert all(isinstance(m, OfflineNovelModel) for m in models.values())
