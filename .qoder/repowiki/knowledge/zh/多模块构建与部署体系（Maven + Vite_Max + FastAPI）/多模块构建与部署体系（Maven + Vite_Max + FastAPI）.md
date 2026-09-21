---
kind: build_system
name: 多模块构建与部署体系（Maven + Vite/Max + FastAPI）
category: build_system
scope:
    - '**'
source_files:
    - java_server/po/pom.xml
    - java_server/po/mvnw
    - java_server/po/.mvn/wrapper/maven-wrapper.properties
    - py_server/pyproject.toml
    - py_server/app/main.py
    - web_client/po-admin/package.json
    - web_client/po-admin/.github/workflows/deploy.yml
    - web_client/shadcn-admin/package.json
    - web_client/shadcn-admin/vite.config.ts
    - web_client/shadcn-admin/netlify.toml
---

## 1. 使用的构建系统概览

本项目为前后端分离的全栈应用，包含三个独立子项目，各自使用语言生态的标准构建工具：
- Java 后端 (`java_server/po`)：基于 **Spring Boot 4.1.1**，通过 **Maven**（`pom.xml`）管理依赖与打包，使用 `spring-boot-maven-plugin` 生成可执行 JAR。
- Python 服务 (`py_server`)：依赖由 `pyproject.toml` 声明（fastapi、uvicorn[standard]、pydantic-settings；dev 可选组含 pytest/httpx），setuptools 打包 `app*` 包，通过 venv 中的 uvicorn 启动（`python -m uvicorn app.main:app`）。
- 前端双工程 (`web_client/po-admin` 与 `web_client/shadcn-admin`)：分别基于 **Umi Max**（Ant Design Pro 6.x）和 **Vite + TanStack Router**，通过各自的 `package.json` scripts 完成编译、测试与预览。

仓库根目录没有统一的 Makefile 或聚合构建脚本，各子工程独立构建、独立发布。

## 2. 关键文件与入口

| 子系统 | 构建/配置核心文件 | 作用 |
|---|---|---|
| Java 后端 | `java_server/po/pom.xml` | 定义 Spring Boot 父 POM、依赖、Lombok 注解处理器、`spring-boot-maven-plugin` 打包 |
| | `java_server/po/.mvn/wrapper/maven-wrapper.properties` | Maven Wrapper 版本与分发 URL |
| | `java_server/po/mvnw` / `mvnw.cmd` | 平台无关的 Maven Wrapper 启动脚本 |
| Python 服务 | `py_server/pyproject.toml` | 项目依赖（运行时 + dev 可选组）、setuptools 打包配置、pytest 配置 |
| | `py_server/app/main.py`、`app/config.py`、`.env.example` | 应用入口（`app.main:app`）与环境变量模板 |
| AntD Pro 前端 | `web_client/po-admin/package.json` | `max build` / `max dev` / `deploy` 等脚本，Node ≥22 要求 |
| | `web_client/po-admin/config/config.ts` | Umi Max 路由、代理、构建配置 |
| | `web_client/po-admin/.github/workflows/deploy.yml` | GitHub Pages 部署流水线 |
| shadcn-admin 前端 | `web_client/shadcn-admin/package.json` | `vite build` / `tsc -b` 编译脚本 |
| | `web_client/shadcn-admin/vite.config.ts` | Vite 插件、`/api` 代理到 `localhost:8080`、Playwright 浏览器测试 |
| | `web_client/shadcn-admin/netlify.toml` | SPA 单页重定向规则 |

## 3. 架构与约定

### Java 后端构建
- 继承 `org.springframework.boot:spring-boot-starter-parent:4.1.1`，Java 版本固定为 17。
- 通过 `maven-compiler-plugin` 显式注册 Lombok 注解处理器（compile 与 test-compile 两个阶段均启用）。
- 打包产物为可执行 JAR（由 spring-boot-maven-plugin 默认行为），未自定义 repackage 参数。
- 使用 Maven Wrapper（`mvnw`），确保团队与 CI 使用一致 Maven 版本。

### Python 服务
- 标准化构建：`python -m venv .venv` + `pip install -e ".[dev]"`（可编辑安装，setuptools 后端）。
- 启动：`./.venv/Scripts/python.exe -m uvicorn app.main:app --reload --port 5090`；配置通过 pydantic-settings 加载 `.env`（`PY_SERVER_` 前缀），提供 `.env.example` 模板。

### 前端构建
- **po-admin (Ant Design Pro)**：使用 Umi Max 的 `max build` 产出静态资源至 `dist/`；`npm run deploy` 会先设置 `CI=true` 再调用 `gh-pages` 推送到 GitHub Pages。开发环境通过 `UMI_ENV=dev`、`MOCK=none` 等环境变量区分模式。
- **shadcn-admin**：TypeScript 先行编译（`tsc -b`），再由 `vite build` 输出；开发时通过 Vite proxy 将 `/api` 转发到 `http://localhost:8080`（即 Java 后端端口）。测试使用 Vitest + Playwright 浏览器模式。
- 两个前端都通过 `vitest` 运行单元测试，shadcn-admin 额外提供 `test:browser` 与覆盖率脚本。

### 部署与 CI
- **po-admin**：GitHub Actions 在 `all-blocks` 分支 push 时触发，使用 `utooland/setup-utoo` 安装构建工具并执行 `ut build`，再通过 `peaceiris/actions-gh-pages` 发布到 `preview.pro.ant.design`。
- **shadcn-admin**：通过 Netlify 托管（`netlify.toml` 配置 SPA 回退路由），仓库附带 `ci.yml` 与 `stale.yml` 工作流。
- 后端服务（Java、Python）在当前仓库中未发现 Dockerfile、docker-compose 或服务器端 CI 流水线，推测通过外部方式部署。

## 4. 约定与约束

- **Node 版本约束**：po-admin 通过 `engines.node >= 22.0.0` 强制 Node 版本。
- **Java 版本约束**：pom.xml 中 `<java.version>17</java.version>` 锁定 JDK 17。
- **Maven 版本一致性**：通过 `mvnw` 与 `.mvn/wrapper/maven-wrapper.properties` 保证所有开发者使用同一 Maven 发行版。
- **前端 API 代理约定**：shadcn-admin 的 `vite.config.ts` 将 `/api` 代理到 `http://localhost:8080`，与 Java 后端默认端口对齐；po-admin 通过 Umi 的 `proxy` 配置实现相同目的。
- **构建产物位置**：两个前端均输出到 `dist/` 目录，便于统一部署。
- **测试框架统一**：前端统一采用 Vitest（po-admin 直接集成，shadcn-admin 通过 `@vitest/browser-playwright` 支持浏览器测试）。
- **无顶层聚合构建**：仓库根不存在 `Makefile`、`build.sh` 或 `docker-compose.yml`，各子工程需单独进入目录执行对应构建命令。

## 5. 缺失项说明

当前仓库未包含以下常见构建工件：Dockerfile、Docker Compose、顶层 Makefile、后端 CI 流水线（仅前端有 GitHub Actions/Netlify）。因此本仓库的“构建系统”本质上是**多语言、多工具的并列式构建**，而非单一编排体系。