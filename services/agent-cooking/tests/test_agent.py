"""插槽契约与装配降级测试。"""

from __future__ import annotations

from conftest import run
from langchain_core.messages import AIMessage

from po_agent_core import AgentCoreSettings, VerticalAgent, create_chat_model
from po_agent_cooking import (
    COOKING_AGENT_NAME,
    COOKING_ROLE,
    OfflineCookingModel,
    build_cooking_agent,
)
from po_agent_cooking.recipes import MockRecipeStore


def _offline_settings() -> AgentCoreSettings:
    """不带密钥的配置：模型解析必定失败，用于验证降级分支。"""
    return AgentCoreSettings(_env_file=None, llm_api_key="")


def _settings_with_key(*, model: str = "test-model") -> AgentCoreSettings:
    """带密钥但不发请求的配置：模型只被构造，不会被调用。"""
    return AgentCoreSettings(
        _env_file=None,
        llm_api_key="test-key",
        llm_provider="custom",
        llm_base_url="http://localhost:1/v1",
        llm_roles={COOKING_ROLE: {"model": model}},
    )


def test_slot_contract() -> None:
    """返回对象必须是合法插槽：名字、描述、语料、已编译子图齐备。"""
    agent = build_cooking_agent(_offline_settings(), store=MockRecipeStore())

    assert isinstance(agent, VerticalAgent)
    assert agent.name == COOKING_AGENT_NAME == "cooking"
    assert agent.description
    assert len(agent.utterances) >= 5
    # 语料要能覆盖「找菜」与「问做法」两类说法，否则路由召回会很差
    assert any("推荐" in item for item in agent.utterances)
    assert any("做法" in item for item in agent.utterances)
    assert agent.metadata["role"] == COOKING_ROLE


def test_slot_name_does_not_collide_with_reserved_nodes() -> None:
    """插槽名不得占用 supervisor 的保留节点名，否则装配期会直接报错。"""
    assert COOKING_AGENT_NAME not in {"route", "chitchat"}


def test_missing_key_degrades_to_offline_model() -> None:
    """缺密钥不抛异常：用离线模型顶上，宿主照常启动。"""
    agent = build_cooking_agent(_offline_settings(), store=MockRecipeStore())

    result = run(agent.graph.ainvoke({"messages": [("user", "推荐几个菜")]}))

    reply = result["messages"][-1]
    assert "离线模式" in reply.content
    # 只有「用户消息 + 一条 AI 回复」：离线模型不调工具，没有工具往返
    assert len(result["messages"]) == 2


def test_explicit_model_is_used_as_is(make_scripted_model) -> None:  # type: ignore[no-untyped-def]
    """显式注入的模型直接生效，不做角色解析。"""
    fake = make_scripted_model([AIMessage(content="好的")])
    agent = build_cooking_agent(
        _offline_settings(), chat_model=fake, store=MockRecipeStore()
    )

    result = run(agent.graph.ainvoke({"messages": [("user", "你好")]}))

    assert result["messages"][-1].content == "好的"


def test_cooking_role_resolves_its_own_model() -> None:
    """cooking 角色的模型名来自角色槽位，与默认槽位互不干扰。

    这是「垂直 Agent 可独立配模型」的关键：把便宜的小模型配给烹饪助手，
    不会影响宿主 chitchat 用的模型。
    """
    settings = _settings_with_key(model="cooking-only-model")
    settings.llm_model = "host-default-model"

    assert create_chat_model(settings, role=COOKING_ROLE).model_name == "cooking-only-model"
    assert create_chat_model(settings).model_name == "host-default-model"


def test_offline_model_bind_tools_returns_self() -> None:
    """离线模型不发起工具调用：bind_tools 必须原样返回自身。"""
    model = OfflineCookingModel()

    assert model.bind_tools([]) is model


def test_offline_reply_is_deterministic() -> None:
    """同样的问题得到同样的回答：离线模式也要可复现。"""
    first = OfflineCookingModel().invoke([("user", "今天吃什么")])
    second = OfflineCookingModel().invoke([("user", "今天吃什么")])

    assert first.content == second.content
    assert first.content.startswith("【离线模式】")
    assert "无法" in first.content or "离线" in first.content
