# po-chat

基于 FastAPI 的示例服务，提供 REST CRUD 接口与 WebSocket 流式对话端点。

## 快速开始

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
uvicorn app.main:app --reload --port 5090
```

启动后访问：

- 接口文档：http://localhost:5090/docs
- 健康检查：http://localhost:5090/api/health

## REST API

资源 `Item` 字段：`name`(必填)、`description`、`price`(>0)、`in_stock`，存储于内存（进程重启后数据丢失）。

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/api/health` | 健康检查 |
| GET | `/api/items` | 列表，支持 `skip`/`limit`/`q` 查询参数 |
| POST | `/api/items` | 新建（201） |
| GET | `/api/items/{id}` | 详情（404 不存在） |
| PUT | `/api/items/{id}` | 全量替换（404 不存在） |
| PATCH | `/api/items/{id}` | 局部更新（404 不存在） |
| DELETE | `/api/items/{id}` | 删除（204） |

## WebSocket

端点：`/ws/chat`

入站帧：

```json
{"type": "message", "content": "你好"}
{"type": "ping", "content": "可选"}
```

出站帧：`token`（流式分片）→ `done` 结束；`ping` 对应 `pong`；非法帧返回 `error`。

## 测试

```powershell
pytest
```

## 配置

环境变量（前缀 `PY_SERVER_`，可写入 `.env`，参考 `.env.example`）：

| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| `PY_SERVER_HOST` | `0.0.0.0` | 监听地址 |
| `PY_SERVER_PORT` | `5090` | 监听端口 |
| `PY_SERVER_CORS_ORIGINS` | 见 `.env.example` | 逗号分隔的跨域来源 |
