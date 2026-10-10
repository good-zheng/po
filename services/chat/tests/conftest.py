"""测试全局夹具：把用例与本机 ``services/chat/.env`` 隔离。

``semantic_router`` 被 import 时会执行一次 ``load_dotenv()``，而 python-dotenv
是从调用方文件所在目录逐级向上查找——本项目跑在 ``services/chat/.venv`` 里，
于是 ``services/chat/.env`` 的 ``AGENT_CORE_*`` 会写进 ``os.environ``。

构造 settings 时传 ``_env_file=None`` 只关掉「.env 文件源」，关不掉「环境变量源」。
于是本地配了真实 embedding 后，路由用例拿到的就不是「无 embedding ⇒ 关键词降级」
那条确定性分支：``test_ws`` 里一句「你好」会被语义路由判给某个垂直 Agent，
chitchat 回显断言随本机配置漂移。

下面这个夹具在每个用例开始前清掉 ``AGENT_CORE_*``；需要环境变量的用例照旧用
``monkeypatch.setenv`` 显式设置——夹具先执行，不会误清。
"""

from __future__ import annotations

import os

import pytest


@pytest.fixture(autouse=True)
def _isolate_host_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in [k for k in os.environ if k.upper().startswith("AGENT_CORE_")]:
        monkeypatch.delenv(key, raising=False)
