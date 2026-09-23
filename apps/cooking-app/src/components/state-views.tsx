import { ActivityIndicator, Pressable, Text, View } from 'react-native';

type EmptyStateProps = {
  title: string;
  description: string;
};

type ErrorStateProps = {
  error: unknown;
  onRetry: () => void;
};

export function LoadingState({
  message = '正在准备菜谱…',
}: {
  message?: string;
}) {
  return (
    <View className="flex-1 items-center justify-center py-16">
      <ActivityIndicator color="#ea580c" size="large" />
      <Text className="mt-3 text-sm text-stone-500 dark:text-stone-400">
        {message}
      </Text>
    </View>
  );
}

export function EmptyState({ title, description }: EmptyStateProps) {
  return (
    <View className="flex-1 items-center justify-center py-16">
      <Text className="text-lg font-semibold text-stone-900 dark:text-stone-50">
        {title}
      </Text>
      <Text className="mt-2 text-center text-sm text-stone-500 dark:text-stone-400">
        {description}
      </Text>
    </View>
  );
}

export function ErrorState({ error, onRetry }: ErrorStateProps) {
  const message =
    error instanceof Error ? error.message : '网络连接出现问题，请稍后再试。';

  return (
    <View className="flex-1 items-center justify-center py-16">
      <Text className="text-lg font-semibold text-stone-900 dark:text-stone-50">
        加载失败
      </Text>
      <Text className="mt-2 text-center text-sm text-stone-500 dark:text-stone-400">
        {message}
      </Text>
      <Pressable
        accessibilityRole="button"
        className="mt-5 rounded-full bg-brand-600 px-5 py-3"
        onPress={onRetry}
      >
        <Text className="font-semibold text-white">重新加载</Text>
      </Pressable>
    </View>
  );
}
