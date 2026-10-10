#!/usr/bin/env node
/**
 * 小说业务线建表/扩列迁移（NOVEL_AGENT_PRD.md §13-N1）。
 *
 * 为什么需要它：schema.sql 全是 CREATE TABLE IF NOT EXISTS，对**已存在**的表不做任何事。
 * 本地 book 三张表是早先 JPA ddl-auto 建的，列宽比恢复的 DDL 窄，且 book_chapter.content
 * 还是 TEXT（64KB，utf8mb4 下约 2.1 万字就会被静默截断）——光靠重启应用修不好。
 *
 * 用法：node scripts/novel-migrate.mjs [--dry-run]
 *   凭据从 services/api/api-bootstrap/src/main/resources/application-local.yaml 读，不落盘不打印。
 *   全程只做「加列 / 放宽列宽 / 建新表」，绝不 DROP、绝不改数据。
 */
import { execFileSync } from 'node:child_process';
import { readFileSync, existsSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const repoRoot = join(dirname(fileURLToPath(import.meta.url)), '..');
const LOCAL_YAML = join(
  repoRoot,
  'services/api/api-bootstrap/src/main/resources/application-local.yaml',
);
const SCHEMA_SQL = join(
  repoRoot,
  'services/api/api-bootstrap/src/main/resources/schema.sql',
);
const DRY_RUN = process.argv.includes('--dry-run');

const fail = (msg) => {
  console.error(`[novel-migrate] ${msg}`);
  process.exit(1);
};

/** 只取 datasource 那一段里的 url/username/password，避免命中别处的 password */
function readDataSource() {
  if (!existsSync(LOCAL_YAML)) {
    fail(`缺少本地配置 ${LOCAL_YAML}；这份文件是 gitignore 的，需要从 IDE 那份复制过来`);
  }
  const text = readFileSync(LOCAL_YAML, 'utf8');
  const block = text.split(/\r?\n/);
  const start = block.findIndex((l) => /^\s*datasource:\s*$/.test(l));
  if (start < 0) fail('application-local.yaml 里找不到 spring.datasource 段');
  const slice = [];
  for (let i = start + 1; i < block.length; i += 1) {
    const line = block[i];
    if (line.trim() === '' || /^\S/.test(line)) break;
    if (/^\s{2,}\S/.test(line) === false) break;
    slice.push(line);
  }
  const pick = (key) =>
    slice
      .find((l) => new RegExp(`^\\s+${key}:\\s*(.*)$`).test(l))
      ?.replace(/^\s+\S+:\s*/, '')
      .trim()
      .replace(/^["']|["']$/g, '');

  const url = pick('url');
  const username = pick('username');
  const password = pick('password');
  if (!url || !username || !password) fail('spring.datasource 的 url/username/password 没读全');

  const m = /^jdbc:mysql:\/\/([^:/]+):(\d+)\/([^?;]+)/.exec(url);
  if (!m) fail(`无法解析 JDBC URL：${url}`);
  return { host: m[1], port: m[2], database: m[3], username, password };
}

function findMysql() {
  const candidates = [
    'mysql',
    'C:/Program Files/MySQL/MySQL Server 8.4/bin/mysql.exe',
    'C:/Program Files/MySQL/MySQL Server 8.0/bin/mysql.exe',
  ];
  for (const c of candidates) {
    try {
      execFileSync(c, ['--version'], { stdio: 'pipe' });
      return c;
    } catch (_error) {
      /* 换下一个候选 */
    }
  }
  fail('找不到 mysql 客户端，装了 MySQL Server 8 再跑，或把 mysql.exe 加进 PATH');
}

const ds = readDataSource();
const mysqlBin = findMysql();

/** MYSQL_PWD 传口令：命令行里出现密码会被进程列表看见，也会触发 mysql 自己的告警 */
function run(sql) {
  return execFileSync(mysqlBin, ['--batch', '--raw', '-N', '-h', ds.host, '-P', ds.port, '-u', ds.username, ds.database], {
    input: sql,
    env: { ...process.env, MYSQL_PWD: ds.password },
    encoding: 'utf8',
    maxBuffer: 64 * 1024 * 1024,
  });
}

const quote = (v) => `'${String(v).replace(/'/g, "''")}'`;

function columnsOf(table) {
  const out = run(
    `SELECT COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE FROM information_schema.COLUMNS ` +
      `WHERE TABLE_SCHEMA=${quote(ds.database)} AND TABLE_NAME=${quote(table)} ORDER BY ORDINAL_POSITION;`,
  );
  const rows = out.split(/\r?\n/).filter(Boolean);
  // 注意要显式取两列：直接 new Map(三列数组) 会把整行当 key、把 COLUMN_TYPE 当 value，
  // 于是 here[1] 变成类型字符串的第二个字符，宽度比较静默失效
  return new Map(
    rows.map((r) => {
      const [name, type, nullable] = r.split('\t').map((c) => c.trim());
      return [name, { type, nullable }];
    }),
  );
}

function tableExists(table) {
  const out = run(
    `SELECT COUNT(*) FROM information_schema.TABLES WHERE TABLE_SCHEMA=${quote(ds.database)} AND TABLE_NAME=${quote(table)};`,
  );
  return Number(out.trim()) > 0;
}

/**
 * 期望的列：宽度按恢复的 DDL；status/revision/summary 是创作工作台要的新列（§10.5、§6）。
 * 只放宽不收窄——本地库是 datetime(6)、author 是 varchar(100)，比 DDL 宽的保持原样。
 * 第三段是附加子句，没有就留空串（写 NULL 会和可空判定拼成 NULL NULL）。
 */
const EXPECTED = {
  book: {
    title: ['VARCHAR(255)', 'NO', ''],
    genre: ['VARCHAR(64)', 'YES', ''],
    status: ['VARCHAR(32)', 'NO', "DEFAULT 'ongoing'"],
    summary: ['TEXT', 'YES', "COMMENT '世界观摘要 + 主线进度'"],
  },
  book_chapter: {
    title: ['VARCHAR(255)', 'NO', ''],
    // 长篇正文：TEXT 会在约 2.1 万字处截断，必须 LONGTEXT
    content: ['LONGTEXT', 'YES', ''],
    status: ['VARCHAR(16)', 'NO', "DEFAULT 'draft' COMMENT 'draft/pending_review/committed'"],
    revision: ['INT', 'NO', "DEFAULT 1 COMMENT '每次保存加 1'"],
  },
  book_character: {
    name: ['VARCHAR(128)', 'NO', ''],
  },
  chapter_summary: {
    // 层级摘要树的覆盖区间：scene/chapter 级 from=to=该章序号，arc 级是跨章区间。
    // 读侧靠「整段区间 <= as-of」判摘要是否已知，缺列就只能退回相交判定，会剧透后文
    from_chapter: ['INT', 'YES', "COMMENT '覆盖区间起始章'"],
    to_chapter: ['INT', 'YES', "COMMENT '覆盖区间结束章'"],
    // arc 级不对应某一章正文，没有 revision 可记，必须允许 NULL：
    // 留着 NOT NULL DEFAULT 1 时，arc 行会被填成 1，编译器按版本判过期就会误判它永不落后
    source_version: ['INT', 'YES', "DEFAULT NULL COMMENT '来源正文版本，正文改了则过期重算；arc 级为 NULL'"],
  },
  canon_proposal: {
    // 驳回依据：卡片内容已经留在表里了，「为什么不要它」必须一起留，
    // 否则下一轮对话只能重新猜作者为什么不采纳这张卡
    decided_basis: ['VARCHAR(512)', 'YES', "COMMENT '驳回依据：卡片内容留下了，为什么不要它必须也留下'"],
  },
};

const statements = [];
for (const [table, cols] of Object.entries(EXPECTED)) {
  if (!tableExists(table)) {
    console.log(`[novel-migrate] ${table} 不存在，交给 schema.sql 建表`);
    continue;
  }
  const current = columnsOf(table);
  for (const [col, [type, nullable, tail]] of Object.entries(cols)) {
    const here = current.get(col);
    const nullness = nullable === 'NO' ? 'NOT NULL' : 'NULL';
    if (!here) {
      statements.push(
        `ALTER TABLE \`${table}\` ADD COLUMN \`${col}\` ${type} ${nullness} ${tail};`.replace(/ +/g, ' ').replace(' ;', ';'),
      );
      continue;
    }
    const wantWidth = /(\d+)/.exec(type)?.[1];
    const hasWidth = /(\d+)/.exec(here.type)?.[1];
    // 大文本类型升级，或现有宽度不够时才 MODIFY；已够宽就不动，避免无意义重建
    const needsTypeUp = /longtext/i.test(type) && !/longtext/i.test(here.type);
    const needsWiden = wantWidth && hasWidth && Number(hasWidth) < Number(wantWidth);
    // 可空性也只放宽不收窄：反向的 NOT NULL 会让存量 NULL 行 MODIFY 失败或被迫改数据，越界了
    const needsRelaxNull = here.nullable === 'NO' && nullable === 'YES';
    if (needsTypeUp || needsWiden || needsRelaxNull) {
      statements.push(
        `ALTER TABLE \`${table}\` MODIFY COLUMN \`${col}\` ${type} ${nullness} ${tail};`.replace(/ +/g, ' ').replace(' ;', ';'),
      );
    }
  }
}

console.log(`[novel-migrate] 目标 ${ds.host}:${ds.port}/${ds.database}（用户 ${ds.username}）`);
if (statements.length === 0) {
  console.log('[novel-migrate] 待检表列宽与新列均已就绪，无增量');
} else {
  console.log(`[novel-migrate] 需要 ${statements.length} 条增量：`);
  for (const s of statements) console.log(`  ${s}`);
  if (DRY_RUN) {
    console.log('[novel-migrate] --dry-run，未执行');
  } else {
    run(statements.join('\n'));
  }
}

if (!DRY_RUN) {
  run(readFileSync(SCHEMA_SQL, 'utf8'));
}

const canon = [
  'canon_entry', 'character_state', 'foreshadow', 'alias', 'timeline_anchor',
  'style_profile', 'scene_plan', 'review_finding', 'gen_job', 'chapter_summary',
  'canon_proposal', 'chapter_revision',
];
if (!DRY_RUN) {
  const present = canon.filter(tableExists);
  console.log(`[novel-migrate] 正典层已存在 ${present.length}/${canon.length} 张表`);
  if (present.length !== canon.length) {
    console.log(`  缺：${canon.filter((c) => !present.includes(c)).join(', ')}`);
    fail('schema.sql 执行后正典表仍不全，检查上面 MySQL 的报错');
  }
  for (const t of ['book', 'book_chapter', 'book_character', ...canon]) {
    const n = run(`SELECT COUNT(*) FROM \`${t}\`;`).trim();
    console.log(`  ${t.padEnd(18)} ${n} 行`);
  }
  console.log('[novel-migrate] 完成');
}
