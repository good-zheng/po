import {
  copyFileSync,
  existsSync,
  mkdirSync,
  readFileSync,
  readdirSync,
  rmSync,
  statSync,
  appendFileSync,
} from 'node:fs';
import { homedir } from 'node:os';
import { dirname, extname, join, relative, resolve, sep } from 'node:path';
import { fileURLToPath } from 'node:url';
import { EXT_WHITELIST, changedFiles, fail, findSecrets, git, scanSecrets } from './wiki-lib.mjs';

// 无人值守把「本地通用 skill」发布到 goodzheng-dev-wiki 公开站点仓库。
// 方向只有一个：本机 ~/.qoder-cn/skills 是真源，站点里的 其他/skills 是镜像。
// 用法：
//   node scripts/sync-dev-wiki.mjs                 # 镜像 + 提交 + 推送
//   node scripts/sync-dev-wiki.mjs --dry-run       # 只打印计划
//   node scripts/sync-dev-wiki.mjs --bootstrap     # 首次：把站点现有 skill 落到本地真源
//   node scripts/sync-dev-wiki.mjs --no-push       # 只提交本地，不推
// 所有写操作前后都过 wiki-lib 的闸门（扩展名白名单 + 密钥扫描）。

const HERE = dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = resolve(HERE, '..');
const QODER_HOME = join(homedir(), '.qoder-cn');
const DEFAULT_SOURCE = join(QODER_HOME, 'skills');
const TARGET_REL = '其他/skills';
const LOG_FILE = join(QODER_HOME, 'wiki-sync.log');

function parseArgs(argv) {
  const opts = { source: DEFAULT_SOURCE, wiki: '', dryRun: false, bootstrap: false, noPush: false, force: false };
  for (let i = 0; i < argv.length; i += 1) {
    const flag = argv[i];
    if (flag === '--local') opts.source = resolve(argv[++i] ?? opts.source);
    else if (flag === '--wiki') opts.wiki = resolve(argv[++i] ?? opts.wiki);
    else if (flag === '--dry-run') opts.dryRun = true;
    else if (flag === '--bootstrap') opts.bootstrap = true;
    else if (flag === '--no-push') opts.noPush = true;
    else if (flag === '--force') opts.force = true;
    else fail(`未知参数: ${flag}`);
  }
  return opts;
}

function findWikiDir(preferred) {
  const candidates = [
    preferred,
    process.env.WIKI_DIR,
    join(REPO_ROOT, '..', 'goodzheng-dev-wiki'), // 日常开发用的正经克隆
    join(REPO_ROOT, '.tmp', 'wiki'),              // 兜底：临时克隆
  ].filter(Boolean);
  for (const dir of candidates) {
    if (existsSync(join(dir, '.git'))) return resolve(dir);
  }
  fail(`找不到 goodzheng-dev-wiki 工作副本，试过: ${candidates.join(' | ')}`);
}

function listFiles(root) {
  if (!existsSync(root)) return [];
  const out = [];
  const walk = (dir) => {
    for (const entry of readdirSync(dir, { withFileTypes: true })) {
      if (entry.name.startsWith('.')) continue; // .git、.DS_Store、编辑器临时文件
      const abs = join(dir, entry.name);
      if (entry.isDirectory()) walk(abs);
      else if (entry.isFile()) out.push(relative(root, abs).split(sep).join('/'));
    }
  };
  walk(root);
  return out.sort();
}

function log(summary) {
  const line = `${new Date().toISOString()} ${summary}\n`;
  try {
    appendFileSync(LOG_FILE, line, 'utf8');
  } catch {
    /* 日志写失败不影响发布 */
  }
  process.stdout.write(line);
}

function pushTo(branch, wikiDir, before) {
  const push = git(['push', 'origin', `HEAD:${branch}`], wikiDir, true);
  if (!push.ok) {
    const after = git(['rev-parse', '--short', 'HEAD'], wikiDir).out;
    log(`✖ 推送失败，本地提交 ${after} 保留，下次运行会补推：${(push.err || push.out).split('\n')[0]}`);
    process.exit(1);
  }
  const after = git(['rev-parse', '--short', 'HEAD'], wikiDir).out;
  log(`✔ 已发布 ${before}..${after} → origin/${branch}（站点 autoSync 下一轮生效）`);
}

function aheadCount(branch, wikiDir) {
  const { out } = git(['rev-list', '--count', `origin/${branch}..HEAD`], wikiDir, true);
  return Number(out) || 0;
}

const opts = parseArgs(process.argv.slice(2));
const wikiDir = findWikiDir(opts.wiki);
const targetDir = join(wikiDir, TARGET_REL);
const branch = git(['rev-parse', '--abbrev-ref', 'HEAD'], wikiDir).out || 'main';

// --- 首次落地：站点 → 本地，只在本地真源为空时允许 ---
if (opts.bootstrap) {
  const localFiles = listFiles(opts.source);
  if (localFiles.length) fail(`本地真源已有 ${localFiles.length} 个文件，不覆盖：${opts.source}`);
  const seeded = listFiles(targetDir);
  if (!seeded.length) fail(`站点里没有 ${TARGET_REL}，无需 bootstrap`);
  for (const rel of seeded) {
    if (!EXT_WHITELIST.has(extname(rel))) {
      log(`跳过 ${rel}（扩展名不在白名单）`);
      continue;
    }
    const dest = join(opts.source, rel);
    mkdirSync(dirname(dest), { recursive: true });
    copyFileSync(join(targetDir, rel), dest);
  }
  log(`bootstrap: ${seeded.length} 个文件 ${TARGET_REL} → ${opts.source}`);
  process.exit(0);
}

