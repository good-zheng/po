#!/usr/bin/env node
/**
 * 小说内部通道冒烟测（NOVEL_AGENT_PRD §13-N2 的退出条件）。
 *
 * 验的是 agent-novel 落库时真正打的那条链路 `/novel/internal/**`：
 * 令牌闸门 → 建书（summary 与 description 分栏）→ 建章 → 建角色 → 抽断言入正典 →
 * 重放不重复 → as-of 快照读回 → 层级摘要三级写入与「整段已知」过滤。
 * 全部读写都走 X-Internal-Token，与管理端 JWT 无关（那是另一套权限）。
 *
 * 用法：
 *   node scripts/novel-internal-smoke.mjs
 *   node scripts/novel-internal-smoke.mjs --token=<内网令牌>
 *   PO_API_BASE=http://127.0.0.1:8080/api node scripts/novel-internal-smoke.mjs
 *
 * 令牌来源优先级：--token > 环境变量 PO_INTERNAL_TOKEN >
 *   services/api/api-bootstrap/src/main/resources/application-local.yaml 的 app.internal-token。
 *   那份 yaml 已被 gitignore；脚本只读取、绝不打印令牌内容。
 *
 * 会写库：每轮新建一本「冒烟正典 <时间戳>」（内部通道没有删除端点，正典只追加）。
 * 结尾打印 bookId，清理用管理端令牌走 DELETE /books/{id}（见 novel-smoke.mjs）。
 */
