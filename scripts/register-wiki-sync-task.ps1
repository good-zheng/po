param(
    [switch]$Unregister,
    [int]$EveryMinutes = 30
)

# 注册/卸载「本地通用 Skill 每 N 分钟镜像到 goodzheng-dev-wiki」的计划任务。
# 用法（PowerShell）：
#   .\scripts\register-wiki-sync-task.ps1            # 注册，默认 30 分钟
#   .\scripts\register-wiki-sync-task.ps1 -EveryMinutes 15
#   .\scripts\register-wiki-sync-task.ps1 -Unregister
# 任务描述与日志保持 ASCII，避免 PowerShell 5.1 读无 BOM 文件时中文乱码。

$ErrorActionPreference = 'Stop'
$taskName = 'goodzheng-wiki-sync'

if ($Unregister) {
    if (Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue) {
        Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
        Write-Output "removed task $taskName"
    } else {
        Write-Output "task $taskName not registered"
    }
    exit 0
}

$repoRoot = Split-Path -Parent $PSScriptRoot
$script = Join-Path $repoRoot 'scripts\sync-dev-wiki.mjs'
$node = (Get-Command node.exe -ErrorAction Stop).Source

$action = New-ScheduledTaskAction -Execute $node -Argument "`"$script`"" -WorkingDirectory $repoRoot
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) `
    -RepetitionInterval (New-TimeSpan -Minutes $EveryMinutes)
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -MultipleInstances IgnoreNew

Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings `
    -Description "Mirror local generic skills into goodzheng-dev-wiki every $EveryMinutes minutes" | Out-Null

$info = Get-ScheduledTaskInfo -TaskName $taskName
Write-Output "registered $taskName (every $EveryMinutes min, next run $($info.NextRunTime))"
Write-Output "  node:   $node"
Write-Output "  script: $script"
Write-Output "  log:    $env:USERPROFILE\.qoder-cn\wiki-sync.log"
