"""编排装配层：把 po-agent-core 组件组装为 chat 宿主可用的 Orchestrator。

降级链（启动永不因配置失败而中断）：

- LLM：``AGENT_CORE_LLM_API_KEY`` 缺失 → ``EchoChatModel`` 回显模式
  （与 P0 阶段的 echo 端点行为一致，保持前端/测试零感知）；
- checkpointer：redis/sqlite 连接失败 → memory（会话记忆退化为进程内，
  服务可用性优先）；
- 垂直 Agent：``agents=None`` 时装配内置插槽（当前为空，登记点见
  :func:`_builtin_agents`），包缺失或装配失败逐个跳过；``agents=[]``
  显式不装配；
- 意图路由：``create_intent_router`` 按 slots 派生语料，embedding 缺失
  或装配失败时降级本地关键词路由（垂直 Agent 仍可被路由到），无命中
  再由 supervisor 兜底 chitchat。

AgentCard/MCP/A2A（P3/P4）在此层之上扩展，不改动本文件的核心装配职责。

在链路中的位置
--------------

调用方：:mod:`app.main` 的 lifespan 在进程启动时调用 :func:`build_orchestrator`
一次，结果放入 ``app.state.orchestrator`` 供所有 WS 连接共享；测试也可直接
调用本函数装配隔离实例（见 ``tests/test_ws.py``）。

被调用方：:class:`Orchestrator` 是宿主唯一持有的编排入口，只有
:mod:`app.routers.ws` 会调用它的 ``run`` / ``resume`` / ``aclose``。

分层意图：本文件是「宿主 ↔ 编排核心」的边界。宿主侧（FastAPI/WS 帧协议）
不应知道 LLM、checkpointer、路由器的具体实现，因此所有与配置有关的决策
（含全部降级）都收敛在这里，上游拿到的永远是一个可直接 ``astream`` 的
Orchestrator。
"""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from uuid import uuid4

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import Command

from po_agent_core import (
    AgentCoreSettings,
    AgentRunner,
    CheckpointerManager,
    ModelRole,
    VerticalAgent,
    create_chat_model,
    create_intent_router,
    routes_from_agents,
)
from po_agent_core.errors import AgentCoreError
from po_agent_core.events import AgentEvent
from po_agent_core.supervisor.graph import build_supervisor_graph

logger = logging.getLogger(__name__)

# 上下文里的保留键：只用于宿主侧的结果回写定位，不拼进提示词，
# 否则模型会把「utteranceId: 128」当成对话内容的一部分去分析。
# bookId/chapterId 同属这一类：它们是「本轮读哪本书、截至哪一章」的定位键，
# 由下面 :meth:`Orchestrator._config` 经 ``configurable`` 交给领域侧，模型不需要、
# 也不应该在文本里看到一个能照着复述的 id（打字进去的假 id 决定不了任何库读）。
# 续写的四个控制键同理，而且更要紧：fromChapter/chapterCount 是「这一轮写哪几章」的
# 范围，auto 是「要不要问作者」。拼进文本会让模型以为作者在跟它商量这些数字，
# 而真正决定链路的是 configurable 里的那份——两边不一致时模型说一套、图做一套。
RESERVED_CONTEXT_KEYS: frozenset[str] = frozenset(
    {
        "utteranceId",
        "sessionId",
        "bookId",
        "chapterId",
        "fromChapter",
        "chapterCount",
        "auto",
        "tailChapterId",
    }
)


