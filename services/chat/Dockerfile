# syntax=docker/dockerfile:1
# ==================== 运行阶段：FastAPI 宿主 + 垂直 Agent ====================
# 构建上下文必须是仓库根目录（本地包 po-agent-core / po-agent-cooking 不在 PyPI）：
#   docker build -f services/chat/Dockerfile .
FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN useradd --system --create-home appuser

# 三个本地包按依赖序安装：agent-core（编排核心）→ agent-cooking（烹饪插槽）→ chat（宿主）
COPY services/agent-core /packages/agent-core
COPY services/agent-cooking /packages/agent-cooking
COPY services/chat/pyproject.toml services/chat/app /packages/chat/
RUN pip install /packages/agent-core /packages/agent-cooking /packages/chat \
    && rm -rf /packages

WORKDIR /app
USER appuser
EXPOSE 5090

# config.py 默认 host=0.0.0.0 / port=5090，可通过 PY_SERVER_* 环境变量覆盖
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5090"]
