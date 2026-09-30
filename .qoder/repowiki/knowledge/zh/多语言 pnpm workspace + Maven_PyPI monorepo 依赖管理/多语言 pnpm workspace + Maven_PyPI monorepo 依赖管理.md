---
kind: dependency_management
name: 多语言 pnpm workspace + Maven/PyPI monorepo 依赖管理
category: dependency_management
scope:
    - '**'
source_files:
    - package.json
    - pnpm-workspace.yaml
    - .npmrc
    - pnpm-lock.yaml
    - apps/admin-web/package.json
    - packages/types/package.json
    - services/api/pom.xml
    - services/chat/pyproject.toml
    - services/agent-core/pyproject.toml
    - .github/workflows/ci.yml
---

## 1. 使用的系统与方法

仓库是一个跨语言的 monorepo，按语言分别采用各自的包管理器：
- **Node.js / TypeScript**：pnpm workspace（`package.json` + `pnpm-workspace.yaml` + `pnpm-lock.yaml`）。
- **Java (Spring Boot)**：Maven reactor（`services/api/pom.xml` 聚合 `shared` / `identity` / `recipe` / `api-bootstrap` 四个子模块）。
- **Python (FastAPI + Agent)**：PEP 621 `pyproject.toml`（`services/chat`、`services/agent-core`、`services/agent-cooking`），通过 `pip install -e` 以可编辑模式安装本地包。
- **Docker 镜像**：各服务目录自带 `Dockerfile`，由根 `docker-compose.yml` 编排 MySQL/Redis/API/Chat/Nginx。

## 2. 关键文件与位置

| 领域 | 关键文件 |
|---|---|
| Node 工作区 | `package.json`、`pnpm-workspace.yaml`、`pnpm-lock.yaml`、`.npmrc` |
| 前端应用 | `apps/admin-web/package.json`（`@po/admin`）、`apps/cooking-app/package.json`、`apps/cooking-mini/package.json` |
| 共享类型包 | `packages/types/package.json`（`@po/types`，`private: true`，仅发布 `dist`） |
| Java 聚合 POM | `services/api/pom.xml`（声明 Spring Boot 4.1.1 parent、`dependencyManagement` 统一 MyBatis-Plus 版本） |
| Python 聊天服务 | `services/chat/pyproject.toml`（依赖 `fastapi`、`uvicorn`、`po-agent-core`） |
| Python agent-core | `services/agent-core/pyproject.toml`（`langgraph`、`langchain-*`、`semantic-router`、`pydantic`） |
| CI 流水线 | `.github/workflows/ci.yml` |
| 根脚本 | `scripts/run-service.mjs`、`scripts/deploy-api.sh`、`scripts/deploy-chat.sh` |

## 3. 架构与约定

### 3.1 Node 层（pnpm workspace）
- 根 `package.json` 声明 `"packageManager": "pnpm@10.28.1"` 与 `engines.node >= 22`，并通过 `scripts` 暴露 `admin:*`、`mobile:*`、`mini:*`、`api:*`、`chat:*` 等统一入口，内部使用 `pnpm --filter <pkg>` 调用子包命令。
- `pnpm-workspace.yaml` 将 `apps/*`、`apps/*/cloudflare-worker`、`packages/*` 纳入工作区；`apps/admin-web` 通过 `"@po/types": "workspace:*"` 引用共享类型包，实现跨包零拷贝引用。
- `.npmrc` 设置 `strict-peer-dependencies=false`，放宽 peer dependency 校验。
- 所有 Node 依赖在根级 `pnpm-lock.yaml` 中锁定；CI 使用 `pnpm install --frozen-lockfile` 强制锁文件一致性。

### 3.2 Python 层（本地包 + PyPI）
- `services/agent-core` 和 `services/agent-cooking` 是**不在 PyPI 的本地库**，通过 `pip install -e '../agent-core[dev]'` 以可编辑模式安装；`services/chat` 在其 `dependencies` 中直接写 `po-agent-core`。
- CI 中显式按依赖顺序安装：先 `agent-core`，再 `agent-cooking`，最后 `chat`（见 `.github/workflows/ci.yml` 第 147–151 行注释说明）。
- 可选依赖通过 `[project.optional-dependencies]` 拆分：`redis`、`sqlite`、`dev` 等 extras，避免主环境引入不必要的运行时依赖。

### 3.3 Java 层（Maven reactor）
- 根 `services/api/pom.xml` 作为聚合 POM（`packaging=pom`），子模块 `shared` / `identity` / `recipe` / `api-bootstrap` 继承其 `<parent>`（Spring Boot 4.1.1）。
- 通过 `<dependencyManagement>` 集中声明 `mybatis-plus-spring-boot4-starter` 与 `mybatis-plus-jsqlparser` 的版本（3.5.17），子模块无需重复指定版本。
- Lombok 注解处理器通过 `<pluginManagement>` 在编译期注入，保证所有子模块一致。

### 3.4 构建产物与共享包
- `packages/types` 是 `private: true` 的内部包，不发布到 npm registry，只产出 `dist/index.d.ts` 与 `dist/index.js`，被 `@po/admin` 通过 `workspace:*` 引用。
- 根 `pnpm types:build` 先构建该包，再由 admin 的 lint/build/test 依赖它（CI 中显式执行 `pnpm types:build` 后再运行 `admin:lint`）。

## 4. 约定与约束

- **Node 依赖必须经 pnpm 安装并更新 `pnpm-lock.yaml`**：CI 使用 `--frozen-lockfile`，任何未提交的锁变更都会导致构建失败（`.github/workflows/ci.yml` 第 32、66 行）。
- **Node 运行时版本受 `engines.node >= 22.0.0` 与 `packageManager.pnpm@10.28.1` 约束**，CI 也固定 setup-node 为 node 22、pnpm action-setup 为 10.28.1。
- **peer dependency 宽松策略**：`.npmrc` 中 `strict-peer-dependencies=false` 允许子包存在 peer 冲突时仍完成安装。
- **Python 本地包必须先于消费者安装**：`services/chat/pyproject.toml` 的注释明确说明 `po-agent-core` 不在 PyPI，需先 `pip install -e '../agent-core[dev]'`；CI 严格遵循此顺序。
- **Java 第三方库版本集中在父 POM 的 `<dependencyManagement>`**：子模块引用 `com.baomidou:mybatis-plus-*` 时不写版本号，由父 POM 统一管控。
- **CI 缓存路径与依赖清单一一对应**：Node 用 `cache-dependency-path: pnpm-lock.yaml`，Java 用 `'services/api/**/pom.xml'`，Python 用三个 `pyproject.toml` 路径列表，确保缓存键随依赖变化失效。
- **无私有 npm registry 配置**：`.npmrc` 仅包含 `strict-peer-dependencies=false`，未配置 `registry` / `@scope:registry` / `NODE_AUTH_TOKEN`，表明依赖全部来自公共 npm registry。
- **无 vendored 第三方源码**：Node 依赖位于各 `node_modules/`（由 pnpm 生成），Java 依赖由 Maven 下载至本地仓库，Python 依赖由 pip 安装至 venv；仓库内没有 `vendor/`、`third_party/` 等 vendored 目录。