class EchoChatModel(BaseChatModel):
    """无 API Key 时的离线降级模型：回显最后一条用户消息。

    继承 ``BaseChatModel`` 而不是写一个假对象，是因为 supervisor graph 与
    ``AgentRunner`` 都按 LangChain 的 ``Runnable`` 协议调用它（``ainvoke`` /
    流式接口），只有满足该协议才能在不改动编排核心的前提下替换真实模型。

    行为上刻意与 P0 阶段的 echo 端点保持一致（同样的固定前缀文案），
    使前端与既有测试在「无 Key」与「有 Key」两种环境下都无需分支处理。
    """

    @property
    def _llm_type(self) -> str:
        # LangChain 要求提供模型标识，用于日志/回调归因。
        return "echo-chat-model"

    @staticmethod
    def _reply(messages: list) -> str:
        """取最后一条 HumanMessage 回显。

        模型收到的是整段会话历史，但回显只关心最新一轮用户输入，因此从后
        往前找第一个 HumanMessage；``content`` 可能是多模态列表（如
        [{"type": "text", ...}]），统一 ``str()`` 兜底避免拼接时报错。
        """
        last_user = next(
            (m for m in reversed(messages) if isinstance(m, HumanMessage)), None
        )
        text = last_user.content if last_user else ""
        if not isinstance(text, str):
            text = str(text)
        return f"你说的是：{text}"

    def _generate(self, messages, stop=None, run_manager=None, **kwargs) -> ChatResult:
        # 同步入口：测试或其他同步调用方可能走这里，行为必须与异步版一致。
        return ChatResult(
            generations=[ChatGeneration(message=AIMessage(content=self._reply(messages)))]
        )

    async def _agenerate(
        self, messages, stop=None, run_manager=None, **kwargs
    ) -> ChatResult:
        # 异步入口才是 WS 运行期实际走的路径（AgentRunner 全程 async）。
        return ChatResult(
            generations=[ChatGeneration(message=AIMessage(content=self._reply(messages)))]
        )


@dataclass(slots=True)
class Orchestrator:
    """宿主持有的编排入口：graph + runner + checkpointer 生命周期。

    三个字段的职责边界：

    - ``graph``：已编译的 supervisor graph（含垂直 Agent 与意图路由），
      由 :class:`AgentRunner` 驱动，本类不直接调用；
    - ``runner``：把 graph 的底层流失翻译成统一的 ``AgentEvent`` 流
      （超时、错误都在其内部转成事件而非抛出）；
    - ``_checkpointer``：checkpointer 的持有者，仅在 :meth:`aclose` 时使用
      （graph 只需要 saver 本身），因此不参与 repr，避免日志里出现连接细节。
    """

    graph: CompiledStateGraph
    runner: AgentRunner
    settings: AgentCoreSettings
    # name → 插槽，供 WSInFrame.agent 直连某个垂直 Agent 时查表
    agents: dict[str, VerticalAgent] = field(default_factory=dict)
    _checkpointer: CheckpointerManager | None = field(default=None, repr=False)

    def _config(
        self, conversation_id: str, context: dict[str, object] | None = None
    ) -> dict:
        """构造 LangGraph 运行配置：会话标识即 ``thread_id``。

        多轮记忆与 interrupt 恢复都依赖这个映射——同一 id 才会命中同一份
        检查点，换 id 等于开新会话。

        ``context`` 原样放进 ``configurable``：垂直 Agent 用
        ``config["configurable"]["context"]`` 读它，这条通道对模型不可见，
        因此「本轮读哪本书」由服务端手里的那份帧决定，而不是提示词里谁打了什么。
        宿主不解释键名（chitchat/supervisor 都不看它），领域侧按自己的白名单取值。
        """
        configurable: dict[str, object] = {"thread_id": conversation_id}
        if context:
            configurable["context"] = context
        return {"configurable": configurable}

    async def run(
        self,
        text: str,
        *,
        conversation_id: str | None = None,
        agent: str | None = None,
        context: dict[str, object] | None = None,
    ) -> AsyncIterator[AgentEvent]:
        """新消息进入编排：conversation_id 缺省时生成新会话。

        :param agent: 显式指定插槽名则跳过意图路由、确定性委托该插槽，用于
            「客户端已经知道要哪个 Agent」的场景（言外小程序、创作工作台的
            生成面板即如此）；**不直连子图**，见下面 state 处的说明。
        :param context: 上下文元信息，会拼成 ``[key: value]`` 前缀随消息发出，
            其中 ``utteranceId`` 是保留键、只用于结果回写定位。
        """
        thread = conversation_id or uuid4().hex
        # 只传本轮用户消息：历史由 checkpointer 按 thread_id 载入，再经 graph
        # 的 messages reducer 追加合并；若要重放上下文需连同历史一起传入。
        content = text
        if context:
            prefix = "".join(
                f"[{key}: {value}]\n"
                for key, value in context.items()
                if key not in RESERVED_CONTEXT_KEYS
            )
            if prefix:
                content = prefix + content
        state: dict[str, object] = {"messages": [HumanMessage(content=content)]}
        # 直连也必须走父图：子图 compile() 刻意不挂 checkpointer（saver 由父图统一
        # 供给），而 :meth:`resume` 只能按 conversation_id 打回 ``self.graph``——
        # run 走子图、resume 走父图，两边不是同一个 checkpoint，垂直 Agent 的
        # interrupt（novel 的归档确认）就永远确认不了。改为把插槽名塞进
        # forced_agent，由 route 节点跳过语义路由。
        if agent and agent in self.agents:
            state["forced_agent"] = agent
        async for event in self.runner.astream(
            self.graph, state, config=self._config(thread, context)
        ):
            yield event

    async def resume(self, conversation_id: str, value: str) -> AsyncIterator[AgentEvent]:
        """interrupt 后继续：按 conversation_id 定位挂起的线程。

        ``Command(resume=value)`` 让 graph 从挂起的节点处继续执行，而不是重跑
        整条链路；``value`` 是用户回答的原文，语义解释交由垂直 Agent 决定。

        这里不需要 ``agent`` 参数：:meth:`run` 无论是否点名插槽都在同一个
        ``thread_id`` 上跑父图，挂起点因此总在父图手里这份 checkpoint 里。
        """
        if not conversation_id:
            # 与路由层的校验重复一次：这里是更内层的守门，避免调用方绕过 WS
            # 直接使用时静默新建线程、把确认丢了。
            raise ValueError("resume 需要 conversation_id（interrupt 挂起的线程）")
        async for event in self.runner.astream(
            self.graph, Command(resume=value), config=self._config(conversation_id)
        ):
            yield event

    async def aclose(self) -> None:
        """释放 checkpointer 持有的外部连接（由 :mod:`app.main` 的关闭阶段调用）。

        ``_checkpointer`` 可为 None：``build_orchestrator`` 总是会返回一个
        manager，但测试可以直接构造 Orchestrator 而不传 checkpointer，
        因此这里做空值判断而不是强制要求。
        """
        if self._checkpointer is not None:
            await self._checkpointer.aclose()


