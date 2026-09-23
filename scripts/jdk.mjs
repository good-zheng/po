import { existsSync, readdirSync } from 'node:fs';
import { homedir } from 'node:os';
import { join } from 'node:path';

const isWindows = process.platform === 'win32';

export function isJdkHome(candidate) {
  return Boolean(candidate) && existsSync(join(candidate, 'bin', isWindows ? 'java.exe' : 'java'));
}

// mvnw 与 gradlew 只认 JAVA_HOME 或 PATH 里的 java，终端没配时按 pom 的 java.version 在 ~/.jdks 里找 JDK 17
export function resolveJdkHome() {
  if (isJdkHome(process.env.JAVA_HOME)) {
    return process.env.JAVA_HOME;
  }

  const jdksRoot = join(homedir(), '.jdks');
  if (existsSync(jdksRoot)) {
    const names = readdirSync(jdksRoot);
    const ordered = [
      ...names.filter((name) => name === 'ms-17.0.20.1'),
      ...names.filter((name) => name.includes('17') && name !== 'ms-17.0.20.1').sort(),
      ...names.filter((name) => !name.includes('17')).sort(),
    ];
    const found = ordered.map((name) => join(jdksRoot, name)).find(isJdkHome);
    if (found) {
      return found;
    }
  }

  throw new Error(
    'JAVA_HOME is not set to a JDK 17 home. Set it first, e.g. JAVA_HOME=%USERPROFILE%\\.jdks\\ms-17.0.20.1, or install a JDK under ~/.jdks.',
  );
}
