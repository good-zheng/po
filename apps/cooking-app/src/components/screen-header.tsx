import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
import { Pressable, Text, useColorScheme, View } from 'react-native';

type ScreenHeaderProps = {
  title: string;
  subtitle?: string;
};

export function ScreenHeader({ title, subtitle }: ScreenHeaderProps) {
  const router = useRouter();
  const isDark = useColorScheme() === 'dark';

  return (
    <View className="flex-row items-center gap-3 px-5 pb-3 pt-4">
      <Pressable
        accessibilityLabel="返回"
        accessibilityRole="button"
        className="h-9 w-9 items-center justify-center rounded-full bg-white shadow-sm active:opacity-70 dark:bg-stone-900"
        hitSlop={8}
        onPress={() => router.back()}
      >
        <Ionicons
          color={isDark ? '#fafaf9' : '#1c1917'}
          name="chevron-back"
          size={20}
        />
      </Pressable>
      <View className="flex-1">
        <Text
          className="text-lg font-bold text-stone-900 dark:text-stone-50"
          numberOfLines={1}
        >
          {title}
        </Text>
        {subtitle ? (
          <Text
            className="mt-0.5 text-xs text-stone-500 dark:text-stone-400"
            numberOfLines={1}
          >
            {subtitle}
          </Text>
        ) : null}
      </View>
    </View>
  );
}
