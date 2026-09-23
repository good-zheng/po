# 做菜 App（Expo）技术方案与实施清单

> 状态：**已批准 v0.1，M0 代码完成，待真机验收**。按 §0 推荐方案执行；后续里程碑以本清单持续跟踪。

---

## 0. 需要先拍板的决策

| # | 决策项 | 选项 | 建议 | 影响 |
| --- | --- | --- | --- | --- |
| D1 | 目标平台 | A. iOS + Android<br>B. 先 Android 后 iOS<br>C. 先 Android 单端 | B | iOS 上架需 Apple Developer（$99/年）；双端同套代码，成本主要在测试与上架流程 |
| D2 | 后端 | A. **复用 `services/api`**（Spring Boot，已有 auth + recipes + uploads）<br>B. 新建独立后端<br>C. BAAS（Supabase/Firebase） | A | 仓库已有完整菜谱 CRUD + JWT + 分类 + 头像上传；管理端 `admin-web` 可直接录入内容，App 侧以读为主，投入最小 |
| D3 | 首发市场 | A. Google Play + App Store<br>B. 国内安卓市场（华为/小米/OV/应用宝）<br>C. 两者都要 | A 先行 | 国内市场需要软著、App 备案、各渠道单独审核，周期长；先海外后国内更平滑 |
| D4 | UI 方案 | A. NativeWind（Tailwind 语法）<br>B. 原生 StyleSheet + 主题对象<br>C. Tamagui 组件库 | A | 与个人开发效率契合，类名即样式；B 最稳但写起来啰嗦 |
| D5 | 离线能力 | A. 仅缓存已看过的菜谱（MMKV）<br>B. 完整离线包（SQLite，可离线浏览全部） | A 先行 | B 需要数据同步设计，放二期 |
| D6 | 是否接微信/Apple 登录 | A. 暂不，仅账号密码<br>B. 首发带三方登录 | A | 三方登录各需平台资质与审核，先跑通再补 |

> 决定：采用上表全部建议（D1=B、D2=A、D3=A、D4=A、D5=A、D6=A）。

---

## 1. 现有资产盘点（可直接复用）

| 资产 | 位置 | App 侧用途 |
| --- | --- | --- |
| JWT 认证 | `POST /api/auth/login`、`POST /api/auth/register` | 登录注册，token 存 SecureStore |
| 用户资料 | `GET/PUT /api/users/me`、`POST /api/users/me/avatar`、`PUT /api/users/me/password` | 个人中心、改密、头像 |
| 菜谱 CRUD | `GET /api/recipes`（分页列表）、`GET /api/recipes/{id}`、`GET /api/recipes/mine`、`POST/PUT/DELETE` | 首页列表、详情、我的菜谱 |
| 菜谱分类 | `GET /api/recipe-categories` | 分类页、筛选 |
| 文件上传 | 后端 `uploads_data` 卷 + Result 统一响应 | 菜谱图、成品照 |
| 共享类型 | `packages/types/src/recipe.ts`、`identity.ts`、`api.ts` | 前后端同一份 TS 类型，App 直接 import `@po/types` |
| 内容管理 | `apps/admin-web`（已有菜谱管理页） | 菜谱内容由管理端维护，App 只读为主，UGC 供稿走「我的菜谱」 |
| 部署底座 | docker-compose（mysql/redis/api/web） | App 直接连生产网关或新增移动端网关路由 |

**新增工作集中在 App 本身**：后端预计只需少量移动端友好调整（见 §7 风险中的后端改动项）。

---

## 2. 技术选型清单

### 2.1 核心框架

| 项 | 选型 | 说明 |
| --- | --- | --- |
| 框架 | Expo（最新稳定 SDK）+ React Native | 全 Expo 托管工作流，`npx create-expo-app` 起步；New Architecture 默认启用 |
| 语言 | TypeScript strict | 与仓库现有前端一致 |
| 路由 | expo-router（文件式路由） | `app/` 目录即路由，支持 tabs/stack/modal，深链天然支持 |
| 包管理 | pnpm workspace（仓库根） | App 放 `apps/cooking-app`，与 admin-web 平级 |

### 2.2 数据与状态

