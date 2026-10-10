/**
 * 代理只在 dev 生效；生产由 nginx/云托管同源转发，故不配 test/pre。
 * @doc https://umijs.org/docs/guides/proxy
 */
export default {
  dev: {
    '/api/': {
      target: process.env.UMI_APP_API_BASE_URL ?? 'http://127.0.0.1:8080',
      changeOrigin: true,
    },
  },
};
