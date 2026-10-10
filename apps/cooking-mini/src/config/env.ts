// 后端地址按构建环境区分：
//   dev:weapp（build --watch）→ 载入 .env.development → localhost
//   build:weapp → 载入 .env.production → 微信云托管域名
// Taro 只把 TARO_APP_ 前缀变量注入 process.env，缺省时回退本地地址。
export const API_BASE_URL =
  process.env.TARO_APP_API_BASE_URL ?? 'http://localhost:8080/api';