// --- 前置检查：工作副本必须干净可快进 ---
const dirty = changedFiles(wikiDir);
const outsideMirror = dirty.filter((f) => !f.startsWith(`${TARGET_REL}/`));
if (outsideMirror.length) {
  // 可能是 wiki-capture 正在写人工文档；绝不把别人的在写内容卷进定时发布
  fail(`工作副本有 ${TARGET_REL} 之外的未提交改动，定时同步中止：\n${outsideMirror.map((f) => `  ${f}`).join('\n')}`);
}
git(['fetch', 'origin', branch], wikiDir, true);
const merge = git(['merge', '--ff-only', `origin/${branch}`], wikiDir, true);
if (!merge.ok) log(`警告: 未能快进到 origin/${branch}（${(merge.err || merge.out).split('\n')[0]}），继续用本地副本`);

// --- 计算镜像计划 ---
const sourceFiles = listFiles(opts.source);
if (!sourceFiles.length && listFiles(targetDir).length && !opts.force) {
  fail(`本地真源 ${opts.source} 为空，而站点有内容 —— 这会删光线上 skill。确认无误再加 --force`);
}
const rejected = sourceFiles.filter((rel) => !EXT_WHITELIST.has(extname(rel)));
const allowed = sourceFiles.filter((rel) => EXT_WHITELIST.has(extname(rel)));
const targetFiles = listFiles(targetDir);

const toWrite = [];
for (const rel of allowed) {
  const src = join(opts.source, rel);
  const dest = join(targetDir, rel);
  const same =
    existsSync(dest) &&
    statSync(src).size === statSync(dest).size &&
    readFileSync(src, 'utf8') === readFileSync(dest, 'utf8');
  if (!same) toWrite.push(rel);
}
const toDelete = targetFiles.filter((rel) => !allowed.includes(rel));

for (const rel of rejected) log(`跳过 ${rel}（扩展名不在白名单，不发布）`);
if (!toWrite.length && !toDelete.length) {
  // 内容没变但可能有上次推送失败留下的提交，顺手补推
  if (aheadCount(branch, wikiDir) > 0 && !opts.noPush && !opts.dryRun) {
    log(`内容无变化，补推 ${aheadCount(branch, wikiDir)} 个待发布提交`);
    pushTo(branch, wikiDir, git(['rev-parse', '--short', `origin/${branch}`], wikiDir, true).out || '?');
    process.exit(0);
  }
  log('无变化，不提交');
  process.exit(0);
}
log(`计划: 更新 ${toWrite.length} / 删除 ${toDelete.length} ← ${opts.source}`);

// 预检：密钥扫描在落盘之前做，中止时不会把工作副本留在半镜像状态
for (const rel of toWrite) {
  const text = readFileSync(join(opts.source, rel), 'utf8');
  const hits = findSecrets(text);
  if (hits.length) fail(`本地真源 ${rel} 含疑似密钥，已中止（未落盘）: ${hits.map((h) => `${h.name}: ${h.sample}`).join(' / ')}`);
}
if (opts.dryRun) {
  for (const rel of toWrite) console.log(`  + ${TARGET_REL}/${rel}`);
  for (const rel of toDelete) console.log(`  - ${TARGET_REL}/${rel}`);
  console.log('✔ dry-run（未落盘、未提交）');
  process.exit(0);
}

for (const rel of toDelete) {
  rmSync(join(targetDir, rel), { force: true });
}
for (const rel of toWrite) {
  const dest = join(targetDir, rel);
  mkdirSync(dirname(dest), { recursive: true });
  copyFileSync(join(opts.source, rel), dest);
}
// 清掉删除后遗留的空目录（只向下走，不会碰 targetDir 之外的东西）
const pruneEmpty = (dir) => {
  if (!existsSync(dir)) return;
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    if (entry.isDirectory()) pruneEmpty(join(dir, entry.name));
  }
  if (dir !== targetDir && readdirSync(dir).length === 0) rmSync(dir, { recursive: true, force: true });
};
pruneEmpty(targetDir);

// --- 闸门：只允许白名单扩展名 + 无密钥 ---
const staged = changedFiles(wikiDir);
const offenders = staged.filter((f) => !f.startsWith(`${TARGET_REL}/`) || !EXT_WHITELIST.has(extname(f)));
if (offenders.length) fail(`待提交内容越界（应全部在 ${TARGET_REL}/ 且扩展名合规）:\n${offenders.map((f) => `  ${f}`).join('\n')}`);
const secrets = scanSecrets(wikiDir, staged);
if (secrets.length) fail(`疑似密钥，已中止（未提交）:\n${secrets.join('\n')}\n工作副本已被镜像覆盖，用 git checkout -- ${TARGET_REL} 复原`);

git(['add', '--', ...staged], wikiDir);
const before = git(['rev-parse', '--short', 'HEAD'], wikiDir).out;
git(['commit', '-m', `chore: 同步本地通用 skill（${toWrite.length} 更新 / ${toDelete.length} 删除）`], wikiDir);
const after = git(['rev-parse', '--short', 'HEAD'], wikiDir).out;
if (opts.noPush) {
  log(`已提交 ${after}（--no-push，未推送）`);
  process.exit(0);
}
pushTo(branch, wikiDir, before);