async def _init_checkpointer(
    settings: AgentCoreSettings,
) -> tuple[BaseCheckpointSaver, CheckpointerManager | None]:
    """初始化 checkpointer，失败则降级 memory；返回 ``(saver, manager)``。

    返回两个对象而不是只返回 saver：graph 编译只需要 saver，而连接池/文件句柄
    的释放必须通过 manager 完成（见 :meth:`Orchestrator.aclose`），所以调用方
    要把 manager 一起保管。

    降级后果：并发会话的记忆退化为进程内，进程重启即失忆；多 worker 部署下
    各 worker 也互不可见。这只影响记忆持久性，不影响服务可用性。
    """
    manager = CheckpointerManager(settings)
    try:
        saver = await manager.get_saver()
        return saver, manager
    except Exception as exc:  # redis/sqlite 不可达 → memory 兜底，服务不阻断
        # 先关闭失败的管理器：get_saver 可能已建立部分连接（如 sqlite 文件句柄、
        # redis 客户端池），不清理会在重启循环里累积泄漏。
        await manager.aclose()
        logger.warning(
            "checkpointer %s 初始化失败，降级为 memory：%s", settings.checkpointer, exc
        )
        # 用 model_copy 生成一份改了 checkpointer 字段的副本，而不是直接改
        # settings：settings 是宿主共享的配置对象（LLM/路由等仍在读它），
        # 就地修改会让日志与实际行为不一致。
        fallback = CheckpointerManager(
            settings.model_copy(update={"checkpointer": "memory"})
        )
        return await fallback.get_saver(), fallback


