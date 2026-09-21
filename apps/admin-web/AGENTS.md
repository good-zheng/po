├── config/                # Umi 配置目录
│   ├── config.ts          # 主配置文件（定义基础配置、主题、代理等）
│   └── routes.ts          # 路由与菜单配置文件
├── mock/                  # 本地模拟数据目录（用于前后端分离开发）
├── public/                # 静态资源目录（无需构建直接复制到产物）
├── src/                   # 核心源码目录
│   ├── assets/            # 本地静态资源（图片、SVG等，会被构建处理）
│   ├── components/        # 全局通用组件（跨页面复用的高阶组件）
│   ├── layouts/           # 全局布局组件（如 BasicLayout, UserLayout）
│   ├── locales/           # 国际化语言包文件
│   ├── models/            # 全局状态管理（基于 Hooks 的数据流）
│   ├── pages/             # 页面组件目录（遵循约定式路由自动生成）
│   ├── services/          # API 接口服务层（统一封装 HTTP 请求）
│   ├── utils/             # 全局工具函数库（如自定义 request 拦截器）
│   ├── access.ts          # 权限控制定义文件
│   ├── app.tsx            # 运行时配置（处理全局初始化逻辑）
│   └── global.less        # 全局样式文件
├── .umirc.ts              # UmiJS 主配置文件（部分项目作为 config 的替代）
├── package.json           # 项目依赖与脚本配置
└── tsconfig.json          # TypeScript 编译配置