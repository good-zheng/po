import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
import { Alert, Pressable, ScrollView, Text, View } from 'react-native';

import { resolveAssetUrl } from '@/lib/api/client';
import { useAuth } from '@/lib/auth/auth-context';
import { Image } from '@/lib/nativewind';

const roleLabels: Record<string, string> = {
  admin: '管理员',
  superadmin: '超级管理员',
  user: '普通用户',
};

type MenuItem = {
  icon: keyof typeof Ionicons.glyphMap;
  label: string;
  description: string;
  onPress: () => void;
};

export default function ProfileScreen() {
  const router = useRouter();
  const { user, signOut } = useAuth();
  const avatarUrl = resolveAssetUrl(user?.avatar);
  const displayName = user?.nickname?.trim() || user?.username || '未登录';

  const handleSignOut = () => {
    Alert.alert('退出登录', '确定要退出当前账号吗？', [
      { style: 'cancel', text: '取消' },
      {
        onPress: () => {
          void signOut();
        },
        style: 'destructive',
        text: '退出登录',
      },
    ]);
  };

  const menuItems: MenuItem[] = [
    {
      icon: 'create-outline',
      label: '编辑资料',
      description: '头像、昵称、手机号、邮箱',
      onPress: () => router.push('/profile/edit'),
    },
    {
      icon: 'restaurant-outline',
      label: '我的菜谱',
      description: '创建菜谱，查看审核进度',
      onPress: () => router.push('/profile/recipes'),
    },
    {
      icon: 'heart-outline',
      label: '我的收藏',
      description: '收藏过的菜谱',
      onPress: () => router.push('/profile/favorites'),
    },
    {
      icon: 'time-outline',
      label: '浏览历史',
      description: '最近看过的菜谱',
      onPress: () => router.push('/profile/history'),
    },
  ];

  return (
    <ScrollView
      className="flex-1 bg-stone-50 dark:bg-stone-950"
      contentContainerClassName="px-5 pt-5 pb-8"
    >
      <Text className="text-2xl font-bold text-stone-900 dark:text-stone-50">
        我的
      </Text>

      <View className="mt-5 flex-row items-center gap-4 rounded-3xl bg-white p-5 shadow-sm dark:bg-stone-900">
        {avatarUrl ? (
          <Image
            accessibilityLabel="用户头像"
            className="h-16 w-16 rounded-full bg-stone-200 dark:bg-stone-800"
            contentFit="cover"
            source={avatarUrl}
            transition={150}
          />
        ) : (
          <View className="h-16 w-16 items-center justify-center rounded-full bg-brand-50 dark:bg-stone-800">
            <Ionicons color="#ea580c" name="person" size={30} />
          </View>
        )}
        <View className="flex-1">
          <View className="flex-row items-center gap-2">
            <Text
              className="text-lg font-bold text-stone-900 dark:text-stone-50"
              numberOfLines={1}
            >
              {displayName}
            </Text>
            {user ? (
              <Text className="rounded-full bg-brand-50 px-2.5 py-1 text-xs font-medium text-brand-700 dark:bg-stone-800 dark:text-brand-500">
                {roleLabels[user.role] ?? user.role}
              </Text>
            ) : null}
          </View>
          <Text
            className="mt-1 text-sm text-stone-500 dark:text-stone-400"
            numberOfLines={1}
          >
            @{user?.username}
          </Text>
          {user?.phoneNumber ? (
            <Text
              className="mt-0.5 text-sm text-stone-500 dark:text-stone-400"
              numberOfLines={1}
            >
              {user.phoneNumber}
            </Text>
          ) : null}
          {user?.email ? (
            <Text
              className="mt-0.5 text-sm text-stone-500 dark:text-stone-400"
              numberOfLines={1}
            >
              {user.email}
            </Text>
          ) : null}
        </View>
      </View>

      <View className="mt-6 overflow-hidden rounded-3xl bg-white shadow-sm dark:bg-stone-900">
        {menuItems.map((item, index) => (
          <Pressable
            accessibilityRole="button"
            className={`flex-row items-center gap-3 px-5 py-4 active:bg-stone-50 dark:active:bg-stone-800 ${
              index > 0 ? 'border-t border-stone-100 dark:border-stone-800' : ''
            }`}
            key={item.label}
            onPress={item.onPress}
          >
            <Ionicons color="#ea580c" name={item.icon} size={20} />
            <View className="flex-1">
              <Text className="text-base font-semibold text-stone-900 dark:text-stone-50">
                {item.label}
              </Text>
              <Text className="mt-0.5 text-xs text-stone-500 dark:text-stone-400">
                {item.description}
              </Text>
            </View>
            <Ionicons color="#a8a29e" name="chevron-forward" size={18} />
          </Pressable>
        ))}
      </View>

      <Pressable
        accessibilityRole="button"
        className="mt-6 flex-row items-center justify-center gap-2 rounded-full border border-red-200 bg-white py-3.5 dark:border-red-900 dark:bg-stone-900"
        onPress={handleSignOut}
      >
        <Ionicons color="#dc2626" name="log-out-outline" size={18} />
        <Text className="text-base font-semibold text-red-600 dark:text-red-400">
          退出登录
        </Text>
      </Pressable>
    </ScrollView>
  );
}
