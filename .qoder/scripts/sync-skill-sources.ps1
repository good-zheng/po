[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$qoderRoot = Split-Path -Parent $PSScriptRoot
$sourceRoot = Join-Path $qoderRoot 'skill-sources'
$manifestPath = Join-Path $sourceRoot 'manifest.json'

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    throw 'Git was not found. Install Git before syncing skill sources.'
}

if (-not (Test-Path $manifestPath)) {
    throw "Source manifest was not found: $manifestPath"
}

$manifest = Get-Content -Path $manifestPath -Raw | ConvertFrom-Json

foreach ($source in $manifest.sources) {
    $target = Join-Path $sourceRoot $source.target

    if (-not (Test-Path $target)) {
        Write-Host "[clone] $($source.id)"
        & git clone --filter=blob:none --no-checkout $source.repository $target
        if ($LASTEXITCODE -ne 0) {
            throw "Unable to clone source: $($source.id)"
        }
    }
    elseif (-not (Test-Path (Join-Path $target '.git'))) {
        throw "Target is not a Git worktree: $target"
    }
    
    Write-Host "[sparse-checkout] $($source.id) @ $($source.commit.Substring(0, 12))"
    & git -C $target fetch --depth 1 origin $source.commit
    if ($LASTEXITCODE -ne 0) {
        throw "Unable to fetch pinned commit for $($source.id)"
    }

    & git -C $target sparse-checkout init --no-cone
    if ($LASTEXITCODE -ne 0) {
        throw "Unable to initialize sparse checkout for $($source.id)"
    }

    $sparseArguments = @('-C', $target, 'sparse-checkout', 'set', '--no-cone', '--') + @($source.sparsePaths)
    & git @sparseArguments
    if ($LASTEXITCODE -ne 0) {
        throw "Unable to set sparse paths for $($source.id)"
    }

    & git -C $target checkout --detach $source.commit
    if ($LASTEXITCODE -ne 0) {
        throw "Unable to checkout pinned commit for $($source.id)"
    }
}

Write-Host 'Open-source skills synchronized with sparse checkout at pinned commits.'
