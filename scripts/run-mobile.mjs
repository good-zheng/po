import { spawnSync } from 'node:child_process';
import { copyFileSync, existsSync, readdirSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

import { resolveJdkHome } from './jdk.mjs';

const repositoryRoot = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const [action] = process.argv.slice(2);
const isWindows = process.platform === 'win32';
const minimumNinjaVersion = [1, 11];

function isSdkRoot(candidate) {
  return Boolean(candidate) && existsSync(join(candidate, 'platform-tools'));
}

function ninjaExecutableName() {
  return isWindows ? 'ninja.exe' : 'ninja';
}

function readNinjaVersion(executable) {
  const result = spawnSync(executable, ['--version'], { encoding: 'utf8' });
  const match = result.status === 0 ? /(\d+)\.(\d+)/.exec(result.stdout ?? '') : null;
  return match ? [Number(match[1]), Number(match[2])] : undefined;
}

function supportsLongPaths(version) {
  if (!version) {
    return false;
  }

  const [major, minor] = version;
  return major > minimumNinjaVersion[0] || (major === minimumNinjaVersion[0] && minor >= minimumNinjaVersion[1]);
}

function findNinjaOnPath(pathKey) {
  return (process.env[pathKey] ?? '')
    .split(isWindows ? ';' : ':')
    .filter(Boolean)
    .map((entry) => join(entry, ninjaExecutableName()))
    .find(existsSync);
}

// pnpm 的 .pnpm 目录名很长，react-native-* 原生模块的 CMake 对象路径会超过 Windows 的 260 字符上限。
// AGP 固定使用 Android SDK 自带的 ninja（不受 PATH 影响），而 SDK 捆绑的 1.10.x 读写不了这类路径，
// 表现为 `manifest 'build.ninja' still dirty after 100 tries` 或 mkdir No such file or directory。
function ensureSdkNinjaSupportsLongPaths(sdkRoot, pathKey) {
  const cmakeRoot = join(sdkRoot, 'cmake');
  if (!existsSync(cmakeRoot)) {
    return;
  }

  const outdated = readdirSync(cmakeRoot)
    .map((version) => join(cmakeRoot, version, 'bin', ninjaExecutableName()))
    .filter((executable) => existsSync(executable) && !supportsLongPaths(readNinjaVersion(executable)));
  if (outdated.length === 0) {
    return;
  }

  const replacement = [process.env.NINJA, findNinjaOnPath(pathKey)]
    .filter(Boolean)
    .find((candidate) => supportsLongPaths(readNinjaVersion(candidate)));
  if (!replacement) {
    throw new Error(
      'Android SDK 自带的 ninja 版本过低，无法处理 pnpm 深层 node_modules 的超长路径。请先安装支持长路径的 ninja（例如 pip install ninja）后重试。',
    );
  }

  for (const executable of outdated) {
    const backup = `${executable}.orig`;
    if (!existsSync(backup)) {
      copyFileSync(executable, backup);
    }
    copyFileSync(replacement, executable);
  }
  console.log(`已用 ${replacement} 覆盖 Android SDK 自带的旧版 ninja（原文件备份为 *.orig）`);
}

// Expo CLI 只在 ANDROID_HOME 存在时才把它拼成 emulator 可执行文件路径，否则退化成裸命令名
function resolveAndroidSdkRoot() {
  const candidates = [
    process.env.ANDROID_HOME,
    process.env.ANDROID_SDK_ROOT,
    isWindows && process.env.LOCALAPPDATA ? join(process.env.LOCALAPPDATA, 'Android', 'Sdk') : undefined,
    !isWindows ? join(process.env.HOME ?? '', 'Android', 'Sdk') : undefined,
  ];
  const found = candidates.find(isSdkRoot);
  if (found) {
    return found;
  }

  throw new Error(
    'Android SDK not found. Set ANDROID_HOME, or install it to the default location (%LOCALAPPDATA%\\Android\\Sdk on Windows).',
  );
}

const sdkRoot = resolveAndroidSdkRoot();
const pathKey = Object.keys(process.env).find((key) => key.toUpperCase() === 'PATH') ?? 'PATH';

const mobileAppDir = resolve(repositoryRoot, 'apps', 'cooking-app');
const androidDir = join(mobileAppDir, 'android');
const gradleExecutable = isWindows ? 'gradlew.bat' : './gradlew';

const commands = {
  android: ['run', 'android'],
  apk: ['apk'],
};

if (!(action in commands)) {
  throw new Error(`Unsupported mobile command: ${action}`);
}

ensureSdkNinjaSupportsLongPaths(sdkRoot, pathKey);

function quoteShellArgument(value) {
  return /[\s"&|<>^]/.test(value) ? `"${value.replaceAll('"', '\\"')}"` : value;
}

function runShellCommand(command, args, options) {
  // shell 与 args 数组同时使用会触发 Node DEP0190（参数不转义），故 shell 场景下先自行拼接并转义
  const [spawnCommand, spawnArgs] = isWindows
    ? [[command, ...args].map(quoteShellArgument).join(' '), undefined]
    : [command, args];

  const result = spawnSync(spawnCommand, spawnArgs, { shell: isWindows, stdio: 'inherit', ...options });
  if (result.error) {
    throw result.error;
  }
  if ((result.status ?? 1) !== 0) {
    process.exit(result.status ?? 1);
  }
}

const buildEnvironment = {
  ...process.env,
  JAVA_HOME: resolveJdkHome(),
  ANDROID_HOME: sdkRoot,
  ANDROID_SDK_ROOT: sdkRoot,
  [pathKey]: [join(sdkRoot, 'platform-tools'), join(sdkRoot, 'emulator'), process.env[pathKey]]
    .filter(Boolean)
    .join(isWindows ? ';' : ':'),
};

// 与 expo run:android 一致：原生目录缺失时才生成，避免覆盖已有 android/ 下的手改内容
if (action === 'apk') {
  if (!existsSync(androidDir)) {
    runShellCommand('pnpm', ['run', 'prebuild:android'], { cwd: mobileAppDir, env: buildEnvironment });
  }

  // 只编 x86_64 时体积小、速度快，适合模拟器与本地冒烟；不传架构参数则产出四种 ABI 的真机包
  const architectures = process.argv[3];
  const gradleArgs = ['assembleDebug', ...(architectures ? [`-PreactNativeArchitectures=${architectures}`] : [])];
  runShellCommand(gradleExecutable, gradleArgs, { cwd: androidDir, env: buildEnvironment });
  console.log(`APK: ${join(androidDir, 'app', 'build', 'outputs', 'apk', 'debug', 'app-debug.apk')}`);
  process.exit(0);
}

const args = commands[action];
runShellCommand('pnpm', args, { cwd: mobileAppDir, env: buildEnvironment });
process.exit(0);
