---
kind: external_dependency
name: 国际化：i18next（默认中文）
slug: i18next
category: external_dependency
category_hints:
    - framework_behavior
scope:
    - '**'
---

### i18next
- 在 `shadcn-admin` 前端集成 i18next + react-i18next，默认语言为中文（zh），回退语言也是中文
- 翻译文件位于 `src/locales/zh.json` 和 `src/locales/en.json`，通过 Context Provider（`language-provider.tsx`）注入
- 语言偏好持久化存储在 Cookie（`i18n_lang`）
- 切换入口：顶栏地球图标按钮 + 设置页面账户表单中的语言选择器