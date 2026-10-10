// https://umijs.org/config/

import { defineConfig } from '@umijs/max';
import proxy from './proxy';
import routes from './routes';

const { UMI_ENV = 'dev' } = process.env;

/**
 * 部署形态已定（PRD §13-Q2，2026-10-10）：独立容器 + 根路径，见 apps/novel-web/DEPLOY_CLOUDRUN.md。
 * 若改成 nginx 的 /novel/ 子路径，publicPath 与 base 两个值要一起换，
 * 且所有分享链接会带前缀——所以这一处必须显式改，不要散落在页面里。
 */
const PUBLIC_PATH: string = '/';

export default defineConfig({
  hash: true,
  publicPath: PUBLIC_PATH,
  routes,
  ignoreMomentLocale: true,
  proxy: proxy[UMI_ENV as keyof typeof proxy],
  fastRefresh: true,

  /**
   * 显式 define：Umi 只在 webpack 链路里自动注入 UMI_APP_*，打包器换掉就静默变空串，
   * 管理端 `apps/admin-web/config/config.ts` 已经踩过（那边注释写明了）。
   * 值来自本目录 `.env`（dev）/ `.env.production`（build），见 src/app.tsx 的 baseURL 用法。
   */
  define: {
    'process.env.UMI_APP_API_BASE_URL': process.env.UMI_APP_API_BASE_URL ?? '',
  },

  model: {},
  initialState: {},
  request: {
    dataField: 'data',
  },

  title: '言外书斋',

  /**
   * Umi 默认注入的 viewport 带 user-scalable=no / maximum-scale=1，会禁掉系统级双指缩放，
   * 阅读站不能接受（字号调节只是补充手段）；同时缺少 viewport-fit=cover，
   * global.less 里的 env(safe-area-inset-*) 需要它才生效。
   */
  metas: [
    {
      name: 'viewport',
      content: 'width=device-width, initial-scale=1, viewport-fit=cover',
    },
    // 手机浏览器的状态栏/地址栏配色跟纸墨色板对齐，否则顶部会露出一条系统蓝/白
    {
      name: 'theme-color',
      media: '(prefers-color-scheme: light)',
      content: '#f6f2ea',
    },
    {
      name: 'theme-color',
      media: '(prefers-color-scheme: dark)',
      content: '#131418',
    },
  ],

  /**
   * 不启用 layout 插件：ProLayout 自带「未登录即跳登录页」的 onPageChange，
   * 与本站「书架/详情/阅读三页游客可看」的约定冲突（见 NOVEL_WEB_PRD.md §5）。
   * 页面自行渲染极简页头页脚（src/components/Chrome.tsx）。
   */
  antd: {
    appConfig: {},
    configProvider: {
      theme: {
        token: {
          // 与 global.less 的 --accent 同值：朱砂。antd 组件（若有）跟着走，
          // 不要留默认的 antd 蓝——两套主色并排就是没做完的设计。
          colorPrimary: '#a83e2b',
          colorLink: '#a83e2b',
          borderRadius: 10,
          fontFamily:
            "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif",
        },
      },
    },
  },

  favicons: [`${PUBLIC_PATH}favicon.svg`],

  theme: {
    'nav-bg': '#f6f2ea',
  },
});
