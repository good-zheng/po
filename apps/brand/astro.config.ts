import path from 'path';
import { fileURLToPath } from 'url';

import { defineConfig, fontProviders } from 'astro/config';

import { unified } from '@astrojs/markdown-remark';

import sitemap from '@astrojs/sitemap';
import tailwindcss from '@tailwindcss/vite';
import mdx from '@astrojs/mdx';
import partytown from '@astrojs/partytown';
import icon from 'astro-icon';
import compress from 'astro-compress';
import type { AstroIntegration } from 'astro';
import type { Plugin as VitePlugin } from 'vite';

import astrowind from './vendor/integration';

import { readingTimeRemarkPlugin, responsiveTablesRehypePlugin } from './src/utils/frontmatter';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const hasExternalScripts = false;
const whenExternalScripts = (items: (() => AstroIntegration) | (() => AstroIntegration)[] = []) =>
  hasExternalScripts ? (Array.isArray(items) ? items.map((item) => item()) : [items()]) : [];

// Windows 下 dev server 会被 astro-icon 的监视路径 bug 拖崩，这里做两件事：
//
// 1. 修路径。astro-icon 1.2.0 用 `resolve(root.pathname, iconDir)` 算本地图标目录，
//    而 file URL 的 pathname 带前导斜杠（`/D:/dev/po/apps/brand/`），Windows 的
//    path.resolve 把前导 `/` 当成「当前盘根目录」，于是拼出
//    `D:\D:\dev\po\apps\brand\src\assets\icons` 这种双盘符路径。该路径不存在，
//    chokidar 会逐级向上找存在的最近父目录，最终退回盘根 `D:\`，然后把整个 D 盘
//    当监视目录递归扫描。
// 2. 兜底。扫描过程中一旦有文件 stat 失败（例如 D:\DumpStack.log.tmp 恒返回
//    EINVAL），chokidar 会抛 'error' 事件；Vite 没有监听它，Node 直接以未处理的
//    error 事件退出进程。这里接住，只警告不退出。
const DUPLICATED_DRIVE = /^[\\/]?([A-Za-z]:)[\\/]+([A-Za-z]:)[\\/]/;

function sanitizeWatchPath(p: string): string {
  const m = DUPLICATED_DRIVE.exec(p);
  return m ? m[2] + '\\' + p.slice(m[0].length) : p;
}

function windowsWatchSafety(): VitePlugin {
  return {
    name: 'po:windows-watch-safety',
    enforce: 'pre',
    configureServer(server) {
      const watcher = server.watcher;
      const originalAdd = watcher.add.bind(watcher);

      watcher.add = ((paths: string | readonly string[], ...rest: unknown[]) => {
        const fixed = Array.isArray(paths) ? paths.map(sanitizeWatchPath) : sanitizeWatchPath(paths as string);
        return (originalAdd as (...args: unknown[]) => unknown)(fixed, ...rest);
      }) as typeof watcher.add;

      watcher.on('error', (error: Error) => {
        server.config.logger.warn(`[watch] 忽略文件监视错误：${error?.message ?? error}`);
      });
    },
  };
}

export default defineConfig({
  output: 'static',

  // Prefetch links as they enter the viewport for snappier navigations
  // (works together with <ClientRouter />, which enables prefetch by default).
  prefetch: {
    prefetchAll: true,
    defaultStrategy: 'viewport',
  },

  // Native Fonts API: self-hosts + subsets + preloads Inter and generates
  // metric-adjusted fallbacks. Injected via <Font /> in Layout.astro and
  // consumed through the `--font-inter` CSS variable in CustomStyles.astro.
  fonts: [
    {
      provider: fontProviders.fontsource(),
      name: 'Inter',
      cssVariable: '--font-inter',
      weights: ['100 900'],
      styles: ['normal'],
      subsets: ['latin'],
      fallbacks: ['sans-serif'],
    },
  ],

  integrations: [
    sitemap(),
    mdx(),
    icon({
      // Local SVG icons (used as <Icon name="file-name" />) live next to the other assets.
      iconDir: 'src/assets/icons',
      include: {
        tabler: ['*'],
        'flat-color-icons': [
          'template',
          'gallery',
          'approval',
          'document',
          'advertising',
          'currency-exchange',
          'voice-presentation',
          'business-contact',
          'database',
        ],
      },
    }),

    ...whenExternalScripts(() =>
      partytown({
        config: { forward: ['dataLayer.push'] },
      })
    ),

    compress({
      // csso off on purpose: its parser doesn't understand the media range
      // syntax Tailwind v4 emits for breakpoints (`@media (width>=48rem)`) and
      // silently drops every one of those blocks — the site then renders as if
      // all `md:`/`lg:` classes were missing. lightningcss parses it correctly.
      CSS: { csso: false, lightningcss: { minify: true } },
      HTML: {
        'html-minifier-terser': {
          removeAttributeQuotes: false,
        },
      },
      Image: false,
      JavaScript: true,
      SVG: false,
      Logger: 1,
    }),

    astrowind({
      config: './src/config.yaml',
    }),
  ],

  image: {
    // Astro's default Sharp service handles local images.
    //
    // Most remote CDN images (Unsplash, Cloudinary, Imgix…) are routed by
    // src/components/common/Image.astro through `unpic`, which rewrites the
    // URL with CDN-side query parameters and serves it straight from the
    // provider — Astro never downloads it, so they don't need to be listed.
    //
    // `domains` only matters for remote URLs that fall through to Astro's
    // native <Image /> (i.e. providers Unpic can't detect, like Pixabay).
    // Listed entries are authorized to be processed by Sharp.
    // Unsplash is listed so post covers can be rendered as real 1200×626 Open Graph images.
    domains: ['cdn.pixabay.com', 'images.unsplash.com'],

    // Emit responsive styles for the native <Image layout=…> used by
    // src/components/common/Image.astro (local images). Utility classes on
    // each usage still win, since these styles use low-specificity selectors.
    responsiveStyles: true,
  },

  markdown: {
    processor: unified({
      remarkPlugins: [readingTimeRemarkPlugin],
      rehypePlugins: [responsiveTablesRehypePlugin],
    }),
    shikiConfig: {
      // Code blocks follow the site theme; see the `.astro-code` rules in tailwind.css.
      themes: { light: 'github-light', dark: 'github-dark' },
    },
  },

  vite: {
    plugins: [windowsWatchSafety(), tailwindcss()],
    resolve: {
      alias: {
        '~': path.resolve(__dirname, './src'),
      },
    },
  },
});
