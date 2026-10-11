# po-agent-cooking

po 的烹饪助手垂直 Agent（纯库）。把「找菜 → 看细节 → 报分类」封装成一个
ReAct 子图，经 agent-core 的插槽协议交给 `services/chat` 宿主编排，
最终由 `apps/cooking-app` 的「AI 指导」聊天页消费——该页不显式指定 `agent`，
靠 Layer1 意图路由委托过来。`apps/cooking-mini` 不再消费本插槽：小程序因个人主体禁 AI 类目
已在编译期摘除大模型 WS 链路（commit `6e70944`），全仓 `apps/cooking-mini/src` 里没有 `/ws/chat`。

- **不独立部署**：本包没有 FastAPI / 路由 / 端口，只提供 `build_cooking_agent`
  一个装配入口；宿主在 `services/chat/app/agent.py` 的 `_builtin_agents`
  登记它，未安装时宿主照常启动（仅跳过该插槽）。
- **不含模型配置**：模型走 agent-core 的角色槽位（本 Agent 用 `cooking`
  角色），菜谱数据源走 `COOKING_*` 前缀，两套配置互不干扰。

## 在编排中的位置

```
用户消息 → Layer1 意图路由（COOKING_UTTERANCES 语料）
             命中 → cooking 子图：START → agent ⇄ tools → END
             未命中 → chitchat 兜底
```

`COOKING_AGENT_NAME`（`agent.py:39` 的模块常量，值为 `cooking`，不是环境变量）必须与路由的
Route 名一致，命中后 supervisor 才委托过来。子图只认 `CoreState.messages`，菜谱数据不进
`artifacts`——工具结果文本就是前端渲染菜谱卡片的唯一数据源。

## 模块

| 模块 | 职责 |
| --- | --- |
| `agent` | 装配入口 `build_cooking_agent`：取模型 → 建 store → 装工具 → 返回 `VerticalAgent` |
| `config` | `CookingSettings`（环境变量前缀 `COOKING_`） |
| `recipes` | 领域模型 + `RecipeStore` 协议 + `HttpRecipeStore`（Java API）/ `MockRecipeStore` |
| `tools` | 三个工具：`search_recipes` / `get_recipe_detail` / `list_categories` |
| `graph` | ReAct 子图（手写节点，见下节） |
| `prompts` | 系统提示词与历史窗口上限 |
| `offline` | `OfflineCookingModel`：确定性离线降级模型 |

## 两个刻意的实现选择

**工具永不抛异常**。数据源失败被翻译成 `{"error": "..."}` 文本回给模型，
模型可以换说法重试或如实告知用户；若异常穿过 ToolNode，整轮对话会以
RUN_ERROR 终止，用户只看到一句「运行出错」。装配期同理不探活后端——后端
没起时表现为「暂时查不到」，优于让整个 chat 服务启动失败。

**手写 ReAct 节点而非 `create_react_agent`**。为了控制两件事：系统提示词
每轮现拼、不写进 state（写进去会被 checkpointer 层层累积，长会话里同一段
提示词重复几十次）；窗口按 HumanMessage 边界裁剪而不是按条数截断（否则会
产生「孤儿 ToolMessage」，模型直接报 tool_call_id 未找到而整轮失败）。

## 工具返回契约

工具返回值是 JSON 字符串（中文不转义），既是模型读的上下文，也是移动端
渲染菜谱卡片的唯一数据源，**字段名不得随意改动**：

| 工具 | 返回 |
| --- | --- |
| `search_recipes` | `{"count":n,"recipes":[{id,title,description,coverImageUrl,prepTime,cookTime,totalTime,difficulty,difficultyLabel,servings,category,tags}]}`；无命中时附 `hint` |
| `get_recipe_detail` | `{"found":true,"recipe":{…摘要字段, tips, ingredients:[{name,amount,unit,isEssential}], steps:[{stepNumber,content,duration}]}}`，不存在时 `{"found":false,"hint"}` |
| `list_categories` | `{"count":n,"categories":[...]}` |

失败一律 `{"error":"..."}`。移动端只认 `search_recipes` / `get_recipe_detail`
（见 `apps/cooking-app/src/lib/ai/agent-chat.ts` 的 `RECIPE_TOOLS`），其余工具
结果不下发卡片。

## 安装与测试

```powershell
# 在 services/chat 下（复用宿主的 .venv，本包无独立虚拟环境）
pip install -e "../agent-core[dev]"      # 先装底座
pip install -e "../agent-cooking[dev]"
```

或直接用仓库根命令：

```powershell
pnpm chat:install        # 按依赖序装 agent-core → agent-cooking → agent-talk → agent-novel → chat
pnpm agentcooking:test   # 运行本包 pytest（当前 34 个用例）
pnpm chat:test           # 含宿主的插槽装配测试（test_cooking_wiring.py）
```

`pnpm chat:install` 会连 talk / novel 一起装（`scripts/run-service.mjs` 里是固定五条），
单独装本包时也要先有 `agent-core`，否则 import 就失败。CI 的 Chat job 同样按这个顺序，
再依次跑四个包的 pytest。

测试不依赖外部服务与模型：数据源用 `MockRecipeStore`，模型用假模型或
`OfflineCookingModel`。

## 配置

环境变量前缀 `COOKING_`（与宿主写同一个 `.env`）：

| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| `COOKING_API_BASE_URL` | `http://localhost:8080/api` | 菜谱接口根地址（含 `/api` 前缀）。容器部署时改成 `http://api:8080/api` |
| `COOKING_REQUEST_TIMEOUT_SECONDS` | `10.0` | 单次请求超时；超时被翻译成可读错误回给模型，不中断整轮对话 |
| `COOKING_SEARCH_LIMIT` | `5` | 单次检索返回给模型的条数上限（越大上下文越长、越慢） |

模型不在本包配置：按 `AGENT_CORE_LLM_ROLES__COOKING__MODEL` 等槽位覆盖，
不配即回落 `AGENT_CORE_LLM_*` 默认槽位（见 `../agent-core/README.md`）。
菜谱读接口（`GET /recipes` 系列）在 Java 侧是 permitAll 的，Agent 无需
持有用户令牌。

## 降级链

| 失效点 | 表现 |
| --- | --- |
| 包未安装 | 宿主跳过本插槽，chitchat 兜底（`logger.info`） |
| 装配异常 | 同上，仅 `logger.warning`，不影响宿主启动 |
| 缺模型 key / provider 配错 | `OfflineCookingModel` 顶上，回复明确标注「离线模式」且不假装在查菜谱 |
| Java 后端不可用 | 工具返回 `{"error":...}`，模型如实告知「暂时查不到」 |
