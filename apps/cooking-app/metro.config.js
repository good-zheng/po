const fs = require('node:fs');
const path = require('node:path');
const { getDefaultConfig } = require('expo/metro-config');
const { createProxyMiddleware } = require('http-proxy-middleware');
const { withNativeWind } = require('nativewind/metro');

const projectRoot = __dirname;
const workspaceRoot = path.resolve(projectRoot, '../..');
const config = getDefaultConfig(projectRoot);

config.watchFolders = [workspaceRoot];
config.resolver.nodeModulesPaths = [
  path.resolve(projectRoot, 'node_modules'),
  path.resolve(workspaceRoot, 'node_modules'),
];

// Metro 默认把文件索引缓存放在系统临时目录，且默认每隔几秒整份重写；
// 写入被中断或两个实例并发写时缓存会损坏，下次启动即报反序列化失败并全量重扫。
// 固定到项目目录内，并改回「启动/退出时落盘」，避免反复重写。
const fileMapCacheDir = path.join(projectRoot, '.expo/metro-file-map');
// 缓存管理器不会自建目录，缺目录时写入失败会静默退化成每次全量扫描。
fs.mkdirSync(fileMapCacheDir, { recursive: true });
config.fileMapCacheDirectory = fileMapCacheDir;
config.watcher.unstable_autoSaveCache = { enabled: false };

// 浏览器访问 Web 版时接口必须同源，这里把 /api 代理到后端 origin（由 EXPO_PUBLIC_API_URL
// 推导，如 http://localhost:8080；未设置或非法时用本地 Spring Boot 默认地址）。
// enhanceMiddleware 在 Metro 中已标记 deprecated，但 Expo CLI 仍会调用，是目前给 dev server 加中间件的入口。
function resolveApiProxyTarget() {
  try {
    return new URL(process.env.EXPO_PUBLIC_API_URL).origin;
  } catch {
    return 'http://localhost:8080';
  }
}

config.server.enhanceMiddleware = (metroMiddleware) => {
  const apiProxy = createProxyMiddleware({
    target: resolveApiProxyTarget(),
    changeOrigin: true,
  });

  return (req, res, next) => {
    if (req.url === '/api' || req.url?.startsWith('/api/')) {
      apiProxy(req, res, next);
      return;
    }

    metroMiddleware(req, res, next);
  };
};

module.exports = withNativeWind(config, { input: './src/global.css' });
