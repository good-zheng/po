import '../global.css';
import '@/lib/nativewind';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import { StyleSheet, View } from 'react-native';
import { GestureHandlerRootView } from 'react-native-gesture-handler';

import { LoadingState } from '@/components/state-views';
import { AuthProvider, useAuth } from '@/lib/auth/auth-context';
import { CookingProvider } from '@/lib/cooking/cooking-context';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 30_000,
    },
  },
});

export default function RootLayout() {
  return (
    <GestureHandlerRootView style={styles.root}>
      <QueryClientProvider client={queryClient}>
        <AuthProvider>
          <CookingProvider>
            <StatusBar style="auto" />
            <RootNavigator />
          </CookingProvider>
        </AuthProvider>
      </QueryClientProvider>
    </GestureHandlerRootView>
  );
}

function RootNavigator() {
  const { status } = useAuth();

  if (status === 'loading') {
    return (
      <View className="flex-1 bg-stone-50 dark:bg-stone-950">
        <LoadingState message="正在恢复登录状态…" />
      </View>
    );
  }

  const isAuthenticated = status === 'authenticated';

  return (
    <Stack screenOptions={{ headerShown: false }}>
      <Stack.Protected guard={isAuthenticated}>
        <Stack.Screen name="(tabs)" />
        <Stack.Screen name="recipe/[id]" />
        <Stack.Screen name="recipe/form" />
        <Stack.Screen name="category/[id]" />
        <Stack.Screen name="profile/edit" />
        <Stack.Screen name="profile/favorites" />
        <Stack.Screen name="profile/history" />
        <Stack.Screen name="profile/recipes" />
        <Stack.Screen
          name="cook/[id]"
          options={{ animation: 'slide_from_bottom' }}
        />
      </Stack.Protected>
      <Stack.Protected guard={!isAuthenticated}>
        <Stack.Screen name="login" />
        <Stack.Screen name="register" />
      </Stack.Protected>
    </Stack>
  );
}

const styles = StyleSheet.create({
  root: {
    flex: 1,
  },
});
