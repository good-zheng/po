# syntax=docker/dockerfile:1
FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN useradd --system --create-home appuser

COPY pyproject.toml ./
COPY app ./app
RUN pip install .

USER appuser
EXPOSE 5090

# config.py 默认 host=0.0.0.0 / port=5090，可通过 PY_SERVER_* 环境变量覆盖
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5090"]
