"""统一事件流契约。

事件名对齐 ``services/chat/agent_run_satus.json`` 草案
（lifecycle / thinking / tool / output / control 五组），
另增 ``STEP`` 承载 graph 节点级阶段进度（继承参考实现的流式进度协议）。
WS 帧、A2A 事件、MCP 通知均由宿主从该事件流翻译。
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class EventType(StrEnum):
    """事件类型枚举：值与前端/外部协议里的帧类型字符串一一对应。

    枚举值即对外契约，改名等同于改协议，前端按字符串匹配消费。
    """

    # lifecycle：一次 run 的开始/正常结束/失败，三选一收尾
    RUN_STARTED = "run_started"
    RUN_FINISHED = "run_finished"
    RUN_ERROR = "run_error"

    # thinking
    THINKING = "thinking"
    PLAN = "plan"

    # tool
    TOOL_CALL_START = "tool_call_start"
    TOOL_CALL_ARGS = "tool_call_args"
    TOOL_CALL_END = "tool_call_end"
    TOOL_CALL_RESULT = "tool_call_result"
    TOOL_APPROVAL_REQUEST = "tool_approval_request"

    # output
    TEXT_MESSAGE_CONTENT = "text_message_content"

    # 设定提议卡（§10.3 约定 1）：对话侧唯一的结构化产出，content 是人读的一句话，
    # payload 是提案字段本体。它不是 tool 结果也不是审批请求——前端把它转成
    # 「作者点采纳才落库」的卡片，编排侧不写任何库。
    PROPOSAL = "proposal"

    # 阶段进度（graph 节点进入/完成）
    # 注意：runner 以 subgraphs=True 驱动，垂直 Agent 内部的子图节点
    # 也会以 STEP 上浮，因此 payload.node 可能是子图内部节点名，
    # 不一定是父图插槽名
    STEP = "step"

    # control（WS 上行；此处仅作协议定义，由宿主消费）
    # INTERRUPT：编排挂起等人确认，宿主下发前端后等 APPROVAL_RESPONSE；
    # 确认值原样回灌给 LangGraph 的 Command(resume=...)，线程才能续跑
    INTERRUPT = "interrupt"
    APPROVAL_RESPONSE = "approval_response"


@dataclass(slots=True)
class AgentEvent:
    """编排运行期对外发布的单条事件。

    这是「唯一真相」：图内部节点的产出先被 runner 归一成本类型，
    再由宿主翻译成各自的对外协议（WebSocket 帧、A2A 事件、MCP 通知）。
    编排层不感知任何具体传输协议。
    """

    type: EventType
    content: str = ""
    payload: dict[str, Any] = field(default_factory=dict)
    ts: float = field(default_factory=time.time)  # epoch 秒，供消费方排序/计时

    def to_frame(self) -> dict[str, Any]:
        """转成可直接 JSON 序列化的字典（默认值语义不变）。"""
        return {
            "type": self.type.value,
            "content": self.content,
            "payload": self.payload,
            "ts": self.ts,
        }