| 项 | 选型 | 说明 |
| --- | --- | --- |
| 服务端状态 | TanStack Query v5 | 与 admin-web 同款，缓存/重试/分页加载成熟 |
| 本地状态 | React 内建 + 少量 context | 做菜模式等局部状态，不上重型全局方案 |
| 网络层 | axios 实例 + 拦截器 | baseURL 指向后端；token 注入与 401 统一处理 |
| 类型 | `@po/types`（workspace 依赖） | 请求/响应类型复用，编译期对齐后端 DTO |

### 2.3 UI 与交互

| 项 | 选型 | 说明 |
| --- | --- | --- |
| 样式 | NativeWind v4（按 D4 决策） | Tailwind 语法；全局主题色/字体走配置 |
| 动画/手势 | react-native-reanimated + react-native-gesture-handler | 步骤卡片滑动翻页、列表动画 |
| 图片 | expo-image | 内存/磁盘缓存完善，做菜场景弱网友好 |
| 视频（如有步骤视频） | expo-video | 二期再定 |
| 语音播报 | expo-speech | 「做菜模式」念步骤，双手不沾屏幕（P1） |
| 防熄屏 | expo-keep-awake | 做菜过程中屏幕常亮 |
| 深色模式 | useColorScheme + NativeWind dark: | 一等公民支持 |

### 2.4 本地存储与设备能力

| 项 | 选型 | 存什么 |
| --- | --- | --- |
| token | expo-secure-store | JWT（Keychain/Keystore 加密） |
| KV 缓存 | react-native-mmkv | 收藏的菜谱 JSON、搜索历史、偏好设置 |
| 结构化离线（二期） | expo-sqlite | 全量菜谱离线包 |
| 拍照/选图 | expo-image-picker（相机用 expo-camera，按需） | 成品照、我的菜谱配图 |
| 推送 | expo-notifications | 提前解冻/腌制提醒（P1） |
| 分享 | RN Share API → react-native-share | 菜谱分享卡片（P2） |

### 2.5 工程化与质量

| 项 | 选型 | 说明 |
| --- | --- | --- |
| Lint/格式化 | Biome（与仓库一致）+ tsc --noEmit | 统一在根脚本增加 `mobile:lint` / `mobile:typecheck` |
| 单测 | jest-expo | 纯函数：份量缩放、单位换算、计时器逻辑 |
| 组件测试 | @testing-library/react-native | 菜谱卡片、步骤导航等关键组件 |
| E2E | Maestro（YAML 流程） | 对 Expo 支持最好，真机/模拟器均可跑 |
| API Mock | MSW | 组件与 E2E 的接口隔离 |
| CI | GitHub Actions 新增 mobile job | lint + typecheck + 单测；构建走 EAS 手动/按 tag |

---

## 3. 功能需求清单（优先级）

### P0（首发必须有）

- [x] 用户名 + 密码注册登录，token 持久化，登出（后端未提供手机号登录）
- [ ] 菜谱首页：分页列表、下拉刷新、上拉加载
- [ ] 分类页 + 按分类筛选
- [ ] 搜索（关键词，含历史记录）
- [ ] 菜谱详情：封面大图、食材表（含用量）、步骤图文、时长/难度/份量
- [ ] 做菜模式：步骤大字号横竖屏卡片、上一步/下一步、防熄屏
- [ ] 收藏 / 取消收藏（本地 MMKV 起步，登录后落库需后端新增收藏端点，见 §7）
- [ ] 个人中心：资料、头像上传、改密、登出

### P1（1.x 版本）

- [ ] 步骤计时器（每个步骤可设时长，倒计时 + 本地通知提醒）
- [ ] 语音播报步骤 / 音量键翻页（免触操作）
- [ ] 份量缩放（2 人份 ↔ 4 人份，用量按比例换算）
- [ ] 购物清单：从菜谱一键汇总食材，可勾选、可合并去重
- [ ] 提醒类推送：腌制/解冻提前提醒
- [ ] 浏览历史、最近做过的菜
- [ ] 单位换算（克/毫升/勺/杯，中西对照）

### P2（二期）

- [ ] UGC：我的菜谱创建/编辑（`/api/recipes` POST/PUT 已有，差 App 端表单）
- [ ] 成品拍照打卡墙
- [ ] 步骤视频
- [ ] 离线全量包（SQLite 同步）
- [ ] 分享卡片海报生成
- [ ] 忌口/过敏原标签与过滤
- [ ] 一周菜单规划

