# 基础镜像默认走国内加速镜像（Docker Hub 本地直连不通）；
# 云端/有代理时构建可 --build-arg RUNTIME_IMAGE=python:3.11-slim 覆盖回官方。
# 注意：不要在这里加 `# syntax=docker/dockerfile:1`——那会让 BuildKit 去 Docker Hub 拉
# docker/dockerfile:1 前端镜像，在本地网络下直接构建失败（ARG-before-FROM 内嵌解析器已支持）。
ARG RUNTIME_IMAGE=docker.m.daocloud.io/library/python:3.11-slim
# ==================== 运行阶段：FastAPI 宿主 + 垂直 Agent ====================
# 构建上下文必须是仓库根目录（本地包 po-agent-core / po-agent-cooking 不在 PyPI）：
#   docker build -f services/chat/Dockerfile .
FROM ${RUNTIME_IMAGE} AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# PyPI 默认源国内不可达，固定走清华镜像（pip 官方镜像站）
ENV PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple

RUN useradd --system --create-home appuser

# 两个本地库包按依赖序 pip 安装：agent-core（编排核心）→ agent-cooking（烹饪插槽）
# agent-core 必须带 [redis] extra：langgraph-checkpoint-redis 是可选依赖，
# 不装则 checkpointer=redis 会静默降级成 memory，Redis 部署等于白做。
COPY services/agent-core /packages/agent-core
COPY services/agent-cooking /packages/agent-cooking
RUN pip install '/packages/agent-core[redis]' /packages/agent-cooking \
        fastapi 'uvicorn[standard]' pydantic-settings \
    && rm -rf /packages

# 宿主 app/ 直接落到运行目录，不再走 pip 打包：一次构建里 po-chat 的 wheel 只有
# dist-info（1111 字节、零个 .py），镜像看着推成功、容器一起手就 ModuleNotFoundError。
WORKDIR /app
COPY services/chat/app /app/app

# 构建期冒烟：导入失败就让 docker build 直接失败，绝不再产出起不来的镜像
RUN python -c "import app.main; import langgraph.checkpoint.redis; print('chat image smoke ok')"

USER appuser
EXPOSE 5090

# config.py 默认 host=0.0.0.0 / port=5090，可通过 PY_SERVER_* 环境变量覆盖
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5090"]
