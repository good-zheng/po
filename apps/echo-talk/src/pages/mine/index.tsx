import { Image, Text, View } from '@tarojs/components';
import Taro from '@tarojs/taro';
import { useState } from 'react';

import { SCENE_OPTIONS } from '@/config/env';
import { resolveAssetUrl } from '@/lib/api/client';
import { AuthGuard } from '@/lib/auth/auth-guard';
import { useAuth } from '@/lib/auth/auth-context';
import { GuestPlaceholder } from '@/lib/auth/guest-placeholder';
import './index.scss';

const roleLabels: Record<string, string> = {
  admin: '管理员',
  superadmin: '超级管理员',
  user: '普通用户',
};

const SCENE_KEY = 'echo.scene';

type MenuItem = {
  label: string;
  desc: string;
  icon: string;
  action: () => void;
};

/** tab 页不自动跳登录：未登录显示游客占位，点「去登录」才跳转 */
export default function MinePage() {
  const { status } = useAuth();
  if (status === 'unauthenticated') {
    return <GuestPlaceholder title='我的' hint='登录后查看头像与昵称，设置分析场景' />;
  }
  return (
    <AuthGuard>
      <MineView />
    </AuthGuard>
  );
}

function MineView() {
  const { user, signOut } = useAuth();
  const [scene, setScene] = useState<string>(Taro.getStorageSync(SCENE_KEY) || 'general');

  const avatarUrl = resolveAssetUrl(user?.avatar);
  const displayName = user?.nickname?.trim() || user?.username || '未命名';

  const pickScene = (value: string) => {
    setScene(value);
    Taro.setStorageSync(SCENE_KEY, value);
    Taro.showToast({ title: `下次新建会话用「${SCENE_OPTIONS.find((o) => o.value === value)?.label}」`, icon: 'none' });
  };

  const handleSignOut = () => {
    Taro.showModal({
      title: '退出登录',
      content: '本地登录态会被清除，对话记录仍保留在服务端',
      confirmText: '退出',
      confirmColor: '#dc2626',
      success: (res) => {
        if (!res.confirm) return;
        signOut();
        Taro.switchTab({ url: '/pages/session/index' });
      },
    });
  };

  const menuItems: MenuItem[] = [
    {
      icon: '\u2630',
      label: '会话记录',
      desc: '回看已保存的对话、继续未说完的一场',
      action: () => Taro.navigateTo({ url: '/pages/history/index' }),
    },
    {
      icon: '\u270E',
      label: '编辑资料',
      desc: '头像、昵称、手机号、邮箱',
      action: () => Taro.navigateTo({ url: '/pages/profile/edit' }),
    },
  ];

  return (
    <View className='mine'>
      <View className='user-card'>
        {avatarUrl ? (
          <Image className='avatar' src={avatarUrl} mode='aspectFill' />
        ) : (
          <View className='avatar avatar-placeholder'>
            <Text className='avatar-icon'>{'\u{1F464}'}</Text>
          </View>
        )}
        <View className='user-info'>
          <View className='name-row'>
            <Text className='display-name'>{displayName}</Text>
            {user ? <Text className='role-tag'>{roleLabels[user.role] ?? user.role}</Text> : null}
          </View>
          <Text className='username'>@{user?.username}</Text>
          {user?.phoneNumber ? <Text className='meta'>{user.phoneNumber}</Text> : null}
          {user?.email ? <Text className='meta'>{user.email}</Text> : null}
        </View>
      </View>

      <View className='menu-list'>
        {menuItems.map((item, index) => (
          <View
            key={item.label}
            className={`menu-item ${index > 0 ? 'menu-item-border' : ''}`}
            onClick={item.action}
          >
            <Text className='menu-icon'>{item.icon}</Text>
            <View className='menu-text'>
              <View className='menu-label'>{item.label}</View>
              <View className='menu-desc'>{item.desc}</View>
            </View>
            <Text className='menu-arrow'>{'\u203A'}</Text>
          </View>
        ))}
      </View>

      <View className='group'>
        <View className='row row--static'>
          <Text className='row__title'>分析场景</Text>
          <Text className='row__sub'>下一场新会话生效</Text>
        </View>
        <View className='row'>
          <View className='seg'>
            {SCENE_OPTIONS.map((option) => (
              <View
                key={option.value}
                className={`seg__item ${scene === option.value ? 'on' : ''}`}
                onClick={() => pickScene(option.value)}
              >
                {option.label}
              </View>
            ))}
          </View>
        </View>
      </View>

      <View className='signout-btn' onClick={handleSignOut}>
        <Text className='signout-text'>退出登录</Text>
      </View>

      <Text className='footnote'>
        言外 v0.1{'\n'}录音内容仅用于实时转写，不保存原始音频
      </Text>
    </View>
  );
}