import { readFileSync, existsSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const repoRoot = join(dirname(fileURLToPath(import.meta.url)), '..');
const LOCAL_YAML = join(
  repoRoot,
  'services/api/api-bootstrap/src/main/resources/application-local.yaml',
);
const base = process.env.PO_API_BASE || 'http://127.0.0.1:8080/api';
const tokenArg = (process.argv.slice(2).find((a) => a.startsWith('--token=')) || '').replace(
  /^--token=/,
  '',
);

let pass = 0;
let fail = 0;

function ok(label, detail = '') {
  pass += 1;
  console.log(`  ✓ ${label}${detail ? ` —— ${detail}` : ''}`);
}
function bad(label, detail = '') {
  fail += 1;
  console.log(`  ✗ ${label}${detail ? ` —— ${detail}` : ''}`);
}

/** 只取 app 段里的 internal-token，避免命中 jwt / wechat 等其它密钥 */
function readInternalTokenFromYaml() {
  if (!existsSync(LOCAL_YAML)) return '';
  const lines = readFileSync(LOCAL_YAML, 'utf8').split(/\r?\n/);
  const start = lines.findIndex((l) => /^app:\s*$/.test(l));
  if (start < 0) return '';
  for (let i = start + 1; i < lines.length; i += 1) {
    const line = lines[i];
    if (line.trim() !== '' && /^\S/.test(line)) break; // app 段结束
    const hit = line.match(/^\s+internal-token:\s*(.*)$/);
    if (hit) return hit[1].trim().replace(/^["']|["']$/g, '');
  }
  return '';
}

const token = tokenArg || process.env.PO_INTERNAL_TOKEN || readInternalTokenFromYaml();

async function call(method, path, { body, useToken = true } = {}) {
  const headers = { Accept: 'application/json' };
  if (body !== undefined) headers['Content-Type'] = 'application/json';
  if (useToken && token) headers['X-Internal-Token'] = token;
  let res;
  try {
    res = await fetch(base + path, {
      method,
      headers,
      body: body === undefined ? undefined : JSON.stringify(body),
    });
  } catch (e) {
    bad(`${method} ${path}`, `连不上 ${base}（${e.cause?.code || e.message}）；api 服务起来了吗？`);
    return { error: true };
  }
  const text = await res.text();
  let json;
  try {
    json = JSON.parse(text);
  } catch (_e) {
    json = undefined;
  }
  if (res.status !== 200) {
    bad(`${method} ${path}`, `HTTP ${res.status} ${text.slice(0, 160)}`);
    return { status: res.status, json: undefined };
  }
  if (json?.success === false) {
    // Result 信封：业务失败也是 HTTP 200，判定必须看 success
    return { status: 200, rejected: true, code: json.code, message: json.message, json: undefined };
  }
  ok(`${method} ${path}`);
  return { status: 200, json: json?.data };
}

console.log(`[novel-internal-smoke] 目标 ${base}`);

// 对照组：菜谱是已知在跑的公开接口。它通而内部端点 404，说明运行中的构建不含 novel 模块
const control = await call('GET', '/recipes?page=0&size=1', { useToken: false });
if (control.error) {
  console.log('[novel-internal-smoke] api 服务不可达，后续步骤全部跳过');
  process.exitCode = 1;
  process.exit(1);
}

if (!token) {
  bad(
    '拿不到内网令牌',
    '--token= / PO_INTERNAL_TOKEN / application-local.yaml 的 app.internal-token 三者都为空；' +
      'Java 侧未配置时内部端点一律拒绝，这不是 bug。配置方法见 scripts/NOVEL_INTERNAL_SMOKE.md',
  );
} else {
  // 闸门：缺令牌必须被拒（且拒的是 403 而不是放行）
  const gate = await call('GET', `/novel/internal/canon/aliases?bookId=1`, { useToken: false });
  if (gate.rejected && gate.code === 403) ok('缺令牌的内部调用被拒（code=403）');
  else if (gate.rejected) bad('缺令牌被拒但错误码不是 403', `code=${gate.code} message=${gate.message}`);
  else bad('缺令牌的内部调用竟然通过', '闸门失效');

  const stamp = new Date().toISOString();
  // authorId 要落在 sys_user 里真实存在的 id：book.author_id 无外键也无校验，
  // 写了不存在的 id 建库能成功，但书架按作者筛选/展示时这本书是孤儿
  const tier0Summary = `冒烟 Tier-0 摘要 ${stamp}：世界观与主线进度。`;
  const book = await call('POST', `/novel/internal/books?authorId=${Number(process.env.PO_AUTHOR_ID ?? 3)}`, {
    body: {
      title: `冒烟正典 ${stamp}`,
      description: '由 novel-internal-smoke 创建',
      summary: tier0Summary,
      // genre 要写 NovelGenres 的 value（fantasy），不是 label（玄幻）：
      // 写 label 不报错，但管理端按类型筛选时这本书会凭空消失
      genre: 'fantasy',
    },
  });
  const bookId = book.json?.id;
  if (!bookId) {
    bad('内部通道建书未返回 id', JSON.stringify(book).slice(0, 160));
  } else {
    console.log(`  · bookId=${bookId}`);
    // summary 与 description 各归各位：前者是注入用的世界观/进度线，后者是对外简介。
    // 建书响应直接回显实体，两者写串了在这里就能看见，不必等到 L1 注入了错文本再查
    if (book.json?.summary !== tier0Summary)
      bad('book.summary 未落库', `回显 ${JSON.stringify(book.json?.summary)}`);
    else if (book.json?.description === tier0Summary)
      bad('book.summary 覆盖掉了对外简介', '两个字段必须分开持久');
    else ok('book.summary 与 description 分别落库');
    const chapters = [];
    for (const index of [1, 2, 3, 4, 5]) {
      const created = await call('POST', `/novel/internal/books/${bookId}/chapters`, {
        body: {
          title: `第${index}章`,
          content: `冒烟正文第 ${index} 章：她抬眼，墨绿色的瞳仁映着灯。`,
          chapterIndex: index,
        },
      });
      if (created.json?.id) chapters.push(created.json.id);
    }
    await call('POST', `/novel/internal/books/${bookId}/characters`, {
      body: { name: '林晚', description: '主角｜剑修' },
    });

    // 幂等键的四维：chapterId + contentHash + promptVersion + model
    const idem = `smoke:${chapters[0] ?? 0}:${stamp}:v1:smoke-model`;
    const payload = {
      bookId,
      asOfChapter: 1,
      idempotencyKey: idem,
      chapterId: chapters[0],
      assertions: [
        {
          kind: 'character',
          subjectKey: 'char:linwan',
          predicate: 'eye_color',
          objectText: '墨绿',
          restatement: '林晚的眼睛是墨绿色。',
          confidence: 1.0,
          establishedChapter: 1,
          validFromChapter: 1,
          sourceChapterId: chapters[0],
          evidenceQuote: '她抬眼，墨绿色的瞳仁映着灯。',
          promptVersion: 'v1',
          model: 'smoke-model',
          status: 'confirmed',
        },
      ],
      foreshadows: [{ op: 'open', plantedChapter: 1, content: '残卷缺的一页去了哪', dueByArc: 2 }],
      aliases: [{ entityKey: 'char:linwan', aliasText: '沈师兄', firstSeenChapter: 1, isPrimary: true }],
      stateChanges: [{ charKey: 'char:linwan', asOfChapter: 1, isAlive: true, lastSeenChapter: 1 }],
    };
    await call('POST', '/novel/internal/assertions:append', { body: payload });
    const replay = await call('POST', '/novel/internal/assertions:append', { body: payload });
    if (replay.json?.applied === false) ok('重放命中幂等键', 'applied=false，未重复入库');
    else bad('重放未命中幂等键', `applied=${replay.json?.applied}（应为 false）`);

    const snapshot = await call(
      'GET',
      `/novel/internal/canon/snapshot?bookId=${bookId}&asOf=1&entities=char:linwan`,
    );
    const rows = Array.isArray(snapshot.json) ? snapshot.json : [];
    if (!Array.isArray(snapshot.json)) bad('快照返回结构不是数组', JSON.stringify(snapshot).slice(0, 160));
    else if (rows.length === 0) bad('as-of=1 快照为空', '断言没进库，或读侧按 status 过滤掉了');
    else if (rows.some((r) => r.authority !== 'model'))
      bad('快照里出现非 model 权限的断言', `authority=${rows.map((r) => r.authority).join(',')}`);
    else ok(`as-of=1 快照 ${rows.length} 条`, 'authority 全为 model');

    // 换章号 + 换幂等键逐章再抽一次：证明「新事实写进去了」而不是永远 REPLAY。
    // 基线取不带 entities 的同一条查询，与下面各章快照同口径
    const base1 = await call('GET', `/novel/internal/canon/snapshot?bookId=${bookId}&asOf=1`);
    const baseline = (base1.json || []).length;
    const perChapter = [{ index: 1, n: baseline }];
    let wroteAll = true;
    for (const index of [2, 3, 4, 5]) {
      const chapterId = chapters[index - 1] ?? chapters[0];
      const written = await call('POST', '/novel/internal/assertions:append', {
        body: {
          ...payload,
          asOfChapter: index,
          chapterId,
          idempotencyKey: `${idem}:ch${index}`,
          assertions: [
            {
              ...payload.assertions[0],
              establishedChapter: index,
              validFromChapter: index,
              objectText: `第 ${index} 章的瞳色`,
              restatement: `第 ${index} 章起林晚的瞳色记为「第 ${index} 章的瞳色」。`,
              sourceChapterId: chapterId,
            },
          ],
          foreshadows: [],
          aliases: [],
          stateChanges: [],
        },
      });
      if (written.json?.applied !== true) {
        bad(`第 ${index} 章新幂等键未生效写入`, `applied=${written.json?.applied}`);
        wroteAll = false;
        break;
      }
      const snap = await call('GET', `/novel/internal/canon/snapshot?bookId=${bookId}&asOf=${index}`);
      perChapter.push({ index, n: (snap.json || []).length });
    }
    if (wroteAll) {
      const counts = perChapter.map((c) => c.n);
      const monotonic = counts.every((v, i) => i === 0 || v >= counts[i - 1]);
      const grew = counts.at(-1) > baseline;
      if (monotonic && grew)
        ok('as-of 过滤生效', `第1章可见 ${baseline} 条 → 第5章可见 ${counts.at(-1)} 条`);
      else bad('as-of 过滤异常', `${perChapter.map((c) => `ch${c.index}=${c.n}`).join(' / ')}`);
    }
    await call('GET', `/novel/internal/canon/foreshadows/open?bookId=${bookId}&asOf=5`);
    await call('GET', `/novel/internal/canon/aliases?bookId=${bookId}`);

    // ---------- 层级摘要树（scene / chapter / arc） ----------
    // 载荷形状与 HttpCanonStore 逐字对齐：scene 级带 sceneNo、chapter 级 sceneNo 恒 0、
    // arc 级不带 chapterId 而带区间。冒烟要验的就是这三条形状后端认不认。
    const readSummaries = async (upto, levels) => {
      const res = await call(
        'GET',
        `/novel/internal/canon/summaries?bookId=${bookId}&upto=${upto}&levels=${levels}&limit=50`,
      );
      return Array.isArray(res.json) ? res.json : null;
    };
    for (const index of [1, 2]) {
      await call('POST', '/novel/internal/summaries', {
        body: {
          chapterId: chapters[index - 1],
          level: 'scene',
          scenes: [
            { sceneNo: 1, content: `第${index}章场景1：她踏入当铺。`, tokens: 12 },
            { sceneNo: 2, content: `第${index}章场景2：掌柜认出那半枚玉。`, tokens: 14 },
          ],
        },
      });
      await call('POST', '/novel/internal/summaries', {
        body: {
          chapterId: chapters[index - 1],
          level: 'chapter',
          scenes: [{ sceneNo: 0, content: `第${index}章章级摘要`, tokens: 8 }],
        },
      });
    }
    await call('POST', '/novel/internal/summaries', {
      body: {
        bookId,
        level: 'arc',
        arcNo: 1,
        fromChapter: 1,
        toChapter: 2,
        scenes: [{ sceneNo: 1, content: '第一弧：当铺与半枚玉。', tokens: null }],
      },
    });

    const at1 = await readSummaries(1, 'scene,chapter');
    const at1Rows = at1 === null ? [] : at1.filter((r) => r.chapterNo === 1);
    if (at1 === null) bad('摘要读取返回结构不是数组');
    else if (at1Rows.length !== 3)
      bad('第 1 章摘要不齐（应为 2 场景 + 1 章级）', `实得 ${at1Rows.length} 行`);
    else if (!at1Rows.some((r) => r.level === 'chapter' && r.sceneNo === 0))
      bad('章级摘要的 sceneNo 不是 0', at1Rows.map((r) => `${r.level}#${r.sceneNo}`).join(' / '));
    else ok('upto=1 读到本章 scene+chapter 摘要', at1Rows.map((r) => `${r.level}#${r.sceneNo}`).join(' / '));

    // 相交即剧透：覆盖 1~2 章的弧摘要在 upto=1 时不能出现
    const arcAt1 = await readSummaries(1, 'arc');
    if (arcAt1 === null) bad('arc 摘要读取失败');
    else if (arcAt1.length > 0)
      bad('upto=1 就读到了覆盖到第 2 章的弧摘要', '区间终点未知等于把后文带进注入');
    else ok('弧摘要按「整段已知」过滤', 'upto=1 时不可见');

    const arcAt2 = await readSummaries(2, 'arc');
    if (arcAt2 === null || arcAt2.length !== 1)
      bad('upto=2 应读到 1 段弧摘要', `实得 ${arcAt2 === null ? '读取失败' : arcAt2.length}`);
    else if (arcAt2[0].chapterNo !== 1 || arcAt2[0].sceneNo !== 1)
      bad('弧摘要的区间起点或弧号不对', `chapterNo=${arcAt2[0].chapterNo} sceneNo=${arcAt2[0].sceneNo}`);
    else ok('upto=2 读到弧摘要', 'chapterNo=区间起点 / sceneNo=弧号');

    // 同弧号重写覆盖而不双写：resume 重放与「重算摘要」都会走这条路
    const arcRewrite = await call('POST', '/novel/internal/summaries', {
      body: {
        bookId,
        level: 'arc',
        arcNo: 1,
        fromChapter: 1,
        toChapter: 2,
        scenes: [{ sceneNo: 1, content: '第一弧（重算）：当铺掌柜是旧识。', tokens: null }],
      },
    });
    const arcAfter = await readSummaries(2, 'arc');
    if (arcAfter === null || arcAfter.length !== 1)
      bad('弧摘要重写后行数不为 1', `实得 ${arcAfter === null ? '读取失败' : arcAfter.length}`);
    else if (!arcAfter[0].content.includes('重算'))
      bad('弧摘要未按覆盖语义更新', arcAfter[0].content);
    else if (arcRewrite.json?.summariesWritten !== 1)
      bad('弧摘要写入计数异常', `summariesWritten=${arcRewrite.json?.summariesWritten}`);
    else ok('同弧号重写按覆盖处理', '仍只有 1 行，summariesWritten=1');

    // 层级过滤：只点名 chapter 时不该混进 scene 行
    const onlyChapter = await readSummaries(2, 'chapter');
    if (onlyChapter === null || onlyChapter.length === 0) bad('levels=chapter 过滤后为空');
    else if (onlyChapter.some((r) => r.level !== 'chapter'))
      bad('levels=chapter 里混进了其他层级', onlyChapter.map((r) => r.level).join(','));
    else ok('levels 过滤生效', `chapter 级 ${onlyChapter.length} 行`);

    const badLevel = await call('GET', `/novel/internal/canon/summaries?bookId=${bookId}&upto=2&levels=bogus`);
    if (badLevel.rejected) ok('未知层级被拒', `code=${badLevel.code}`);
    else bad('未知层级竟然通过', 'levels 白名单失效');
    console.log(`  · 清理：node scripts/novel-smoke.mjs --token=<管理端JWT> 后 DELETE ${base}/books/${bookId}`);
  }
}

console.log(`[novel-internal-smoke] 通过 ${pass}，失败 ${fail}`);
// 用 exitCode 而不是 process.exit()：后者会在 fetch 连接未排空时退出，Windows 上会甩一句 libuv 断言
process.exitCode = fail === 0 ? 0 : 1;
