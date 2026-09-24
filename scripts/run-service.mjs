import { spawnSync } from 'node:child_process';
import { existsSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

import { resolveJdkHome } from './jdk.mjs';

const repositoryRoot = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const [service, action] = process.argv.slice(2);
const isWindows = process.platform === 'win32';

// 每个服务产出一组待执行命令（chat:install 需要按序执行多条）
let commandList = [];

if (service === 'api') {
  const goals = {
    install: ['-pl', 'api-bootstrap', '-am', 'install', '-DskipTests'],
    start: ['-pl', 'api-bootstrap', '-am', 'spring-boot:run'],
    verify: ['verify'],
  };

  if (!(action in goals)) {
    throw new Error(`Unsupported API command: ${action}`);
  }

  commandList = [
    {
      // Windows 上 mvnw.cmd 必须经 shell 执行，见下方 spawnCommand
      command: isWindows ? '.\\mvnw.cmd' : './mvnw',
      args: goals[action],
      cwd: resolve(repositoryRoot, 'services', 'api'),
      shell: isWindows,
      env: { ...process.env, JAVA_HOME: resolveJdkHome() },
    },
  ];
} else if (service === 'chat' || service === 'agentcore' || service === 'agentcooking') {
  // agent-core / agent-cooking 都是库包，无独立 venv，复用 chat 的 .venv 跑测试
  const chatDir = resolve(repositoryRoot, 'services', 'chat');
  const serviceLayout = {
    chat: {
      cwd: chatDir,
      goals: {
        // chat 依赖本地库包，须先装库再装宿主；顺序即依赖链
        install: [
          ['-m', 'pip', 'install', '-e', '../agent-core[dev]'],
          ['-m', 'pip', 'install', '-e', '../agent-cooking[dev]'],
          ['-m', 'pip', 'install', '-e', '.[dev]'],
        ],
        start: [
          [
            '-m',
            'uvicorn',
            'app.main:app',
            '--port',
            '5090',
            '--reload',
            // --reload 默认只盯 CWD（services/chat），而 agent-core / agent-cooking
            // 是 editable 安装的本地库包，改它们的 src 不重启就一直跑旧代码；
            // 指定 --reload-dir 后 CWD 不再自动纳入，所以三个目录都要列全
            '--reload-dir',
            '.',
            '--reload-dir',
            '../agent-core/src',
            '--reload-dir',
            '../agent-cooking/src',
          ],
        ],
        test: [['-m', 'pytest', 'tests']],
      },
    },
    agentcore: {
      cwd: resolve(repositoryRoot, 'services', 'agent-core'),
      goals: { test: [['-m', 'pytest', 'tests']] },
    },
    agentcooking: {
      cwd: resolve(repositoryRoot, 'services', 'agent-cooking'),
      goals: { test: [['-m', 'pytest', 'tests']] },
    },
  };
  const { cwd, goals } = serviceLayout[service];

  if (!(action in goals)) {
    throw new Error(`Unsupported ${service} command: ${action}`);
  }

  const command = isWindows
    ? resolve(chatDir, '.venv', 'Scripts', 'python.exe')
    : resolve(chatDir, '.venv', 'bin', 'python');
  if (!existsSync(command)) {
    throw new Error(
      `Python venv not found: ${command}. Create it first: cd services/chat && python -m venv .venv`,
    );
  }
  commandList = goals[action].map((args) => ({
    command,
    args,
    cwd,
  }));
} else {
  throw new Error(`Unsupported service: ${service}`);
}

function quoteShellArgument(value) {
  return /[\s"&|<>^]/.test(value) ? `"${value.replaceAll('"', '\\"')}"` : value;
}

for (const { command, args, cwd, shell, env } of commandList) {
  // shell 与 args 数组同时使用会触发 Node DEP0190（参数不转义），故 shell 场景下先自行拼接并转义
  const [spawnCommand, spawnArgs] = shell
    ? [[command, ...args].map(quoteShellArgument).join(' '), undefined]
    : [command, args];
  const result = spawnSync(spawnCommand, spawnArgs, {
    cwd,
    shell,
    stdio: 'inherit',
    env,
  });
  if (result.error) {
    throw result.error;
  }
  if (result.status !== 0) {
    process.exitCode = result.status ?? 1;
    break;
  }
}
