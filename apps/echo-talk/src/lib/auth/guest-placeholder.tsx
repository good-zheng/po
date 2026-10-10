import { Button, Text, View } from '@tarojs/components';
import Taro from '@tarojs/taro';

import { currentPageUrl, saveReturnTo } from '@/lib/auth/return-path';
import './guest-placeholder.scss';

/** tab 页的游客态：占位 + 去登录按钮，跳转只由用户点击触发 */
export function GuestPlaceholder({ title, hint }: { title: string; hint: string }) {
  const goLogin = () => {
    saveReturnTo(currentPageUrl());
    Taro.navigateTo({ url: '/pages/login/index' });
  };

  return (
    <View className='guest-placeholder'>
      <Text className='guest-icon'>{'\u{1F510}'}</Text>
      <Text className='guest-title'>{title}</Text>
      <Text className='guest-hint'>{hint}</Text>
      <Button className='guest-login-btn' onClick={goLogin}>
        去登录
      </Button>
      <Text className='guest-footnote'>登录即表示同意用户协议和隐私政策</Text>
    </View>
  );
}
