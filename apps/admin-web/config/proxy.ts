/**
 * @name 代理的配置
 * @see 在生产环境 代理是无法生效的，所以这里没有生产环境的配置
 * -------------------------------
 * The agent cannot take effect in the production environment
 * so there is no configuration of the production environment
 * For details, please see
 * https://pro.ant.design/docs/deploy
 *
 * @doc https://umijs.org/docs/guides/proxy
 */
export default {
  // 本机开发（dev 走同源 /api，由这里分流到 .env.local 里的后端地址）
  dev: {
    '/api/': {
      // 目标取自 UMI_APP_API_BASE_URL。注意 Umi 只有 .env / .env.local 两档且后者覆盖前者，
      // 而 .env 是生产档 —— 没有 .env.local 时这里会代理到线上域名（点「保存」就是往线上写数据）。
      // 新克隆先 `cp .env.example .env.local`。
      target: process.env.UMI_APP_API_BASE_URL,
      // 配置了这个可以从 http 代理到 https
      // 依赖 origin 的功能可能需要这个，比如 cookie
      changeOrigin: true,
    },
    // localhost:8000/ws/** -> py_server WebSocket（同源路径，同样只在这两档里取值）
    '/ws': {
      target: process.env.UMI_APP_WS_BASE_URL,
      changeOrigin: true,
      ws: true,
    },
  },
  /**
   * @name 详细的代理配置
   * @doc https://github.com/chimurai/http-proxy-middleware
   */
  test: {
    // localhost:8000/api/** -> https://pro-api.ant-design-demo.workers.dev/api/**
    '/api/': {
      target: 'https://pro-api.ant-design-demo.workers.dev',
      changeOrigin: true,
    },
  },
  pre: {
    '/api/': {
      target: 'your pre url',
      changeOrigin: true,
    },
  },
};
