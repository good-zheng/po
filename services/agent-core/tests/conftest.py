"""测试全局夹具：把用例与本机 ``.env`` 隔离。

``semantic_router`` 被 import 时会执行一次 ``load_dotenv()``（见其
``encoders/cohere.py``），而 python-dotenv 是从调用方文件所在目录逐级向上
寻找 ``.env``——本项目三个 Python 包共用 ``services/chat/.venv``，于是它会
命中 ``services/chat/.env``，把其中的 ``AGENT_CORE_*`` 写进 ``os.environ``。

构造 settings 时传 ``_env_file=None`` 只关掉了「.env 文件源」，关不掉
「环境变量源」：只要宿主配了自己的 ``services/chat/.env``，本目录里断言
默认值的用例就会被真实配置顶掉（如 ``llm_provider`` 变成 deepseek）。

下面的 autouse 夹具在每个用例开始前清掉 ``AGENT_CORE_*``；需要环境变量的
用例照旧用 ``monkeypatch.setenv`` 显式设置——夹具先执行，不会误清。
"""

from __future__ import annotations

import os

import pytest


@pytest.fixture(autouse=True)
def _isolate_host_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in [k for k in os.environ if k.upper().startswith("AGENT_CORE_")]:
        monkeypatch.delenv(key, raising=False)