def _builtin_agents(settings: AgentCoreSettings) -> list[VerticalAgent]:
    """宿主默认装配的垂直 Agent；包缺失或装配失败逐个跳过。

    此函数是唯一的插槽登记点：垂直 Agent 按「函数内延迟导入 + 失败仅跳过
    本插槽」的模式在这里登记（延迟导入是为了让未安装该包的部署环境仍能
    启动 chitchat）。装配失败只降级本插槽——烹饪助手起不来不该让整个
    聊天服务不可用，用户仍能拿到 chitchat 兜底回复。
    """
    agents: list[VerticalAgent] = []
    try:
        from po_agent_cooking import build_cooking_agent
    except ImportError as exc:
        logger.info("未安装 po-agent-cooking，跳过 cooking 插槽：%s", exc)
    else:
        try:
            agents.append(build_cooking_agent(settings))
        except Exception as exc:  # 装配异常（配置/依赖问题）不该阻断宿主启动
            logger.warning("cooking 插槽装配失败，已跳过：%s", exc)
    try:
        from po_agent_talk import build_talk_agent
    except ImportError as exc:
        logger.info("未安装 po-agent-talk，跳过 talk 插槽：%s", exc)
    else:
        try:
            agents.append(build_talk_agent(settings))
        except Exception as exc:
            logger.warning("talk 插槽装配失败，已跳过：%s", exc)
    try:
        from po_agent_novel import build_novel_agent
    except ImportError as exc:
        logger.info("未安装 po-agent-novel，跳过 novel 插槽：%s", exc)
    else:
        try:
            agents.append(build_novel_agent(settings))
        except Exception as exc:
            logger.warning("novel 插槽装配失败，已跳过：%s", exc)
    # 第四个插槽、第二个小说插槽：创作工作台右栏的对话面板（§10.3）。与 novel 插槽分开注册是
    # 必要的——生成链路是会写库的长任务，对话面板只读不写，两者共用一个名字就会
    # 让「直连 novel」的客户端拿到意料之外的行为。
    try:
        from po_agent_novel import build_novel_chat_agent
    except ImportError as exc:
        logger.info("未安装 po-agent-novel，跳过 novel-chat 插槽：%s", exc)
    else:
        try:
            agents.append(build_novel_chat_agent(settings))
        except Exception as exc:
            logger.warning("novel-chat 插槽装配失败，已跳过：%s", exc)
    return agents


async def build_orchestrator(
    settings: AgentCoreSettings | None = None,
    *,
    chat_model: BaseChatModel | None = None,
    agents: list[VerticalAgent] | None = None,
) -> Orchestrator:
    """按配置组装 Orchestrator（全降级链见模块 docstring）。

    ``agents=None`` 装配内置垂直 Agent；``agents=[]`` 显式不装配（测试
    可借此锁定纯 chitchat 路径）。

    :param settings: 编排核心配置；缺省用 ``AgentCoreSettings()``（即全部走
        环境变量默认值），异常情形下也能构造出实例。
    :param chat_model: 显式注入聊天模型（测试用假模型锁定输出）；缺省按配置
        创建，无 Key 时降级为 :class:`EchoChatModel`。
    :param agents: 垂直 Agent 插槽；语义如上。
    :return: 可直接 ``run``/``resume`` 的 Orchestrator（checkpointer 已就绪）。
    """
    settings = settings or AgentCoreSettings()
    if chat_model is None:
        try:
            # 闲聊兜底固定按 chat 角色取模型：宿主用不到「长文写作」那类重模型，
            # 可单独给 AGENT_CORE_LLM_ROLES__CHAT__MODEL 配便宜的小模型；
            # 未配置该角色时回落默认槽位，与单模型时代的行为完全一致。
            chat_model = create_chat_model(settings, role=ModelRole.CHAT)
        except AgentCoreError as exc:
            # 只兜住「配置缺失」这一预期异常（未配置 Key 等）；其他异常说明
            # 工厂本身有问题，应照常上抛而不是伪装成可用状态。
            logger.warning("LLM 未配置，chitchat 降级为回显模式：%s", exc)
            chat_model = EchoChatModel()
    if agents is None:
        # None 与 [] 的区别是刻意的：前者表示「用宿主默认插槽」，后者表示
        # 「明确不要任何垂直 Agent」，测试依赖后者排除路由干扰。
        agents = _builtin_agents(settings)
    saver, manager = await _init_checkpointer(settings)
    # 用插槽的 utterances 派生 Layer1 路由语料；embedding 不可用时
    # create_intent_router 内部会退化为本地关键词路由，全部插槽名保留。
    router = create_intent_router(settings, routes_from_agents(agents))
    graph = build_supervisor_graph(agents, router, chat_model, checkpointer=saver)
    # runner 的职责边界：它按 settings.run_timeout_seconds 给每次 run 加超时，
    # 并把超时/异常转成 RUN_ERROR 事件，因此 WS 层永远收到完整的事件序列。
    runner = AgentRunner(timeout_seconds=settings.run_timeout_seconds)
    logger.info(
        "Orchestrator 就绪：checkpointer=%s model=%s agents=%d",
        settings.checkpointer,
        type(chat_model).__name__,
        len(agents or []),
    )
    return Orchestrator(
        graph=graph,
        runner=runner,
        settings=settings,
        agents={slot.name: slot for slot in (agents or [])},
        _checkpointer=manager,
    )
