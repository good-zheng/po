import { Ionicons } from '@expo/vector-icons';
import { Tabs } from 'expo-router';
import { useColorScheme } from 'react-native';

export default function TabLayout() {
  const colorScheme = useColorScheme();
  const isDark = colorScheme === 'dark';
  const backgroundColor = isDark ? '#1c1917' : '#fafaf9';

  return (
    <Tabs
      screenOptions={{
        headerShadowVisible: false,
        headerStyle: { backgroundColor },
        headerTintColor: isDark ? '#fafaf9' : '#1c1917',
        headerTitleStyle: { fontWeight: '700' },
        sceneStyle: { backgroundColor },
        tabBarActiveTintColor: '#ea580c',
        tabBarInactiveTintColor: isDark ? '#a8a29e' : '#78716c',
        tabBarStyle: {
          backgroundColor,
          borderTopColor: isDark ? '#292524' : '#e7e5e4',
        },
      }}
    >
      <Tabs.Screen
        name="index"
        options={{
          title: '首页',
          tabBarIcon: ({ color, size, focused }) => (
            <Ionicons
              color={color}
              name={focused ? 'home' : 'home-outline'}
              size={size}
            />
          ),
        }}
      />
      <Tabs.Screen
        name="categories"
        options={{
          title: '分类',
          tabBarIcon: ({ color, size, focused }) => (
            <Ionicons
              color={color}
              name={focused ? 'grid' : 'grid-outline'}
              size={size}
            />
          ),
        }}
      />
      <Tabs.Screen
        name="ai"
        options={{
          title: 'AI 指导',
          headerShown: false,
          tabBarIcon: ({ color, size, focused }) => (
            <Ionicons
              color={color}
              name={
                focused ? 'chatbubble-ellipses' : 'chatbubble-ellipses-outline'
              }
              size={size}
            />
          ),
        }}
      />
      <Tabs.Screen
        name="profile"
        options={{
          title: '我的',
          tabBarIcon: ({ color, size, focused }) => (
            <Ionicons
              color={color}
              name={focused ? 'person' : 'person-outline'}
              size={size}
            />
          ),
        }}
      />
    </Tabs>
  );
}
