import { existsSync, readFileSync, readdirSync } from 'node:fs';
import { dirname, join, resolve, sep } from 'node:path';
import { fileURLToPath } from 'node:url';
import { changedFiles, fail, git, scanSecrets } from '../../../../scripts/wiki-lib.mjs';

// goodzheng-dev-wiki 的人工沉淀入口：准备工作副本 → 追加经验 → 闸门 → 推送。
// 闸门与 sync-dev-wiki（定时镜像通用 skill）共用 scripts/wiki-lib.mjs。
// 用法：
//   node .qoder/skills/wiki-capture/scripts/wiki-capture.mjs prepare
//   node .qoder/skills/wiki-capture/scripts/wiki-capture.mjs status
//   node .qoder/skills/wiki-capture/scripts/wiki-capture.mjs publish --message "<中文标题>" [--dry-run]

const HERE = dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = resolve(HERE, '../../../..');
const DEFAULT_REPO = 'https://github.com/good-zheng/goodzheng-dev-wiki';
const DEFAULT_BRANCH = 'main';

function resolveDir(preferred) {
  const candidates = [
    preferred,
    process.env.WIKI_DIR,
    join(REPO_ROOT, '..', 'goodzheng-dev-wiki'), // 日常开发用的正经克隆
    join(REPO_ROOT, '.tmp', 'wiki'),              // 兜底：临时克隆
  ].filter(Boolean);
  for (const dir of candidates) {
    if (existsSync(join(dir, '.git'))) return resolve(dir);
  }
  return resolve(candidates[candidates.length - 1]); // 都没有 → clone 到 .tmp/wiki
}

function parseArgs(argv) {
  const [command = 'prepare', ...rest] = argv;
  const opts = { command, dir: '', repo: DEFAULT_REPO, branch: DEFAULT_BRANCH, message: '', dryRun: false };
  for (let i = 0; i < rest.length; i += 1) {
    const flag = rest[i];
    if (flag === '--dir') opts.dir = resolve(rest[++i] ?? '');
    else if (flag === '--repo') opts.repo = rest[++i] ?? opts.repo;
    else if (flag === '--branch') opts.branch = rest[++i] ?? opts.branch;
    else if (flag === '--message' || flag === '-m') opts.message = rest[++i] ?? '';
    else if (flag === '--dry-run') opts.dryRun = true;
    else fail(`未知参数: ${flag}`);
  }
  opts.dir = resolveDir(opts.dir);
  return opts;
}

function walkMd(dir, base = dir) {
  const entries = [];
  for (const item of readdirSync(dir, { withFileTypes: true })) {
    if (item.name === '.git' || item.name.startsWith('.')) continue;
    const abs = join(dir, item.name);
    if (item.isDirectory()) entries.push(...walkMd(abs, base));
    else if (item.name.endsWith('.md')) entries.push(abs.slice(base.length + 1).split(sep).join('/'));
  }
  return entries.sort();
}

function outline(dir) {
  for (const rel of walkMd(dir)) {
    const lines = readFileSync(join(dir, rel), 'utf8').split(/\r?\n/);
    const headings = lines
      .map((line, idx) => [idx + 1, line.match(/^(#{2,3})\s+(.+?)\s*$/)])
      .filter(([, match]) => match)
      .slice(0, 24)
      .map(([idx, match]) => `      ${'  '.repeat(match[1].length - 2)}L${idx} ${match[2]}`);
    console.log(`  ${rel} (${lines.length} 行)`);
    if (headings.length) console.log(headings.join('\n'));
  }
}

const opts = parseArgs(process.argv.slice(2));

if (opts.command === 'prepare') {
  if (!existsSync(join(opts.dir, '.git'))) {
    if (existsSync(opts.dir)) fail(`目录已存在但不是 git 仓库: ${opts.dir}`);
    git(['clone', '--branch', opts.branch, opts.repo, opts.dir]);
    console.log(`✔ 已克隆到 ${opts.dir}`);
  } else {
    const dirty = changedFiles(opts.dir);
    if (dirty.length) {
      console.error('✖ 工作副本有未提交改动，先 publish 或手工处理（不自动 reset，以免丢你在写的内容）:');
      console.error(dirty.map((f) => `  ${f}`).join('\n'));
      process.exit(1);
    }
    git(['checkout', opts.branch], opts.dir, true);
    git(['fetch', 'origin', opts.branch], opts.dir, true);
    const merge = git(['merge', '--ff-only', `origin/${opts.branch}`], opts.dir, true);
    console.log(merge.ok ? `✔ ${opts.dir} 已跟上 origin/${opts.branch}` : `✔ 使用本地副本（${(merge.err || merge.out).split('\n')[0]}）`);
  }
  const log = git(['log', '--oneline', '-3'], opts.dir).out;
  console.log(`最近提交:\n${log.split('\n').map((l) => `  ${l}`).join('\n')}`);
  console.log('文档结构（行号可直接 Edit）:');
  outline(opts.dir);
} else if (opts.command === 'status') {
  const dirty = changedFiles(opts.dir);
  console.log(dirty.length ? dirty.map((f) => `  ${f}`).join('\n') : '（无改动）');
} else if (opts.command === 'publish') {
  const dirty = changedFiles(opts.dir);
  if (!dirty.length) fail('没有待提交改动');
  const nonMd = dirty.filter((f) => !f.endsWith('.md'));
  if (nonMd.length) fail(`只允许提交 md，发现其他改动:\n${nonMd.map((f) => `  ${f}`).join('\n')}`);
  const secrets = scanSecrets(opts.dir, dirty);
  if (secrets.length) fail(`疑似密钥，已中止:\n${secrets.join('\n')}`);
  if (!opts.message.trim()) fail('缺少 --message');

  console.log(`工作副本: ${opts.dir}`);
  console.log(`待提交:\n${dirty.map((f) => `  ${f}`).join('\n')}`);
  if (opts.dryRun) {
    console.log('✔ dry-run 通过（未提交、未推送）');
    process.exit(0);
  }

  git(['add', '--', ...dirty], opts.dir);
  const before = git(['rev-parse', '--short', 'HEAD'], opts.dir).out;
  git(['commit', '-m', opts.message], opts.dir);
  const after = git(['rev-parse', '--short', 'HEAD'], opts.dir).out;
  const push = git(['push', 'origin', `HEAD:${opts.branch}`], opts.dir, true);
  if (!push.ok) {
    console.error(`✖ 推送失败，本地提交 ${after} 已保留（先 git pull --ff-only，不要 amend）\n${push.err || push.out}`);
    process.exit(1);
  }
  console.log(`✔ 已提交并推送 ${before}..${after} → origin/${opts.branch}：${opts.message}`);
} else {
  fail(`未知命令: ${opts.command}（prepare | status | publish）`);
}
