// 后端地址按构建环境区分：
//   dev:weapp（build --watch）→ 载入 .env.development → localhost
//   build:weapp → 载入 .env.production → 微信云托管域名
// Taro 只把 TARO_APP_ 前缀变量注入 process.env，缺省时回退本地地址。
export const API_BASE_URL =
  process.env.TARO_APP_API_BASE_URL ?? 'http://localhost:8080/api';

// 聊天 WebSocket（FastAPI 服务，独立于 api）。线上需填 chat 服务的云托管 wss 地址，
// 并把该域名加入小程序「socket 合法域名」。
export const CHAT_WS_URL =
  process.env.TARO_APP_CHAT_WS_URL ?? 'ws://localhost:5090/ws/chat';