---

## 4. 实施步骤（里程碑）

> 每个 M 都是可运行、可演示的增量；M1 结束即能在真机看到真数据。

### M0 工程骨架（0.5~1 周）

- [x] `apps/cooking-app` 落入 pnpm workspace；create-expo-app（TypeScript + expo-router 模板）
- [x] Metro 适配 monorepo（pnpm 符号链接 → `node-linker=hoisted` 或 resolver 配置，见 §7）
- [x] 依赖 `@po/types`（workspace:*）；axios 实例 + Result 响应拦截器骨架
- [x] 主题色/字体/深色模式基座；Biome + tsc 接入根脚本
- [x] CI mobile job（lint + typecheck + jest）
- [x] 浏览器中渲染真实 `/api/recipes` 分页数据，并核验四个标签页
- [ ] 真机用 Expo Go 连本地 dev server 跑通「Hello + 请求一次 /api/recipes」

**验收**：浏览器已渲染后端返回的菜谱列表第一页；待在真机 Expo Go 中完成同一验收。

### M1 菜谱浏览（1~2 周）

- 首页列表（分页/刷新）、分类页、搜索（含历史）、详情页（食材表 + 步骤）
- 图片加载与占位（expo-image priority）
- 空态/错误态/骨架屏
- MSW mock 补齐，组件测试覆盖列表与详情

**验收**：断网重连、快速滚动、深色模式下无明显缺陷。

### M2 做菜模式（1 周）

- 步骤卡片全屏翻页（reanimated）、防熄屏、横竖屏
- 步骤计时器 + 本地通知；语音播报（P1 项，若时间富余一并做）
- 做菜进度保存（中断续做）

**验收**：跟做一道 5 步以上的菜，中途锁屏/来电不丢进度。

### M3 账号与收藏（1 周）

- [x] 登录/注册/登出、token SecureStore、401 统一跳转
- [ ] 收藏（先 MMKV 本地，若后端已加收藏端点则同步）
- [ ] 个人中心 + 头像上传 + 改密

**验收**：登录、注册、登出与 401 跳转已实现并有组件测试覆盖；待真机验证杀进程重启登录态保持、token 过期引导重登。

### M4 媒体与分享（0.5~1 周）

- image-picker 接头像与成品照；上传走后端 uploads
- 分享菜单（P2 海报则后置）

### M5 提醒与购物清单（1 周，P1 内核）

- 购物清单页 + 菜谱一键汇总
- expo-notifications 定时提醒（需 dev build，Expo Go 不支持完整推送）

### M6 打磨与上线准备（1~2 周）

- 性能（列表虚拟化、图片预算）、无障碍标签、i18n（若只中文可后置）
- 应用图标/启动屏（app.json + eas 配置）、隐私政策页
- 生产环境后端网关确认（App 直连 `https://<域名>`，见 §7）
- TestFlight / Play 内部测试 → 灰度 → 提审

---

## 5. 测试方案

| 层次 | 工具 | 覆盖对象 | 运行时机 |
| --- | --- | --- | --- |
| 静态 | Biome + tsc | 全量 | 每次 commit（lint-staged）+ CI |
| 单元 | jest-expo | 份量换算、单位换算、计时器、收藏去重逻辑 | CI |
| 组件 | RNTL + MSW | 菜谱卡片、步骤翻页、登录表单 | CI |
| E2E | Maestro | 登录→浏览→做菜模式全程、收藏流程 | 发版前手动/按 tag |
| 接口联调 | 本地全套（docker compose 或本地三件套） | 真机连 dev server，走与生产一致的网关 | 每个里程碑验收 |
| 真机矩阵 | 至少 1×iOS + 2×Android（不同厂商） | 权限弹窗、深色模式、熄屏、弱网 | 发版前 |
| 灰度 | TestFlight / Play 内部轨道 | 崩溃率、接口错误率 | 提审前 1 周 |

关键冒烟脚本（真机）：

1. 冷启动 ≤ 3s 出列表；2. 断网打开详情→恢复→图片补载；3. 做菜模式锁屏 10 分钟回来续做；4. 登录态跨重启保持；5. 低电量下推送提醒准时。

