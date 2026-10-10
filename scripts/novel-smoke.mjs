#!/usr/bin/env node
/**
 * 小说接口冒烟测（NOVEL_AGENT_PRD §13-N1 的退出条件「CRUD 通」）。
 *
 * 用法：
 *   node scripts/novel-smoke.mjs                      # 只跑读接口（/books 的 GET 已 permitAll）
 *   node scripts/novel-smoke.mjs --token=<管理端JWT>   # 再加一轮写：建书→章→角色→改→删
 *   PO_TOKEN=xxx node scripts/novel-smoke.mjs
 *
 * 口令与令牌都不写进仓库：管理端 JWT 从浏览器 devtools 的 Authorization 头里复制，几小时就过期。
 * 写接口要的是「管理端客户端 + admin 角色」两个权限都在的令牌（SecurityConfig 的 ADMIN_CLIENT），
 * 从 App 端登录拿到的令牌会 403，那不是 bug。
 */
const base = process.env.PO_API_BASE || 'http://127.0.0.1:8080/api';
const argv = process.argv.slice(2);
const tokenArg = argv.find((a) => a.startsWith('--token='));
const token = (tokenArg || '').replace(/^--token=/, '') || process.env.PO_TOKEN || '';

let pass = 0;
let fail = 0;

async function call(method, path, { body, auth = false, expect = [200] } = {}) {
  const headers = { Accept: 'application/json' };
  if (body !== undefined) headers['Content-Type'] = 'application/json';
  if (auth) {
    if (!token) return { skipped: true, why: '没有 --token / PO_TOKEN' };
    headers.Authorization = token.startsWith('Bearer ') ? token : `Bearer ${token}`;
  }
  let res;
  try {
    res = await fetch(base + path, {
      method,
      headers,
      body: body === undefined ? undefined : JSON.stringify(body),
    });
  } catch (e) {
    fail += 1;
    console.log(`  ✗ ${method} ${path} —— 连不上 ${base}（${e.cause?.code || e.message}）；api 服务起来了吗？`);
    return { error: true };
  }
  const text = await res.text();
  let json;
  try {
    json = JSON.parse(text);
  } catch (_e) {
    json = undefined;
  }
  // 信封是 Result{code,success,data,message}：成功 code=1；业务失败仍是 HTTP 200 但 success=false
  const bizFail = json !== undefined && json.success === false;
  const ok = expect.includes(res.status) && !bizFail;
  if (ok) {
    pass += 1;
    console.log(`  ✓ ${method} ${path} → ${res.status}${json?.data?.total !== undefined ? ` 共 ${json.data.total} 条` : ''}`);
  } else {
    fail += 1;
    console.log(
      `  ✗ ${method} ${path} → ${res.status}${bizFail ? ` 业务失败 code=${json.code} message=${json.message}` : ` ${text.slice(0, 200)}`}`,
    );
  }
  return { status: res.status, json: json?.data, raw: text };
}

console.log(`[novel-smoke] 目标 ${base}`);

// 对照组：菜谱是已知在跑的公开接口。若它 200 而 /books 404，说明进程里根本没有 novel 模块（旧构建）
const control = await call('GET', '/recipes?page=0&size=1');
const first = await call('GET', '/books?page=0&size=5');
if (control.status === 200 && first.status === 404) {
  console.log('  → /api/recipes 通而 /api/books 404：运行中的 jar 不含 novel 模块，需要从 IDE 重启 api 服务');
}
await call('GET', '/books/genres');

const content = first.json?.content ?? first.json?.records ?? [];
if (content.length === 0) {
  console.log('  ! 书架为空：跳过按书读取，直接看写接口');
} else {
  const bookId = content[0].id;
  console.log(`  · 用《${content[0].title}》(id=${content[0].id}) 验详情与子资源`);
  await call('GET', `/books/${bookId}`);
  await call('GET', `/books/${bookId}/chapters`);
  await call('GET', `/books/${bookId}/characters`);
}

if (!token) {
  console.log('[novel-smoke] 未提供令牌，写接口未覆盖（CRUD 的 CUD 部分）');
} else {
  const created = await call('POST', '/books', {
    auth: true,
    expect: [200, 201],
    body: { title: `冒烟书 ${new Date().toISOString()}`, description: '由 novel-smoke 创建', genre: 'fantasy', status: 'ongoing', author: 'smoke' },
  });
  const bookId = created.json?.id;
  if (!bookId) {
    console.log('  ! 建书失败，后续写步骤跳过');
  } else {
    const ch = await call('POST', `/books/${bookId}/chapters`, {
      auth: true,
      expect: [200, 201],
      body: { title: '第一章', content: '冒烟正文，含换行\n与长文本占位。' },
    });
    const chr = await call('POST', `/books/${bookId}/characters`, {
      auth: true,
      expect: [200, 201],
      body: { name: '冒烟角色', description: '测试用' },
    });
    if (ch.json?.id) {
      await call('PUT', `/books/${bookId}/chapters/${ch.json.id}`, {
        auth: true,
        body: { title: '第一章（改）', content: '改过的正文，字数变了要重算 total。' },
      });
      // revision 由服务端推进；这里只确认改完还能读回来，且没有把没传的字段刷成 NULL
      const back = await call('GET', `/books/${bookId}/chapters/${ch.json.id}`);
      const c = back.json;
      if (c) {
        const bad = ['title', 'content', 'wordCount', 'status', 'revision'].filter((k) => c[k] === null || c[k] === undefined);
        console.log(bad.length ? `  ✗ 改后字段丢失：${bad.join(', ')}` : `  ✓ 改后字段完好 status=${c.status} revision=${c.revision} wordCount=${c.wordCount}`);
        if (bad.length) fail += 1;
        else pass += 1;
      }
      await call('DELETE', `/books/${bookId}/chapters/${ch.json.id}`, { auth: true });
    }
    if (chr.json?.id) {
      await call('DELETE', `/books/${bookId}/characters/${chr.json.id}`, { auth: true });
    }
    await call('DELETE', `/books/${bookId}`, { auth: true });
  }
}

console.log(`[novel-smoke] 通过 ${pass}，失败 ${fail}`);
// 用 exitCode 而不是 process.exit()：后者会在 fetch 的连接还没排空时退出，Windows 上会甩一句 libuv 断言
process.exitCode = fail === 0 ? 0 : 1;
