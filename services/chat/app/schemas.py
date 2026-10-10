"""宿主服务的 Pydantic V2 校验模型（REST 与 WS 共用）。

两类模型刻意放在同一模块：

- ``Item*``：items 示例 CRUD 的领域模型，被 :mod:`app.store` 与
  :mod:`app.routers.items` 使用（``ItemCreate`` 做写入校验、``ItemUpdate``
  承载 PATCH 语义、``Item`` 是带服务端字段的持久化形态）；
- ``WSInFrame`` / ``WSOutFrame``：``/ws/chat`` 的帧协议。放在这里是为了让
  前端联调时只需对照一个文件即可确认字段，路由层不再另做字典校验。

所有模型均为 Pydantic V2 ``BaseModel``，由 FastAPI 在入口处自动完成
校验与序列化（校验失败由框架统一返回 422；WS 侧因无框架兜底，由
:mod:`app.routers.ws` 自行捕获 ``ValidationError`` 并回 ``error`` 帧）。
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class ItemBase(BaseModel):
    """items 的公共字段与校验约束，作为 Create/持久化形态的共同基类。"""

    name: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    price: float = Field(gt=0)
    in_stock: bool = True


class ItemCreate(ItemBase):
    """创建请求体：字段与约束完全复用 ItemBase，不额外放宽或收紧。"""

    pass


class ItemUpdate(BaseModel):
    """PATCH 局部更新请求体：所有字段可选，未出现的字段保持原值。

    单独定义而不继承 ``ItemBase``，是为了让「不传字段」在类型层面成立；
    存储层再用 ``model_dump(exclude_unset=True)`` 区分「未传」与「显式传
    null」，因此这里允许 ``name``/``price`` 为 ``None`` 也不会把已有值清空。
    """

    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    price: float | None = Field(default=None, gt=0)
    in_stock: bool | None = None


class Item(ItemBase):
    """对外返回的完整资源形态：在入参字段之外附加服务端生成字段。"""

    id: int
    created_at: datetime
    updated_at: datetime


class WSInFrame(BaseModel):
    """WebSocket 入站帧：``message``（新消息）/ ``ping``（心跳）/ ``resume``（继续挂起线程）。

    ``content`` 与 ``conversation_id`` 统一给空字符串默认值而非 ``None``，
    这样 ping 帧可以只发 ``{"type": "ping"}``，路由层也能用简单的真值判断
    处理缺省情况，不必到处写 ``is None`` 分支。
    """

    type: Literal["message", "ping", "resume"]
    content: str = ""
    # 语义上等价于 LangGraph 的 thread_id：同一 id 复用同一份会话记忆，
    # 也是 interrupt 后 resume 定位挂起线程的唯一凭据。
    conversation_id: str = ""
    # 显式指定垂直 Agent 插槽名（如 "talk"）：命中则跳过意图路由，确定性委托该插槽
    # （仍在 supervisor 父图上执行，好让 resume 命中同一份 checkpoint）。
    # 缺省 None = 交给 supervisor 的 Layer1 路由决定，与历史上线的行为一致
    # （这是后加字段，老客户端不发它也不会改变任何行为）。
    agent: str | None = None
    # 随消息携带的上下文元信息，宿主会把它拼成 [key: value] 前缀一起发给模型；
    # 其中 utteranceId 是保留键——只用于结果回写定位，不进提示词。
    context: dict[str, object] | None = None


class WSOutFrame(BaseModel):
    """WebSocket 出站帧：``type`` 取值即前端消费的帧协议全集。

    ``type`` 用 ``Literal`` 收口是为了让协议变更有类型检查兜底（新增帧类型
    必须同时改动这里）；``payload`` 承载结构化附加信息（如 run_started 的
    thread_id、tool_call_* 的工具名与参数），前端对未知 ``type`` 必须忽略
    而非报错，以支持后续新增帧的灰度。
    """

    type: Literal[
        "token",
        "done",
        "pong",
        "error",
        "run_started",
        "step",
        "thinking",
        "plan",
        "tool_call_start",
        "tool_call_args",
        "tool_call_end",
        "tool_call_result",
        "interrupt",
        "proposal",
    ]
    content: str = ""
    # 可变默认值在 Pydantic V2 中是安全的：每个实例都会拿到深拷贝，
    # 不会出现多个帧共享同一个 dict 的串数据问题。
    payload: dict[str, object] = {}
