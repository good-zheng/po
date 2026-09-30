import Taro from '@tarojs/taro';

const RETURN_TO_KEY = 'po.auth.returnTo';

const TAB_PATHS = [
  '/pages/index/index',
  '/pages/categories/index',
  '/pages/ai/chat',
  '/pages/profile/index',
];

export function isTabPath(path: string): boolean {
  return TAB_PATHS.includes(path);
}

export function saveReturnTo(url: string) {
  Taro.setStorageSync(RETURN_TO_KEY, url);
}

export function consumeReturnTo(): string | null {
  const url = Taro.getStorageSync(RETURN_TO_KEY);
  Taro.removeStorageSync(RETURN_TO_KEY);
  return url || null;
}

/** 当前页面完整路径（含查询参数），如 /pages/cook/index?id=1 */
export function currentPageUrl(): string {
  const pages = Taro.getCurrentPages();
  const page = pages[pages.length - 1];
  if (!page) return '';
  const path = '/' + page.route;
  const params = Object.entries(page.options || {})
    .map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(String(v))}`)
    .join('&');
  return params ? `${path}?${params}` : path;
}
