"""``app.config.Settings`` 的「共用一份 .env」回归测试。

本服务与 po-agent-core 刻意共用 ``services/chat/.env``：前者只认
``PY_SERVER_`` 前缀，后者只认 ``AGENT_CORE_``。但 pydantic-settings 的
``env_prefix`` 只过滤环境变量，对 ``.env`` 文件里的键是无差别读入的，且
新版本 ``extra`` 默认是 forbid——文件里只要出现 ``AGENT_CORE_*``，构造
``Settings()`` 就会抛 ``extra_forbidden``，「配好 LLM 的 .env」反而让服务
起不来。下面的用例锁住 ``extra="ignore"`` 这一修复。
"""

import os

import pytest

from app.config import Settings


def test_settings_ignores_foreign_namespace_in_shared_dotenv(
    tmp_path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / ".env").write_text(
        "PY_SERVER_PORT=6001\n"
        "AGENT_CORE_LLM_PROVIDER=deepseek\n"
        "AGENT_CORE_LLM_API_KEY=sk-not-a-real-key\n",
        encoding="utf-8",
    )
    # .env 按当前工作目录解析：切到临时目录以隔离本机真实配置
    monkeypatch.chdir(tmp_path)
    # 环境变量源优先级高于文件源，残留的 PY_SERVER_* 会盖掉文件里的端口
    for key in [k for k in os.environ if k.upper().startswith("PY_SERVER_")]:
        monkeypatch.delenv(key)

    settings = Settings()
    assert settings.port == 6001  # 本命名空间的键照常生效
    assert settings.host == "0.0.0.0"  # 文件未覆盖的项回落默认值
