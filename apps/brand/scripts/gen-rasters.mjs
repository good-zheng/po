import { mkdir, readdir, readFile, stat } from 'node:fs/promises';
import path from 'node:path';
import sharp from 'sharp';

// 插画一律以 SVG 为准；但两类产物必须是位图：OG 分享图（爬虫不读 SVG）和博客封面
// （模板的 blog 组件写死 format="webp"，Astro 默认拒绝栅格化 SVG 源）。
// 改完 src/assets/illustrations 下的 SVG 后跑 `pnpm brand:assets` 重新生成。

const appRoot = path.resolve(import.meta.dirname, '..');
const srcDir = path.join(appRoot, 'src', 'assets', 'illustrations');
const outDir = path.join(appRoot, 'src', 'assets', 'images');

const jobs = [{ in: 'og.svg', out: 'og.png', width: 1200, height: 628, format: 'png' }];

const coverDir = path.join(srcDir, 'covers');
for (const entry of await readdir(coverDir)) {
  if (!entry.endsWith('.svg')) continue;
  jobs.push({
    in: path.join('covers', entry),
    out: path.join('covers', entry.replace(/\.svg$/, '.webp')),
    width: 900,
    height: 506,
    format: 'webp',
    quality: 82,
  });
}

const flatten = '#0B1220';

for (const job of jobs) {
  const from = path.join(srcDir, job.in);
  const to = path.join(outDir, job.out);
  const svg = await readFile(from);
  let image = sharp(svg, { density: 288 })
    .resize(job.width, job.height, { fit: 'inside' })
    .flatten({ background: flatten });
  image = job.format === 'webp' ? image.webp({ quality: job.quality }) : image.png({ quality: 92 });
  await mkdir(path.dirname(to), { recursive: true });
  const info = await image.toFile(to);
  const { size } = await stat(to);
  console.log(`${job.in} -> ${job.out}  ${info.width}x${info.height}  ${(size / 1024).toFixed(1)} KB`);
}

// 录屏的 poster。竖屏录屏不走 Video 组件（它写死 aspect-video，会把 9:19 的手机屏压扁），
// 首页那一屏改用页面里的原生 <video>，poster 烘进 public/demo/，与 mp4 同目录。
const poster = {
  from: path.join(appRoot, 'src', 'assets', 'images', 'screenshots', 'dingdingchu-home.png'),
  to: path.join(appRoot, 'public', 'demo', 'dingdingchu-home-poster.webp'),
  width: 560,
};
await mkdir(path.dirname(poster.to), { recursive: true });
const posterInfo = await sharp(poster.from).resize({ width: poster.width }).webp({ quality: 78 }).toFile(poster.to);
console.log(
  `screenshots/dingdingchu-home.png -> public/demo/${path.basename(poster.to)}  ${posterInfo.width}x${posterInfo.height}  ${((await stat(poster.to)).size / 1024).toFixed(1)} KB`
);
