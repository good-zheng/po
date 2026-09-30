import { View, Text, Image } from '@tarojs/components';
import Taro from '@tarojs/taro';
import { useAuth } from '@/lib/auth/auth-context';
import { resolveAssetUrl } from '@/lib/api/client';
import { AuthGuard } from '@/lib/auth/auth-guard';
import { GuestPlaceholder } from '@/lib/auth/guest-placeholder';
import './index.scss';

const roleLabels: Record<string, string> = {
  admin: '管理员',
  superadmin: '超级管理员',
  user: '普通用户',
};

type MenuItem = {
  label: string;
  desc: string;
  icon: string;
  action: () => void;
};

export default function ProfilePage() {
  const { status } = useAuth();
  if (status === 'unauthenticated') {
    return (
      <GuestPlaceholder
        title="我的"
        hint="登录后查看收藏、浏览历史和我的菜谱"
      />
    );
  }
  return (
    <AuthGuard>
      <ProfileView />
    </AuthGuard>
  );
}

function ProfileView() {
  const { user, signOut } = useAuth();
  const avatarUrl = resolveAssetUrl(user?.avatar);
  const displayName = user?.nickname?.trim() || user?.username || '未登录';

  const handleSignOut = () => {
    Taro.showModal({
      title: '退出登录',
      content: '确定要退出当前账号吗？',
      confirmText: '退出',
      confirmColor: '#dc2626',
      success: (res) => {
        if (res.confirm) {
          signOut();
          Taro.reLaunch({ url: '/pages/login/index' });
        }
      },
    });
  };

  const menuItems: MenuItem[] = [
    {
      icon: '\u270E',
      label: '编辑资料',
      desc: '头像、昵称、手机号、邮箱',
      action: () => Taro.navigateTo({ url: '/pages/profile/edit' }),
    },
    {
      icon: '\u{1F4D6}',
      label: '我的菜谱',
      desc: '创建菜谱，查看审核进度',
      action: () => Taro.navigateTo({ url: '/pages/profile/recipes' }),
    },
    {
      icon: '\u2665',
      label: '我的收藏',
      desc: '收藏过的菜谱',
      action: () => Taro.navigateTo({ url: '/pages/profile/favorites' }),
    },
    {
      icon: '\u{1F551}',
      label: '浏览历史',
      desc: '最近看过的菜谱',
      action: () => Taro.navigateTo({ url: '/pages/profile/history' }),
    },
  ];

  return (
    <View className="profile">
      <View className="user-card">
        {avatarUrl ? (
          <Image className="avatar" src={avatarUrl} mode="aspectFill" />
        ) : (
          <View className="avatar avatar-placeholder">
            <Text className="avatar-icon">{'\u{1F464}'}</Text>
          </View>
        )}
        <View className="user-info">
          <View className="name-row">
            <Text className="display-name">{displayName}</Text>
            {user ? (
              <Text className="role-tag">{roleLabels[user.role] ?? user.role}</Text>
            ) : null}
          </View>
          <Text className="username">@{user?.username}</Text>
          {user?.phoneNumber ? <Text className="meta">{user.phoneNumber}</Text> : null}
          {user?.email ? <Text className="meta">{user.email}</Text> : null}
        </View>
      </View>

      <View className="menu-list">
        {menuItems.map((item, index) => (
          <View
            key={item.label}
            className={`menu-item ${index > 0 ? 'menu-item-border' : ''}`}
            onClick={item.action}
          >
            <Text className="menu-icon">{item.icon}</Text>
            <View className="menu-text">
              <View className="menu-label">{item.label}</View>
              <View className="menu-desc">{item.desc}</View>
            </View>
            <Text className="menu-arrow">{'\u203A'}</Text>
          </View>
        ))}
      </View>

      <View className="signout-btn" onClick={handleSignOut}>
        <Text className="signout-text">退出登录</Text>
      </View>
    </View>
  );
}
