# 本地开发 → 知识库站点 的自动同步

站点仓库 `good-zheng/goodzheng-dev-wiki`（本机克隆 `D:\dev\goodzheng-dev-wiki`）由自建 PowerWiki 每 180 秒拉取，所以只要内容进了这个仓库的 `main`，站点就自动更新。本脚本只负责「让内容进仓库」这一步。

## 真源与镜像（方向唯一）

| 内容 | 真源 | 站点位置 | 由谁维护 |
| --- | --- | --- | --- |
| 通用 Skill（跨项目复用） | `C:\Users\Administrator\.qoder-cn\skills\` | `其他/skills/` | `pnpm wiki:sync`（定时）自动镜像 |
| 项目笔记（叮叮厨架构、部署、平台坑） | 站点仓库本身 | `项目/叮叮厨/` | 人工，走 `/wiki-capture` |
| 站点导航与维护约定 | 站点仓库本身 | `README.md`、`其他/README.md` | 人工，走 `/wiki-capture` |
| `po/.qoder/repowiki/`、`~/.qoder-cn/memory/` | 本地 | **不上站** | 仓库是公开的，这两处含私有项目结构与内部标识 |

改通用 Skill 就改本机用户级目录（Qoder 在任何项目都能加载它），不要在站点克隆里改 `其他/skills/**`——下一次同步会覆盖。

## 命令

```bash
pnpm wiki:sync          # 镜像 + 提交 + 推送
pnpm wiki:sync:dry      # 只打印计划
pnpm wiki:sync:bootstrap  # 换机时首次：把站点现有 Skill 落到本机用户级目录（本地非空则拒绝）
node scripts/sync-dev-wiki.mjs --no-push   # 只提交本地，先看看 diff
```

工作副本按 `--wiki` → `WIKI_DIR` → `../goodzheng-dev-wiki` → `po/.tmp/wiki` 顺序取第一个存在的 git 仓库。

## 站点本体（PowerWiki）

PowerWiki 是解压进来的上游代码，位于 `apps/power-wiki/`，整个目录已在 `.gitignore` 里。仓库根提供三个入口：

```bash
pnpm wiki:site            # 启动，读取 apps/power-wiki/config.json
pnpm wiki:site:dev        # nodemon，改源码即热重启
pnpm wiki:site:install    # 单独重装它的依赖
```

它虽然不入库，但目录匹配 `pnpm-workspace.yaml` 的 `apps/*`，仍是 workspace 成员：`apps/power-wiki/node_modules` 里全是指向根 store（`node_modules/.pnpm/express@…`）的软链。不要把 `!apps/power-wiki` 加回 workspace 配置——一旦排除，根 `pnpm install` 会把 express、marked、nodemon 这些包剪掉，站点下一次启动就 `MODULE_NOT_FOUND`。目录里自带的 `package-lock.json` 是上游 npm 遗留，不参与安装。

端口优先级 `PORT` > `config.json.port`（本机为 80）> 3150。Windows 下覆盖端口用 PowerShell：`$env:PORT=3150; pnpm wiki:site`，或改 `config.json`（本地副本，不进仓库）。`config.json` 里的 `gitRepo`、`mdPath`、`siteUrl`、`autoSyncInterval` 等同样是本地配置，站点每 180 秒拉的就是上面那个仓库，所以推送成功后最多等 3 分钟本地/线上都能看到新内容。

## 闸门（`scripts/wiki-lib.mjs`，人工与定时共用一套）

- 只发布白名单扩展名：`.md .txt .json .yaml .yml .js .cjs .mjs .py .sh`，其余跳过并在日志里告警；隐藏文件一律不取
- 落盘前先扫密钥（`sk-`、`ghp_`、私钥块、`appsecret=`、长凭据赋值），命中即中止且不写任何文件
- 待提交内容必须全部落在 `其他/skills/` 内，越界即中止
- 本地真源为空而站点有内容时拒绝执行（否则会删光线上 Skill），确认无误再加 `--force`

## 定时任务

每 30 分钟跑一次，日志追加到 `C:\Users\Administrator\.qoder-cn\wiki-sync.log`（每行一次运行；无变化也记一行）。注册与卸载用同一个脚本：

```powershell
.\scripts\register-wiki-sync-task.ps1                    # 注册（默认 30 分钟）
.\scripts\register-wiki-sync-task.ps1 -EveryMinutes 15    # 改周期需重新注册
.\scripts\register-wiki-sync-task.ps1 -Unregister         # 卸载
```

任务在当前用户登录态下运行；`-StartWhenAvailable` 只补一次错过的运行，长期关机期间不会同步，开机后下一轮自动追上。手动验证：`Start-ScheduledTask -TaskName goodzheng-wiki-sync` 后看 `Get-ScheduledTaskInfo -TaskName goodzheng-wiki-sync` 的 LastTaskResult 应为 0。

## 故障排查

| 现象 | 处理 |
| --- | --- |
| `工作副本有 其他/skills 之外的未提交改动` | 你在 `/wiki-capture` 中途。先 `publish` 掉，或在站点克隆里手工提交/还原，同步会自动恢复 |
| `推送失败，本地提交保留` | 多为 GitHub 连接抖动。下次运行会走「内容无变化，补推 N 个待发布提交」自动带上，不必 amend |
| `疑似密钥，已中止（未落盘）` | 真源 Skill 里写了凭据字面值，删掉再跑；站点是公开仓库，这条闸门不会放行 |
| 站点没更新 | 看 `wiki-sync.log` 是否真的推送了；已推送则等 PowerWiki 的 180 秒 autoSync，再查站点的同步时间 |
