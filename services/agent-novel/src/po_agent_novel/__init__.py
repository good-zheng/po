"""po-agent-novel：小说创作垂直 Agent（经 po-agent-core 插槽接入 supervisor）。

本模块是包的对外门面：把插槽装配入口、子图工厂、L1 上下文编译器、离线模型、
领域 schema 与数据层协议统一提升到包根，宿主只需
``from po_agent_novel import build_novel_agent``
即可装配（services/chat 的内置插槽装配正是这样引用的）。

依赖方向严格单向：本包依赖 po-agent-core（插槽协议、事件契约、CoreState），
core 不反向依赖本包——因此 novel 可独立测试、按需装卸，装配失败也不阻断宿主启动。
"""

# 下列导入即包根的公开 API 面重导出；符号语义见各自模块。
from po_agent_novel.actor import current_actor, reset_actor, set_actor
from po_agent_novel.agent import (
    NOVEL_AGENT_NAME,
    NOVEL_UTTERANCES,
    build_novel_agent,
)
from po_agent_novel.chat import NOVEL_CHAT_AGENT_NAME, build_novel_chat_agent
from po_agent_novel.context import Budgets, compile_context
from po_agent_novel.graph import build_novel_graph
from po_agent_novel.http_store import HttpCanonStore, HttpNovelStore, NovelStoreError
from po_agent_novel.offline import OfflineNovelChatModel, OfflineNovelModel
from po_agent_novel.schemas import (
    ArchivedBook,
    BookDraft,
    BookIdea,
    ChapterDraft,
    ChapterExtraction,
    ChapterOutline,
    CharacterList,
    CharacterProfile,
    Outline,
    SceneCard,
    WorldBible,
)
from po_agent_novel.store import (
    AppendOutcome,
    CanonStore,
    ExtractionSource,
    InMemoryCanonStore,
    MockNovelStore,
    NovelStore,
    SceneSummary,
    SummaryRecord,
    content_hash,
    pending_assertions,
)

# 包版本，与 pyproject.toml 的 [project].version 保持一致。
__version__ = "0.1.0"

# __all__ 按用途分组，同时也是「允许宿主使用的全部符号」清单；
# 分组顺序与上方导入顺序一致，便于对照维护、避免 API 面失控。
__all__ = [
    "__version__",
    # 插槽
    "NOVEL_AGENT_NAME",
    "NOVEL_UTTERANCES",
    "build_novel_agent",
    "build_novel_graph",
    "NOVEL_CHAT_AGENT_NAME",
    "build_novel_chat_agent",
    # 连接级作者身份（宿主握手验出 uid 后绑定，正典读口据此盖归属章）
    "current_actor",
    "reset_actor",
    "set_actor",
    # 离线降级
    "OfflineNovelModel",
    "OfflineNovelChatModel",
    # 领域 schema
    "ArchivedBook",
    "BookDraft",
    "BookIdea",
    "ChapterDraft",
    "ChapterExtraction",
    "ChapterOutline",
    "CharacterList",
    "CharacterProfile",
    "Outline",
    "SceneCard",
    "WorldBible",
    # 数据层：协议 + 两套实现（进程内 / HTTP）
    "AppendOutcome",
    "CanonStore",
    "ExtractionSource",
    "HttpCanonStore",
    "HttpNovelStore",
    "InMemoryCanonStore",
    "MockNovelStore",
    "NovelStore",
    "NovelStoreError",
    "SceneSummary",
    "SummaryRecord",
    "content_hash",
    "pending_assertions",
    # L1 记忆装配（注入预算与编号的下沉点，宿主/测试都按它核对 §6）
    "Budgets",
    "compile_context",
]
