import { spawnSync } from 'node:child_process';
import { existsSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

// pnpm 在 Windows 上通过 shell 执行 `bash foo.sh` 时，PATH 里的 bash.exe 常常
// 解析成 WSL 的 stub（`C:\Windows\System32\bash.exe`），进入 WSL 后发现发行版
// 里没有 /bin/bash 直接失败。这里显式定位 Git Bash，绕开 PATH 抢跑。
//
// 用法:
//   node scripts/run-sh.mjs <script.sh> [args...]
//   node scripts/run-sh.mjs --env KEY=VAL [--env K2=V2] <script.sh> [args...]
const argv = process.argv.slice(2);
const env = { ...process.env };
while (argv[0] === '--env') {
  const pair = argv[1];
  if (!pair || !pair.includes('=')) {
    console.error('--env 需要 KEY=VALUE 形式');
    process.exit(2);
  }
  const idx = pair.indexOf('=');
  env[pair.slice(0, idx)] = pair.slice(idx + 1);
  argv.splice(0, 2);
}

const [scriptPath, ...restArgs] = argv;
if (!scriptPath) {
  console.error('用法: node scripts/run-sh.mjs [--env KEY=VAL] <script.sh> [args...]');
  process.exit(2);
}

const repositoryRoot = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const absScript = resolve(repositoryRoot, scriptPath);
if (!existsSync(absScript)) {
  console.error(`找不到脚本: ${absScript}`);
  process.exit(2);
}

function findBash() {
  const candidates = [
    process.env.BASH_BIN,
    'C:\\Program Files\\Git\\bin\\bash.exe',
    'C:\\Program Files (x86)\\Git\\bin\\bash.exe',
    process.env.LOCALAPPDATA &&
      `${process.env.LOCALAPPDATA}\\Programs\\Git\\bin\\bash.exe`,
  ].filter(Boolean);
  for (const c of candidates) {
    if (existsSync(c)) return c;
  }
  // deploy-*.sh 依赖 bash 特性（[[ ]]、BASH_SOURCE），/bin/sh(dash) 会直接报错
  return process.platform === 'win32' ? 'bash' : '/bin/bash';
}

const bash = findBash();
const result = spawnSync(bash, [absScript, ...restArgs], {
  cwd: repositoryRoot,
  stdio: 'inherit',
  env,
});
if (result.error) throw result.error;
process.exit(result.status ?? 1);
