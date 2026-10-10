// 已上线项目的真实地址。域名一律从云托管控制台抄，别按规律推（同一条教训见
// apps/novel-web/DEPLOY_CLOUDRUN.md 第 7 节）。换证书或换默认域名时只改这里，
// 首页卡片、项目页与页脚都引这张表。
export const LIVE = {
  // 言外书斋阅读端。TLS 还没配好：`curl https://novel.dingdingchu.site/` 现在拿不到响应，
  // 所以先挂 http；证书生效后把 scheme 改成 https 即可。
  novel: 'http://novel.dingdingchu.site/',

  // 管理后台（菜谱维护、注册审批，以及小说创作工作台）。http 会被平台 308 回 https，
  // 证书是好的，所以直接写 https 少一次跳转。需要管理员账号才能进。
  admin: 'https://admin.dingdingchu.site/',
} as const;
