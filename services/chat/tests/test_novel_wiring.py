"""novel 插槽在宿主装配下的端到端帧序（离线模型，不打真实额度）。

这层接缝此前没有覆盖：agent-core 测自己的 supervisor 图、agent-novel 测自己的领域图，
而 §15.19 遗留 #1 恰好长在两者的接缝上——`run` 直连子图、`resume` 打回父图，两边不是同一份
checkpoint，于是浏览器点「确认归档」永远确认不了。全套测试当时是绿的。

所以这里刻意用**真实**的 novel 插槽（`build_novel_graph` 的 `compile()` 不挂 checkpointer），
只把模型换成 `OfflineNovelModel`、两个 store 换成进程内实现，走宿主的 WS 端点跑一遍
`message{agent} → interrupt → done → resume{conversation_id} → 归档`。
"""

import asyncio

import pytest
from app.agent import build_orchestrator
from app.main import create_app
from fastapi.testclient import TestClient
from po_agent_core import AgentCoreSettings
from po_agent_novel import (
    InMemoryCanonStore,
    MockNovelStore,
    OfflineNovelModel,
    build_novel_agent,
)

def offline_settings() -> AgentCoreSettings:
    return AgentCoreSettings(_env_file=None, checkpointer="memory", llm_api_key="")


def build_client() -> tuple[TestClient, MockNovelStore]:
    """装配一个「宿主 + 真图 + 离线模型」的 TestClient，成稿留在进程内。

    章数不显式指定：`OfflineNovelModel` 的大纲恒产 3 章，传 `chapter_count` 只会让
    「请求 2 章 / 实得 3 章」变成这条用例要解释的额外变量。
    """
    store = MockNovelStore()
    slot = build_novel_agent(
        offline_settings(),
        chat_model=OfflineNovelModel(),
        store=store,
        canon_store=InMemoryCanonStore(),
    )
    orchestrator = asyncio.run(
        build_orchestrator(
            offline_settings(), chat_model=OfflineNovelModel(), agents=[slot]
        )
    )
    return TestClient(create_app(orchestrator=orchestrator)), store


def drain(websocket) -> list[dict]:
    """收帧直到 done/error：一轮的完整帧序列。"""
    frames: list[dict] = []
    while True:
        frame = websocket.receive_json()
        frames.append(frame)
        if frame["type"] in ("done", "error"):
            assert frame["type"] == "done", f"本轮以 error 收尾：{frame}"
            return frames


def test_archive_interrupt_is_confirmed_over_ws() -> None:
    """带 `agent` 的那轮 interrupt，只带 `conversation_id` 的 resume 就能确认并落库。"""
    client, store = build_client()

    with client.websocket_connect("/ws/chat") as websocket:
        websocket.send_json(
            {
                "type": "message",
                "content": "帮我写一本玄幻小说",
                "agent": "novel",
                "conversation_id": "conv-novel-ws",
            }
        )
        first = drain(websocket)

        interrupts = [f for f in first if f["type"] == "interrupt"]
        assert len(interrupts) == 1, f"应有且仅有一次归档确认：{first}"
        value = interrupts[0]["payload"]["value"]
        assert value["chapter_count"] >= 1
        assert value["hint"]
        # 直连插槽改成走父图后多了一条编排节点的 step；有它就是真的过了 route 节点，
        # 而不是被 chitchat 代答（那种情况下永远不会有 interrupt）。
        nodes = [f["payload"].get("node") for f in first if f["type"] == "step"]
        assert "route" in nodes

        websocket.send_json(
            {"type": "resume", "content": "yes", "conversation_id": "conv-novel-ws"}
        )
        second = drain(websocket)

    archived = [
        f
        for f in second
        if f["type"] == "thinking" and f["payload"].get("stage") == "archived"
    ]
    assert archived, f"resume 之后没有归档帧：{[f['type'] for f in second]}"
    book_id = archived[0]["payload"]["book_id"]

    books = asyncio.run(store.list_books())
    assert [book.book_id for book in books] == [book_id]
    # 卡片上报的章数与真正入库的章数是同一个数：作者拍板时读到的就是落库的结果
    assert books[0].chapter_count == value["chapter_count"]
    # 正文随 resume 那轮回流：确认之后前端才看得到成稿
    tokens = "".join(f["content"] for f in second if f["type"] == "token")
    assert "已归档入库" in tokens


@pytest.mark.parametrize("answer", ["", "先看看"])
def test_archive_declined_writes_nothing_over_ws(answer: str) -> None:
    """答非确认词 = 暂不落库：正文照回，但成稿表与正典一行都不该有（§9.3 口径）。"""
    client, store = build_client()

    with client.websocket_connect("/ws/chat") as websocket:
        websocket.send_json(
            {
                "type": "message",
                "content": "帮我写一本玄幻小说",
                "agent": "novel",
                "conversation_id": "conv-novel-decline",
            }
        )
        first = drain(websocket)
        assert [f["type"] for f in first if f["type"] == "interrupt"] == ["interrupt"]

        websocket.send_json(
            {"type": "resume", "content": answer, "conversation_id": "conv-novel-decline"}
        )
        second = drain(websocket)

    assert not [f for f in second if f["payload"].get("stage") == "archived"]
    assert asyncio.run(store.list_books()) == []
