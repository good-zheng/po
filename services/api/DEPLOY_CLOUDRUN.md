# po API 部署到微信云托管（镜像模式）

`services/api`（Spring Boot 4.1.1 / Java 17，端口 8080，context-path `/api`）以**自定义镜像**方式部署到微信云托管。云托管底层跑容器，不依赖平台内置 JDK，因此 Java 17 由镜像自带即可，无需平台提供。

## 0. 密钥从哪来

生产环境变量集中记在 **`application-prod.json`**（与本文同目录）。该文件已被 `.gitignore`/`.dockerignore` 排除——**不入库、不进镜像**，只作为把键值填入云托管环境变量控制台的清单。密钥本身不写进本文档。

> 上线后请去腾讯云/CAM/讯飞逐项轮换这些已明文存在过的密钥。

## 1. 一键脚本

```bash
# 前置：Docker Desktop 需在运行；先用 TCR「访问凭证」固定密码登录（密码非登录密码；交互式，需在本终端输入）
docker login ccr.ccs.tencentyun.com --username=100053273154

# 构建 + 推送（默认走国内加速镜像，适合 Docker Hub 被墙的本地）
pnpm api:deploy                      # 等价于 bash scripts/deploy-api.sh
pnpm api:deploy:official             # 云端/梯子环境用官方 Docker Hub 基础镜像

# 换 tag / 换镜像仓库命名空间：Git Bash 下用环境变量覆盖（cmd/PowerShell 不认这种写法，直接改脚本默认值）
TAG=v2 bash scripts/deploy-api.sh
NAMESPACE=... REPO=... bash scripts/deploy-api.sh
```

脚本产物镜像地址形如：
`ccr.ccs.tencentyun.com/tcb-100053273154-byrm/ca-eyxzseoz_po:prod`

## 2. 手动等价命令

构建上下文是 `services/api`（Dockerfile 用相对路径 `COPY shared/src ...`）：

```bash
cd services/api
docker build \
  --build-arg BUILD_IMAGE=docker.m.daocloud.io/library/maven:3.9-eclipse-temurin-17 \
  --build-arg RUNTIME_IMAGE=docker.m.daocloud.io/library/eclipse-temurin:17-jre \
  -t ccr.ccs.tencentyun.com/tcb-100053273154-byrm/ca-eyxzseoz_po:prod .
docker push ccr.ccs.tencentyun.com/tcb-100053273154-byrm/ca-eyxzseoz_po:prod
```

## 3. Dockerfile 的三处国内加速（本地被墙时才需要）

1. 两条 `FROM` 用 build-arg 参数化，默认前缀 `docker.m.daocloud.io/library/`；云端可 `USE_OFFICIAL_IMAGES=1`（或直接 `--build-arg` 传官方镜像名）覆盖。
2. **不要加** `# syntax=docker/dockerfile:1`——它会触发 BuildKit 去 Docker Hub 拉 `docker/dockerfile:1` 前端镜像而被墙。当前语法（`ARG` 在 `FROM` 前）内置解析器即支持。
3. `services/api/maven-settings.xml` 把 Maven Central 镜像到阿里云，`COPY` 进构建阶段 `/root/.m2/settings.xml`，否则 `mvn dependency:go-offline` 极慢/超时。

`services/api/.dockerignore` 单独一份：compose 的 build 上下文是 `services/api`，根 `.dockerignore` 不作用于此，须在此排除 `application-local.yaml`/`application-prod.*`。

## 4. 云托管「从镜像部署」控制台配置

| 项 | 值 |
| --- | --- |
| 部署方式 | 从镜像部署 |
| 镜像地址 | `ccr.ccs.tencentyun.com/tcb-100053273154-byrm/ca-eyxzseoz_po:<TAG>` |
| 监听端口 | `8080` |
| 健康检查路径 | `/api/actuator/health`（含 `/api` 前缀） |
| 最小副本数 | ≥ 1（避免冷启动打断 WS/语音） |
| 公网出站访问 | 开启（api 需访问讯飞 `tts-api.xfyun.cn`、腾讯云 COS） |
| 环境变量 | 照 `application-prod.json` 逐条填；**`SPRING_PROFILES_ACTIVE=prod` 必填**，否则回落到打包内 `local` profile 的 localhost 数据源导致连库失败；**`WECHAT_API_BASE_URL=http://api.weixin.qq.com` 必填**（见第 5 节 PKIX） |

## 5. 部署后高频坑

- **连不上数据库**（`Communications link failure`）：`SPRING_DATASOURCE_URL` 建议用 MySQL 的**内网/VPC** 地址；在 CDB 安全组放行容器所在 VPC；`po` 库与账号需预先创建（`schema.sql` 只建表不建库），必要时 `useSSL=true`。
- **微信登录 PKIX 证书失败**（`jscode2session` 报 `PKIX path building failed`）：云托管把容器对外 https 走内网代理，返回证书不在 JDK cacerts 内（镜像本身信任库正常，含 DigiCert 根 → 反证拿到的不是微信公网证书）。结论：**在云托管里访问 `api.weixin.qq.com` 必须走 http，不能用 https**。**方案 A（采用）**：
  1. 只加环境变量 `WECHAT_API_BASE_URL=http://api.weixin.qq.com` → 新建版本并发布（代码用 `wechat.mini.api-base-url` 拼接口，本地默认 https；镜像已含该配置项，**不用重新构建镜像**），真机试登录。绝大多数情况这一步就够了。
  2. 若 http 仍失败（连接被拒 / `errcode 40164` IP 白名单 / 未授权），才说明「开放接口服务」没开或权限没绑：去**微信侧**云托管控制台（`cloud.weixin.qq.com/cloudrun`，或小程序后台 → 云托管；**不是**腾讯云 CloudBase 控制台），左侧「微信开放能力」→「开放接口服务」（老版叫「云调用」），它是**环境级**开关，不在服务详情页里；开启后需重新发版。
  3. 开启开放接口服务后，需 access_token 的接口不必自己传（网关注入）。`jscode2session` 不需要 token；`getPhoneNumber` 需要，但该流程目前搁置。
  4. 小程序、Expo 均无需改，两端共用后端 jscode2session 逻辑。
  **方案 B（备选，A 的第 2 步也走不通时）**：把 `apps/cooking-mini/src/lib/api/client.ts` 从 `Taro.request` 换成云调用 `Taro.cloud.callContainer`，云托管直接注入 `X-WX-OPENID`，后端 `AuthServiceImpl.resolveOpenId` 已优先读该头、无头才回退 jscode2session，服务端可完全不碰微信接口。代价：普通 `wx.request` 直连域名不会注入此头（必须改造客户端），且 Expo 端用不了 callContainer。
- **免域名校验不全覆盖**：云托管免域名 HTTP 校验管 `request/uploadFile`，但**不管 WebSocket 与 audio/COS 播放**。小程序「开发设置-服务器域名」需另加：
  - socket 合法域名：聊天服务的 `wss://…run.tcloudbase.com`
  - downloadFile 合法域名：COS `https://7072-prod-d7g3zal0655a67232-1496875399.cos.ap-shanghai.myqcloud.com`
- **profile 泄漏**：绝不要把 `application-prod.yaml`/`application-local.yaml` 打进镜像；一律 env 注入。

## 6. chat 与 Redis 服务

已单独成文：**`services/chat/DEPLOY_CLOUDRUN.md`**（`pnpm chat:deploy` / `pnpm redis:deploy`、Redis Stack 镜像的必要性、
内网调用地址怎么填、WS 域名白名单、api 侧 `SPRING_DATA_REDIS_*` 与 actuator redis 探针的关系）。
