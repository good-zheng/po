"""agent-core 的异常类型。

刻意只保留两个层级：宿主既可以用 ``except AgentCoreError`` 统一兜底，
也能单独区分配置类错误——装配降级链需要靠它判断「该降级到哪个后备组件」。
"""


class AgentCoreError(Exception):
    """agent-core 基础异常，宿主统一兜底的粒度。"""


class AgentCoreConfigError(AgentCoreError):
    """配置缺失或非法（如缺少 API Key、provider 无 embedding 预设）。

    抛错方是配置解析处（``llm.factory`` 等），捕获方是宿主装配层：
    它属于「预期内的控制流」，用来驱动降级（回显模型 / 关键词路由），
    而不是让服务启动失败。
    """