---

## 6. 上线与分发

### 6.1 构建通道（EAS）

- `eas.json` 三 profile：`development`（dev client）/ `preview`（内测 apk/ipa）/ `production`
- Android：`eas build -p android --profile preview` 出 apk 给内测；production 出 aab
- iOS：EAS 云构建免 Mac；证书与描述文件首次由 EAS 托管生成

### 6.2 商店提审

| 商店 | 账号费用 | 流程要点 |
| --- | --- | --- |
| Google Play | $25 一次性 | 内部测试轨道 → 封闭/公开测试 → 生产；需隐私政策 URL、内容分级问卷 |
| App Store | $99/年 | TestFlight 内测（100 内部/10000 外部）→ 提审；首发建议先 TestFlight 打磨 |
| 国内安卓（二期） | 各渠道免费但门槛高 | 软著、App 备案（工信部）、部分渠道需企业账号；逐家单独审核 |

### 6.3 OTA 热更新（EAS Update）

- JS/资源层改动免提审直接推（原生模块变更仍需走商店）
- 通道：production 稳定 / staging 内部验证；回滚一条命令
- 做菜 App 内容型属性强，OTA 频率预期较高，值得一开始就配好

### 6.4 发布节奏建议

内测（preview 包 + 蒲公英类工具或直接 apk）→ TestFlight/内部轨道 1~2 周 → 提审 → 分阶段放量（Play 按百分比；iOS 手动 phased release）。

---

## 7. 风险与注意事项

| # | 风险 | 说明与对策 |
| --- | --- | --- |
| R1 | **本机 DLP 限制 EAS 上传** | 本机非浏览器进程对外上传在 ~9KB 即被切断（git/curl 已验证）。`eas build`（上传项目）/ `eas submit`（上传包）/ `eas update` 均走终端进程，**大概率失败**。对策：① Android 用 `eas build --local` 本地构建产 aab，再经**浏览器**登录 Play Console 网页上传（浏览器是白名单通道）；② iOS 云构建若被切断，考虑公司外网络环境操作，或换机器；③ 上线前先用一个 hello-world 工程试一次完整链路，把网络问题提前暴露 |
| R2 | pnpm workspace + Metro | Metro 对 pnpm 符号链接敏感：`.npmrc` 设 `node-linker=hoisted`（影响整仓）或 Metro `watchFolders` + resolver 配置。M0 第一件事就是打通，卡住则退化为独立目录 + types 用 npm 包版本号引用 |
| R3 | Expo Go 能力边界 | 推送、部分原生模块在 Expo Go 里受限 → M3 起切 dev build（`eas build --profile development` 或 `npx expo run:android`） |
| R4 | 后端需小改 | ① 收藏端点目前没有（identity/recipe 均无 favorite 相关），要么 M3 前加 `favorites` 表 + CRUD，要么 App 先纯本地收藏；② 列表接口若移动端字段过重需精简 DTO；③ 生产环境需 HTTPS 域名 + 网关对 App 开放（当前 compose 仅 `web:8000`，App 无法直连容器内网 api） |
| R5 | JWT 无 refresh | 现有 token 默认 24h 过期且无刷新端点 → App 侧策略：401 时静默用记住的凭据重登一次，失败才引导手动登录；或后端加 refresh（二期） |
| R6 | 图片体积 | 菜谱大图在弱网/流量下的加载策略：CDN 或后端加缩略图尺寸参数；M1 先用 expo-image 的缩放与优先级兜底 |
| R7 | 合规 | 隐私政策页（商店硬性要求）；国内分发另需软著 + 备案；收集了手机号/头像需在政策中声明 |

---

## 8. 下一步

1. 你评审本清单，对 §0 的 D1~D6 拍板（或提出修改）
2. 按决策裁剪 §2~§6（例如 D3 选国内则 §6.2 换轨）
3. 从 M0 开始动代码（届时先打通 monorepo + Metro + CI 这三个基建点，再进功能）

---

*生成于 2026-09-21，基于仓库当前状态（main @ 2d1b7ee）：后端 recipes/auth/users 端点与 `@po/types` 均已就绪。*
