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

from app.config import get_settings

# 日志落盘在「收集阶段」就要关掉，所以写在模块顶层而不是夹具里：pytest 先 import
# 本文件，再 import 测试模块，而 ``app.main`` 的模块级 ``app = create_app()`` 在
# import 时就会按 Settings 默认值挂上文件 handler 并在 services/chat/.tmp 下建目录。
# 夹具要等到用例开始才跑，那时目录已经建好了。
os.environ["PY_SERVER_LOG_FILE"] = ""
get_settings.cache_clear()


@pytest.fixture(autouse=True)
def _isolate_host_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in [k for k in os.environ if k.upper().startswith("AGENT_CORE_")]:
        monkeypatch.delenv(key, raising=False)
    # ``Settings.log_file`` 有意带非空默认值（保证真实运行一定落盘），而几乎所有
    # 用例都会 ``create_app()``——不关掉的话每个用例都往 services/chat/.tmp 里挂一个
    # 文件 handler，root 的 handler 也会越积越多，同一条记录被写 N 遍。
    # 落盘本身由 tests/test_logging_sink.py 显式开启验证。
    monkeypatch.setenv("PY_SERVER_LOG_FILE", "")
    get_settings.cache_clear()
    yield
    # 用例内部可能再 setenv + cache_clear，收尾清一次免得把脏 Settings 留给下个用例
    get_settings.cache_clear()
