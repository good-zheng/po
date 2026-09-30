import { spawnSync } from 'node:child_process';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';

// 知识库站点（goodzheng-dev-wiki）自动化共用的一层：git 调用、待提交清单、
// 推送前的密钥闸门。wiki-capture（人工追加）与 sync-dev-wiki（定时镜像）
// 都必须走这里，避免两处闸门各写一套、其中一处漏判。

export const SECRET_PATTERNS = [
  { name: 'API key', re: /\bsk-[A-Za-z0-9_-]{12,}/ },
  { name: 'GitHub token', re: /\bgh[pouesr]_[A-Za-z0-9]{20,}/ },
  { name: 'private key', re: /-----BEGIN [A-Z ]*PRIVATE KEY-----/ },
  { name: 'appsecret', re: /appsecret\s*[:=]\s*['"]?[A-Za-z0-9]{8,}/i },
  { name: '凭据赋值', re: /(password|secret|token)\s*[:=]\s*['"]?[^\s'"$]{12,}/i },
];

// 镜像时允许的扩展名；其他文件一律跳过并告警，防止 node_modules、.env、二进制混进公开仓
export const EXT_WHITELIST = new Set(['.md', '.txt', '.json', '.yaml', '.yml', '.js', '.cjs', '.mjs', '.py', '.sh']);

export function fail(message) {
  console.error(`✖ ${message}`);
  process.exit(1);
}

export function git(args, cwd, allowFail = false) {
  const result = spawnSync('git', ['-c', 'core.quotepath=off', ...args], {
    cwd,
    encoding: 'utf8',
    windowsHide: true,
  });
  const out = (result.stdout ?? '').trim();
  const err = (result.stderr ?? '').trim();
  if (result.status !== 0) {
    if (allowFail) return { ok: false, out, err };
    fail(`git ${args.join(' ')} 失败\n${err || out || result.error?.message}`);
  }
  return { ok: true, out, err };
}

// -z 取原始 UTF-8 路径：中文目录名不会被八进制转义，也不必猜 porcelain 的状态列宽
export function changedFiles(dir) {
  const sources = [
    ['diff', '--name-only', 'HEAD', '-z'],
    ['diff', '--name-only', '--cached', '-z'],
    ['ls-files', '--others', '--exclude-standard', '-z'],
  ];
  const files = new Set();
  for (const args of sources) {
    for (const path of git(args, dir).out.split('\0')) {
      if (path) files.add(path);
    }
  }
  return [...files].sort();
}

export function findSecrets(text) {
  const hits = [];
  for (const pattern of SECRET_PATTERNS) {
    const match = text.match(pattern.re);
    if (match) hits.push({ name: pattern.name, sample: match[0].slice(0, 40) });
  }
  return hits;
}

export function scanSecrets(dir, files) {
  const hits = [];
  const { out: diff } = git(['diff', '--unified=0', 'HEAD'], dir);
  const added = diff.split('\n').filter((line) => line.startsWith('+') && !line.startsWith('+++'));
  for (const pattern of SECRET_PATTERNS) {
    for (const line of added) {
      if (pattern.re.test(line)) hits.push(`${pattern.name}（改动行）: ${line.slice(0, 120)}`);
    }
  }
  for (const rel of files) {
    let text;
    try {
      text = readFileSync(join(dir, rel), 'utf8');
    } catch {
      continue; // 已删除的文件
    }
    for (const hit of findSecrets(text)) hits.push(`${hit.name} (${rel}): ${hit.sample}`);
  }
  return hits;
}
