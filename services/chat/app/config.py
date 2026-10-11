"""宿主服务自身的运行配置。

只承载「HTTP 服务怎么监听、允许谁跨域」这类宿主级参数；LLM Key、
checkpointer、意图路由等编排相关配置由 ``po-agent-core`` 的
``AgentCoreSettings`` 负责（``AGENT_CORE_`` 前缀），两者刻意分家：
把宿主参数与编排参数混在一个 Settings 里会让凭据散落到 host/port 同一处。

被调用方：:func:`app.main.create_app` 读取 CORS 白名单；端口/host 由
uvicorn 启动命令读取（不在代码内引用）。测试可通过清空 ``get_settings``
的缓存来注入自定义环境变量。
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """宿主设置：环境变量前缀 ``PY_SERVER_``，并自动加载当前工作目录的 ``.env``。

    使用 ``PY_SERVER_`` 前缀是为了与同进程/同 ``.env`` 文件中的
    ``AGENT_CORE_*`` 变量互不干扰。
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="PY_SERVER_",
        # 前缀只作用于环境变量：「同一份 .env 文件」里的键是无差别读入的，
        # 而 pydantic-settings 的 extra 默认就是 forbid——文件里那些给
        # po-agent-core 用的 AGENT_CORE_* 键会被判为非法输入并直接抛
        # ValidationError，于是「配好 LLM 的 .env」反而让服务起不来。
        # 显式 ignore 才与上面「两个命名空间共用一个 .env」的设计一致。
        extra="ignore",
    )

    host: str = "0.0.0.0"
    port: int = 5090
    # 逗号分隔的字符串而非 list：pydantic-settings 对复杂类型的环境变量要求
    # JSON 语法，写成裸字符串更便于在 .env / 部署环境里直接维护。
    cors_origins: str = "http://localhost:8000,http://localhost:5173"

    # WS 握手的身份层（见 app/ws_auth.py）：票据由 Spring Boot 签也由它验，
    # 本服务既不加签 JWT 也不持 jwt.secret——那会把同一把密钥分发到第二个进程。
    api_base_url: str = "http://localhost:8080/api"
    # 与 Spring 侧 app.internal-token 同值；留空即「没配验票通道」，
    # 需要身份的插槽（novel-chat）因此一律拒连（宁缺不可放）
    internal_token: str = ""
    ticket_timeout_seconds: float = 5.0

    # 日志落盘（见 app/logging_setup.py）。默认开：事故里「进程静默退出」之所以
    # 无从判定，就是因为服务端磁盘上零记录——靠 .env 才开等于把坑留给下一个环境。
    # 相对路径按进程 cwd 解析：本机是 services/chat，容器里是 /app。
    # 留空即关闭落盘、只输出到 stderr（测试用它）。根 .gitignore 的 .tmp/ 与 *.log
    # 已覆盖默认路径，不会把日志带进提交。
    log_file: str = ".tmp/logs/chat.log"
    log_level: str = "INFO"

    @property
    def cors_origin_list(self) -> list[str]:
        """把逗号分隔的配置拆成 CORS 中间件需要的列表，并丢弃空项。

        允许写 ``a, b,`` 这类带空格/尾逗号的形式，避免部署时因手写格式
        导致中间件拿到空 origin 而整体失效。
        """
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """进程级单例：``.env`` 只解析一次，避免每个请求重复读盘。

    ``lru_cache`` 同时意味着运行期修改环境变量不会生效；测试若需覆盖配置，
    应先 ``get_settings.cache_clear()`` 再调用。
    """
    return Settings()
