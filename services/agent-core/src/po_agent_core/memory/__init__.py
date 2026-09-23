"""记忆子系统：checkpointer 三策略 + 长期记忆 store。

短期记忆（线程内消息，支撑多轮与 interrupt 恢复）走
``CheckpointerManager``；跨会话的长期记忆（用户偏好、人设等）走
``StoreManager`` + ``user_namespace``。两者生命周期都归宿主：
延迟初始化 + 进程退出前显式 ``aclose()``。
"""

from po_agent_core.memory.checkpointer import CheckpointerManager
from po_agent_core.memory.store import StoreManager, user_namespace

__all__ = ["CheckpointerManager", "StoreManager", "user_namespace"]
