"""po-agent-novel：小说创作垂直 Agent（经 po-agent-core 插槽接入 supervisor）。

本模块是包的对外门面：把插槽装配入口、子图工厂、离线模型、领域 schema 与
数据层协议统一提升到包根，宿主只需 ``from po_agent_novel import build_novel_agent``
即可装配（services/chat 的内置插槽装配正是这样引用的）。

依赖方向严格单向：本包依赖 po-agent-core（插槽协议、事件契约、CoreState），
core 不反向依赖本包——因此 novel 可独立测试、按需装卸，装配失败也不阻断宿主启动。
"""

# 下列导入即包根的公开 API 面重导出；符号语义见各自模块。
from po_agent_novel.agent import (
    NOVEL_AGENT_NAME,
    NOVEL_UTTERANCES,
    build_novel_agent,
)
from po_agent_novel.graph import build_novel_graph
from po_agent_novel.offline import OfflineNovelModel
from po_agent_novel.schemas import (
    ArchivedBook,
    BookDraft,
    BookIdea,
    ChapterDraft,
    ChapterOutline,
    CharacterList,
    CharacterProfile,
    Outline,
    Reflection,
)
from po_agent_novel.store import MockNovelStore, NovelStore

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
    # 离线降级
    "OfflineNovelModel",
    # 领域 schema
    "ArchivedBook",
    "BookDraft",
    "BookIdea",
    "ChapterDraft",
    "ChapterOutline",
    "CharacterList",
    "CharacterProfile",
    "Outline",
    "Reflection",
    # 数据层
    "MockNovelStore",
    "NovelStore",
]
