import { View, Text, Button } from '@tarojs/components';
import Taro from '@tarojs/taro';
import './guest-placeholder.scss';

export function GuestPlaceholder({ title, hint }: { title: string; hint: string }) {
  return (
    <View className="guest-placeholder">
      <Text className="guest-icon">{'\u{1F510}'}</Text>
      <Text className="guest-title">{title}</Text>
      <Text className="guest-hint">{hint}</Text>
      <Button
        className="guest-login-btn"
        onClick={() => Taro.navigateTo({ url: '/pages/login/index' })}
      >
        去登录
      </Button>
      <Text className="guest-footnote">登录即表示同意用户协议和隐私政策</Text>
    </View>
  );
}
