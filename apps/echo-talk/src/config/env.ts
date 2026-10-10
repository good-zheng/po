// 后端地址按构建环境区分：
//   dev:weapp（build --watch）→ 载入 .env.development → localhost
//   build:weapp → 载入 .env.production → 线上网关域名
// Taro 只把 TARO_APP_ 前缀变量注入 process.env，缺省时回退本地地址。
export const API_BASE_URL = process.env.TARO_APP_API_BASE_URL ?? 'http://127.0.0.1:8080/api';

// 聊天 WebSocket（FastAPI 服务，独立于 api）：Agent 的洞察与建议从这里流式返回。
// 线上需填 chat 服务的 wss 地址，并把该域名加入小程序「socket 合法域名」。
export const CHAT_WS_URL = process.env.TARO_APP_CHAT_WS_URL ?? 'ws://127.0.0.1:5090/ws/chat';

// ASR WebSocket（Spring Boot 的 /ws/asr 网关）：PCM 帧上行、转写文本下行。
// 注意两点：① 云托管域名只服务 TLS，线上必须用 wss，明文 ws 的握手拿不到 101
// （小程序侧报 "Invalid HTTP status"，首页点「继续」没反应）；
// ② 线上直连 api 实例、不经过 infra/nginx，所以路径要带 context-path：/api/ws/asr。
// 本地同理要带 /api，且不能用 127.0.0.1（真机上它指向手机自己），要填开发机局域网 IP。
export const ASR_WS_URL = process.env.TARO_APP_ASR_WS_URL ?? 'ws://127.0.0.1:8080/api/ws/asr';

// 场景选项：与后端 TalkConstants 的 SCENE_* 一一对应
export const SCENE_OPTIONS = [
  { value: 'general', label: '通用' },
  { value: 'work', label: '职场' },
  { value: 'sales', label: '销售' },
  { value: 'romance', label: '亲密' },
] as const;

export type SceneValue = (typeof SCENE_OPTIONS)[number]['value'];

export function sceneLabel(value?: string): string {
  return SCENE_OPTIONS.find((item) => item.value === value)?.label ?? '通用';
}
