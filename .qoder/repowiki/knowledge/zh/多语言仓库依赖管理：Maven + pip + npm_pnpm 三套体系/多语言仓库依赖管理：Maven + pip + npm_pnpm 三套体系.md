---
kind: dependency_management
name: 多语言仓库依赖管理：Maven + pip + npm/pnpm 三套体系
category: dependency_management
scope:
    - '**'
source_files:
    - java_server/po/pom.xml
    - java_server/po/.mvn/wrapper/maven-wrapper.properties
    - py_server/pyproject.toml
    - web_client/po-admin/package.json
    - web_client/po-admin/package-lock.json
    - web_client/po-admin/.npmrc
    - web_client/shadcn-admin/package.json
    - web_client/shadcn-admin/pnpm-lock.yaml
    - web_client/shadcn-admin/pnpm-workspace.yaml
---

## 1. 使用的系统/方法

本仓库是一个全栈项目，包含 Java（Spring Boot）、Python（FastAPI）和两个前端工程（Ant Design Pro、shadcn-admin），每个子模块各自使用其生态的标准依赖管理工具：

- **Java 后端** (`java_server/po`)：使用 **Maven**，通过 `pom.xml` 声明依赖，继承 `spring-boot-starter-parent:4.1.1` 作为父 POM 统一管理 Spring 生态版本；使用 Maven Wrapper（`.mvn/wrapper/maven-wrapper.properties`，固定 `distributionUrl=https://repo.maven.apache.org/maven2/org/apache/maven/apache-maven/3.9.16/apache-maven-3.9.16-bin.zip`）保证构建环境一致。
- **Python 服务** (`py_server`)：使用 **pip + pyproject.toml**（setuptools 后端），以 `>=` 宽松版本约束声明 fastapi、uvicorn[standard]、pydantic-settings，dev 可选组含 pytest/httpx；可编辑安装（`pip install -e ".[dev]"`）；未提供锁定文件。
- **Ant Design Pro 前端** (`web_client/po-admin`)：使用 **npm**，通过 `package.json` 声明依赖与开发依赖，并附带 `package-lock.json` 锁定精确版本；通过 `.npmrc` 设置 `legacy-peer-deps=true` 兼容 Ant Design Pro 模板的 peer dependency 冲突；通过 `overrides` 将 `@umijs/plugins` 中的 `@ant-design/pro-components` 指向根依赖版本。
- **shadcn-admin 前端** (`web_client/shadcn-admin`)：使用 **pnpm**，通过 `package.json` 声明依赖，附带 `pnpm-lock.yaml` 与 `pnpm-workspace.yaml`（仅配置 `allowBuilds` 允许 `@clerk/shared` 与 `esbuild` 构建）；同时存在 `package-lock.json`，但实际由 pnpm 管理。

## 2. 关键文件

| 模块 | 关键文件 | 作用 |
|---|---|---|
| Java | `java_server/po/pom.xml` | 依赖声明、插件配置、Lombok annotation processor |
| Java | `java_server/po/.mvn/wrapper/maven-wrapper.properties` | 固定 Maven 3.9.16 分发地址 |
| Python | `py_server/pyproject.toml` | 运行时依赖 + dev 可选组 + setuptools/pytest 配置（无锁定文件） |
| 前端 A | `web_client/po-admin/package.json` | 依赖声明、scripts、`engines.node >= 22` |
| 前端 A | `web_client/po-admin/package-lock.json` | npm 精确锁 |
| 前端 A | `web_client/po-admin/.npmrc` | `legacy-peer-deps=true` |
| 前端 B | `web_client/shadcn-admin/package.json` | 依赖声明（pnpm） |
| 前端 B | `web_client/shadcn-admin/pnpm-lock.yaml` | pnpm 精确锁 |
| 前端 B | `web_client/shadcn-admin/pnpm-workspace.yaml` | workspace 构建白名单 |

## 3. 架构与约定

- **按模块隔离**：每个技术栈独立维护自己的依赖清单，不存在跨语言共享依赖或统一聚合 manifest。Java 不感知 Python/JS 依赖，反之亦然。
- **版本策略差异明显**：
  - Java 通过 `spring-boot-starter-parent` 的 BOM 间接管理 Spring 生态版本，第三方库（如 mybatis-plus-spring-boot4-starter 3.5.17、jjwt 0.12.6）在 pom 中显式指定版本。
  - Python 使用 `>=` 宽松语义（如 `fastapi>=0.115`、`uvicorn[standard]>=0.30`），没有锁定文件，每次安装可能获得最新兼容版本。
  - 前端均使用 `^` 主/次版本范围（如 `react: ^19.2.7`），并通过 lockfile 固化实际解析结果。
- **依赖覆盖与降级**：Ant Design Pro 通过 `overrides` 强制将 `@umijs/plugins` 内的 `@ant-design/pro-components` 替换为根依赖版本，解决模板自带的 peer dependency 冲突。
- **Redis 客户端替换**：Java 中通过 `<exclusions>` 排除 spring-boot-starter-data-redis 默认引入的 `lettuce-core`，改用 `redis.clients:jedis`，体现对底层客户端的显式控制。
- **Node 版本约束**：Ant Design Pro 通过 `engines.node >= 22.0.0` 声明最低 Node 版本。

## 4. 约定与约束

- **Maven 构建一致性**：通过 Maven Wrapper 固定 3.9.16 二进制分发 URL，避免不同机器上 Maven 版本差异导致构建不一致。
- **Lombok 注解处理器**：在 `maven-compiler-plugin` 的 `annotationProcessorPaths` 中显式注册 Lombok，确保编译期生成代码可用。
- **测试/开发依赖分离**：Java 使用 `<scope>test</scope>`（spring-boot-starter-test）、`<scope>runtime</scope>`（mysql-connector-j、jjwt-impl/jjwt-jackson）、`<optional>true</optional>`（lombok）区分依赖用途；前端同样严格区分 `dependencies` 与 `devDependencies`。
- **Python 无锁定约束**：`pyproject.toml` 未提供 lockfile（如 `uv.lock` / pip constraints 锁定版），属于“可复现性较弱”的管理方式，升级时行为不确定。
- **前端包管理器混用**：同一仓库内同时存在 npm（`package-lock.json`）与 pnpm（`pnpm-lock.yaml`）两套锁文件，分别对应两个前端子项目，互不干扰。
- **无私有仓库配置**：未发现 `.m2/settings.xml`、`~/.pypirc`、`.npmrc` 中配置私有 registry 的证据，所有依赖均从公共仓库（Maven Central、PyPI、npm registry）拉取。
- **无 vendoring**：Java 未使用 `lib/` 目录或 Shade 打包第三方 jar；Python 未使用 `vendor/`；前端未使用 `node_modules` 之外的源码级 vendoring（`node_modules` 本身是标准缓存目录）。