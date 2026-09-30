---
name: wiki-capture
description: 任务收尾时把已验证、反直觉、下次还会踩的经验追加进 goodzheng-dev-wiki 知识库并推送。当用户说"沉淀一下""记进知识库""补进 wiki""这条经验存下来""更新知识中心"，或刚完成一个涉及平台约束、部署链路、小程序/云托管坑、后端契约的任务时使用。不用于记录能从代码直接读出的事实、密钥与平台常量。
---

# 知识库边开发边沉淀

## Overview

把沉淀做成任务收尾的一个动作：三问筛掉流水账，路由表决定写进哪篇文档，脚本负责 clone→闸门→push。

## 第一关：三问（全部为「是」才写）

1. 反直觉，或踩过一次才知道的吗？
2. 已在代码、配置或真实命令里验证过，不是推测？
3. 下次还会遇到（同项目复发，或跨项目可迁移）？

不写：改动流水账、`git log`/代码本身能读出的事实、任何密钥值、CloudRun 域名与环境 ID 这类平台常量（只写"必须从控制台复制"这条规则本身）。

## 第二关：分层，别双写

- **auto-memory**（`C:\Users\Administrator\.qoder-cn\projects\D--dev-po\memory\`）是草稿层：允许快、允许过期，同一会话内可反复更新。
- **wiki** 是定稿层：只收已经稳定、值得给别人看的结论。升级时把 memory 里的临时措辞改成结论 + 为什么 + 怎么避开，不要整段复制。
- **通用 Skill 不在这里写**：它的真源是本机用户级目录 `C:\Users\Administrator\.qoder-cn\skills\`，站点里的 `其他/skills/` 是定时任务的镜像，在 wiki 工作副本里手改会被下一次同步覆盖。要改通用技能就改用户级目录，然后跑 `pnpm wiki:sync`（或等下一轮定时）。
- **`.qoder/repowiki` 与 memory 不上站**：站点仓库是公开的，这两处含私有项目结构与内部标识。

## 第三关：去向路由

| 经验信号 | 目标文档 |
| --- | --- |
| 模块划分、MyBatis-Plus 约定、鉴权与 gating、聊天 WS 协议与降级、TTS/COS 契约 | `项目/叮叮厨/架构与模块.md` |
| 镜像构建与推送、云托管运行时、内网地址、加速源、合法域名、端口/健康检查 | `项目/叮叮厨/云托管部署.md` |
| WXSS 不支持属性、分包与体积、`project.config.json`、环境变量注入、Umi/Astro 配置生效时机 | `项目/叮叮厨/小程序平台坑.md` |
| 技术栈版本、工程入口与阅读顺序 | `项目/叮叮厨/README.md` |
| 站点自身的导航与维护约定 | `README.md`、`其他/README.md` |
| 跨项目可复用的方法论（排查六步法、审查清单、提交规范） | 改本机 `~/.qoder-cn/skills/<slug>/SKILL.md`，再由 `pnpm wiki:sync` 带上来；新增技能要在 `README.md` 导航表挂一行（先判问题类型，再判技术栈） |
| 以上都不匹配 | 新建 `项目/叮叮厨/<主题>.md` 或 `其他/<主题>.md`，并同步 `README.md` 的目录树与表格，否则侧栏导航看不到 |

## 操作流程

1. 准备工作副本（优先复用 `D:\dev\goodzheng-dev-wiki`，都没有才 clone 到 `.tmp/wiki`；脏则拒绝并列出未提交文件，绝不自动 reset）：

   ```bash
   node .qoder/skills/wiki-capture/scripts/wiki-capture.mjs prepare
   ```

   输出本地绝对路径、最近提交和各文档的 `## / ###` 大纲与行号，直接照着行号定位要追加的小节。

2. 用 Read + Edit 在该文档里追加。追加优先，不要新开文件（除非路由表无匹配）。每条记录带锚点：具体文件路径、配置键或命令，方便下次改到同一处时顺手校准，也防止过期。

3. 先闸门后推送：

   ```bash
   node .qoder/skills/wiki-capture/scripts/wiki-capture.mjs publish --message "<中文标题>" --dry-run
   node .qoder/skills/wiki-capture/scripts/wiki-capture.mjs publish --message "<中文标题>"
   ```

   `publish` 拒收非 `.md` 改动，并对新增行和未跟踪新文件做密钥扫描（`sk-`、`ghp_`、`-----BEGIN PRIVATE KEY-----`、`appsecret=`、长凭据赋值），命中即中止，不会先把脏内容推上 GitHub。

4. 收尾提醒一句：PowerWiki 每 180 秒自动同步该仓库，站点根为 `goodzheng`，`项目` / `其他` 两个分区直接来自仓库目录结构；本地预览用仓库根 `pnpm wiki:site`。通用 Skill 那一侧另有每 30 分钟的定时镜像任务（`goodzheng-wiki-sync`），不需要人工推送。

## 写作规范

- 中文，结论一句话在前，再写「为什么」和「怎么避开」；一节一个主题，段落式而非要点堆叠。
- 命令、路径、配置键用代码片段；不写"我之前如何如何"的叙事。
- 提交标题用汉字开头（该仓库无 commitlint，但保持与 po 仓库一致的习惯）。
- `push` 失败时脚本保留本地提交并提示重跑：先 `git pull --ff-only`，不要 amend 已推送的内容。

## Resources

- `scripts/wiki-capture.mjs` — `prepare`（复用/克隆工作副本 + 快进 + 大纲）、`status`（待提交清单）、`publish`（md-only + 密钥闸门 → commit → push，`--dry-run` 只校验不写）。工作副本按 `--dir` → `WIKI_DIR` → `../goodzheng-dev-wiki` → `.tmp/wiki` 顺序解析。
- `D:\dev\po\scripts\sync-dev-wiki.mjs` — 每 30 分钟把本机用户级 Skill 镜像到站点 `其他/skills/`（`pnpm wiki:sync` / `wiki:sync:dry` / `wiki:sync:bootstrap`）。
- `D:\dev\po\scripts\wiki-lib.mjs` — 两条链路共用的闸门：git 包装、待提交清单、扩展名白名单、密钥扫描。
- `D:\dev\po\scripts\WIKI_SYNC.md` — 真源/镜像归属表、计划任务注册与卸载、故障排查。
