#!/usr/bin/env node
/**
 * 把 book.genre 里写成了 label（玄幻）的行改成 value（fantasy）。
 *
 * 为什么需要它：genre 的契约是存 value，但服务端从前只校验 status，写 label 照样入库。
 * 列表页拿 label 只做展示映射（`genreLabelMap[record.genre] ?? record.genre`），所以脏行**看起来完全正常**，
 * 只有在书架按类型筛选（发的是 value）时才会凭空少掉一本——scripts/novel-internal-smoke.mjs
 * 早期就是这么写脏了 3 行。服务端现在已挡住新脏值（BookServiceImpl.requireKnownGenre），
 * 存量还得靠这条脚本刷；别的环境（比如云上库）如果也脏过，同一份脚本直接复用。
 *
 * 用法：node scripts/novel-genre-fix.mjs [--dry-run | --apply]
 *   不带参数只打印计划，不落写入——这是改数据，不是改结构，宁可让人先看一眼 SQL。
 *   label→value 的映射从 NovelGenres.java 现读，绝不在这里抄一份字典（抄了就会漂）。
 *   凭据沿用 novel-migrate.mjs：从 gitignore 的 application-local.yaml 解析，经 MYSQL_PWD 传入，不打印。
 */
import { execFileSync } from 'node:child_process';
import { existsSync, readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const repoRoot = join(dirname(fileURLToPath(import.meta.url)), '..');
const LOCAL_YAML = join(repoRoot, 'services/api/api-bootstrap/src/main/resources/application-local.yaml');
const GENRES_JAVA = join(
  repoRoot,
  'services/api/novel/src/main/java/com/goodzheng/po/novel/constant/NovelGenres.java',
);
const DRY_RUN = process.argv.includes('--dry-run');
const APPLY = process.argv.includes('--apply');

const fail = (msg) => {
  console.error(`[novel-genre-fix] ${msg}`);
  process.exit(1);
};

if (DRY_RUN && APPLY) fail('--dry-run 与 --apply 不能同时给');

function readDataSource() {
  if (!existsSync(LOCAL_YAML)) {
    fail(`缺少本地配置 ${LOCAL_YAML}；这份文件是 gitignore 的，需要从 IDE 那份复制过来`);
  }
  const block = readFileSync(LOCAL_YAML, 'utf8').split(/\r?\n/);
  const start = block.findIndex((l) => /^\s*datasource:\s*$/.test(l));
  if (start < 0) fail('application-local.yaml 里找不到 spring.datasource 段');
  const slice = [];
  for (let i = start + 1; i < block.length; i += 1) {
    const line = block[i];
    if (line.trim() === '' || /^\S/.test(line)) break;
    slice.push(line);
  }
  const pick = (key) =>
    slice
      .find((l) => new RegExp(`^\\s+${key}:\\s*(.*)$`).test(l))
      ?.replace(/^\s+\S+:\s*/, '')
      .trim()
      .replace(/^["']|["']$/g, '');
  const url = pick('url'), username = pick('username'), password = pick('password');
  if (!url || !username || !password) fail('spring.datasource 的 url/username/password 没读全');
  const m = /^jdbc:mysql:\/\/([^:/]+):(\d+)\/([^?;]+)/.exec(url);
  if (!m) fail(`无法解析 JDBC URL：${url}`);
  return { host: m[1], port: m[2], database: m[3], username, password };
}

/** 客户端候选路径与 novel-migrate.mjs 保持一致 */
function findMysql() {
  for (const c of ['mysql', 'C:/Program Files/MySQL/MySQL Server 8.4/bin/mysql.exe', 'C:/Program Files/MySQL/MySQL Server 8.0/bin/mysql.exe']) {
    try {
      execFileSync(c, ['--version'], { stdio: 'pipe' });
      return c;
    } catch {
      /* 换下一个候选 */
    }
  }
  fail('找不到 mysql 客户端');
}

/** 从 Java 字典现读 label→value，避免脚本里抄一份会漂的表 */
function readGenreMap() {
  if (!existsSync(GENRES_JAVA)) fail(`缺少 ${GENRES_JAVA}`);
  const src = readFileSync(GENRES_JAVA, 'utf8');
  const pairs = [...src.matchAll(/new GenreOption\("([^"]+)",\s*"([^"]+)"\)/g)];
  if (pairs.length === 0) fail('NovelGenres.java 里一个 GenreOption 都没解析到，格式改了？');
  return new Map(pairs.map(([, value, label]) => [label, value]));
}

const ds = readDataSource();
const mysqlBin = findMysql();
const labelToValue = readGenreMap();

/**
 * 显式 utf8mb4：客户端默认字符集若是 gbk/latin1，中文 label 会在传输层就变形成另一个串，
 * WHERE 匹配不上还看不出原因。
 */
function run(sql) {
  return execFileSync(
    mysqlBin,
    ['--batch', '--raw', '-N', '--default-character-set=utf8mb4', '-h', ds.host, '-P', ds.port, '-u', ds.username, ds.database],
    {
      input: sql,
      env: { ...process.env, MYSQL_PWD: ds.password },
      encoding: 'utf8',
      maxBuffer: 64 * 1024 * 1024,
    },
  );
}

const quote = (v) => `'${String(v).replace(/'/g, "''")}'`;

const rows = run(
  `SELECT id, title, genre FROM book WHERE genre IS NOT NULL AND genre <> '' ORDER BY id;`,
)
  .split(/\r?\n/)
  .filter(Boolean)
  .map((line) => {
    const [id, title, genre] = line.split('\t');
    return { id, title, genre };
  });

const values = new Set(labelToValue.values());
const dirty = rows.filter((r) => !values.has(r.genre));
const fixable = dirty.filter((r) => labelToValue.has(r.genre));
const unknown = dirty.filter((r) => !labelToValue.has(r.genre));

console.log(`[novel-genre-fix] 目标 ${ds.host}:${ds.port}/${ds.database}（用户 ${ds.username}）`);
console.log(`[novel-genre-fix] genre 非空 ${rows.length} 行，其中码值 ${rows.length - dirty.length} 行`);

if (fixable.length > 0) {
  console.log('[novel-genre-fix] 需要改写的行：');
  for (const r of fixable) console.log(`  id=${r.id} 《${r.title}》 ${r.genre} → ${labelToValue.get(r.genre)}`);
}
if (unknown.length > 0) {
  console.log('[novel-genre-fix] 既不是码值也不是 label，跳过（不猜）：');
  for (const r of unknown) console.log(`  id=${r.id} 《${r.title}》 genre=${JSON.stringify(r.genre)}`);
}

const statements = [
  ...new Map(
    fixable.map((r) => [r.genre, `UPDATE book SET genre=${quote(labelToValue.get(r.genre))} WHERE genre=${quote(r.genre)};`]),
  ).values(),
];

if (statements.length === 0) {
  console.log('[novel-genre-fix] 没有 label 写法的行，无需改写');
  process.exit(0);
}

console.log(`[novel-genre-fix] 计划执行 ${statements.length} 条：`);
for (const s of statements) console.log(`  ${s}`);

if (!APPLY) {
  console.log(DRY_RUN ? '[novel-genre-fix] --dry-run，未执行' : '[novel-genre-fix] 未执行；确认无误后加 --apply');
  process.exit(0);
}

run(statements.join('\n'));

const after = run(
  `SELECT genre, COUNT(*) FROM book WHERE genre IS NOT NULL AND genre <> '' GROUP BY genre ORDER BY genre;`,
).trim();
console.log('[novel-genre-fix] 改写后 genre 分布：');
console.log(after);
