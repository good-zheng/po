#!/usr/bin/env node
/**
 * 云托管空闲回收探针：判断「过段时间再访问就重启」是缩容到零的冷启动，还是容器自己在重启。
 *
 * 用法：
 *   node scripts/cloudrun-idle-probe.mjs                              # 默认测言外书斋，静默 900s
 *   IDLE=2700 node scripts/cloudrun-idle-probe.mjs                    # 拉长到 45 分钟
 *   URL=https://admin.dingdingchu.site/healthz IDLE=1800 node scripts/cloudrun-idle-probe.mjs
 *   PATHS=healthz,/ node scripts/cloudrun-idle-probe.mjs              # 顺带测首页（别写 /healthz，Git Bash 会把它改写成 C:/Program Files/Git/healthz）
 *
 * 原理：静默期内这个进程不再发任何请求，只 sleep；到点后打第一枪，把首个请求和紧随其后的
 * 第二次对比。网关回的是 x-cloudbase-upstream-timecost（容器侧耗时，单位 ms）：
 *   首枪就是百 ms 级  → 实例还在，最小副本数已经是 ≥1；
 *   首枪秒级或先 5xx  → 缩容到零了（云托管不显式设这项就是 0，约半小时无请求即回收），去控制台设 ≥1。
 * 探针只读，不构建不推送；期间任何别处的请求都会把实例焐热，这轮数据就作废了。
 */
const url = process.env.URL || 'http://novel.dingdingchu.site/healthz';
const idleMs = Number(process.env.IDLE || 900) * 1000;
const norm = (p) => (p.startsWith('/') ? p : `/${p}`);
const paths = (process.env.PATHS || '').split(',').filter(Boolean).map(norm);

const origin = new URL(url).origin;
const probePaths = paths.length > 0 ? paths : [norm(new URL(url).pathname)];

function fmt(ms) {
  return `${(ms / 1000).toFixed(3)}s`;
}

async function hit(path) {
  const started = Date.now();
  const res = await fetch(origin + path, {
    headers: { 'Cache-Control': 'no-cache' },
    signal: AbortSignal.timeout(120_000),
  });
  const cost = Date.now() - started;
  const upCost = res.headers.get('x-cloudbase-upstream-timecost');
  const upStatus = res.headers.get('x-cloudbase-upstream-status-code');
  const reqId = res.headers.get('x-cloudbase-request-id');
  const body = path.endsWith('healthz') ? (await res.text()).trim() : '';
  return { path, status: res.status, cost, upCost, upStatus, reqId, body };
}

async function round(label) {
  for (const path of probePaths) {
    try {
      const r = await hit(path);
      console.log(
        `  ${label} ${path} code=${r.status} total=${fmt(r.cost)}` +
          ` upstream=${r.upCost ?? '-'}ms upstream_code=${r.upStatus ?? '-'}` +
          `${r.body ? ` body=${r.body}` : ''} req=${r.reqId ?? '-'}`
      );
    } catch (e) {
      console.log(`  ${label} ${path} 请求失败：${e.cause?.code || e.message}`);
    }
  }
}

console.log(`目标 ${origin} 静默 ${Math.round(idleMs / 1000)}s`);
await round('热');
console.log(`  —— 静默中，${new Date(Date.now() + idleMs).toISOString()} 后打第一枪 ——`);
await new Promise((r) => setTimeout(r, idleMs));
await round('冷');
await round('续');
console.log(
  '判读：首枪 total 到秒级或 code 非 2xx → 缩容到零，控制台把最小副本数设成 ≥1；' +
    '与热态同量级 → 实例一直在，最小副本数已经是 ≥1。'
);
