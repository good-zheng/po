import {
  ActivityIndicator,
  Pressable,
  Text,
  TextInput,
  type TextInputProps,
  View,
} from 'react-native';

import { cn } from '@/lib/utils';

type TextFieldProps = TextInputProps & {
  label: string;
};

export function TextField({ label, ...props }: TextFieldProps) {
  return (
    <View className="gap-1.5">
      <Text className="text-sm font-medium text-stone-700 dark:text-stone-300">
        {label}
      </Text>
      <TextInput
        autoCapitalize="none"
        autoCorrect={false}
        className="rounded-2xl border border-stone-200 bg-stone-50 px-4 py-3 text-base text-stone-900 dark:border-stone-700 dark:bg-stone-800 dark:text-stone-50"
        placeholderTextColor="#a8a29e"
        {...props}
      />
    </View>
  );
}

export function FormError({ message }: { message: string | null }) {
  if (!message) {
    return null;
  }

  return (
    <View className="rounded-2xl bg-red-50 px-4 py-3 dark:bg-red-950">
      <Text className="text-sm text-red-600 dark:text-red-300">{message}</Text>
    </View>
  );
}

type SubmitButtonProps = {
  label: string;
  loading?: boolean;
  onPress: () => void;
};

export function SubmitButton({
  label,
  loading = false,
  onPress,
}: SubmitButtonProps) {
  return (
    <Pressable
      accessibilityRole="button"
      className={cn(
        'items-center justify-center rounded-full bg-brand-600 py-3.5',
        loading && 'opacity-60',
      )}
      disabled={loading}
      onPress={onPress}
    >
      {loading ? (
        <ActivityIndicator color="#ffffff" />
      ) : (
        <Text className="text-base font-semibold text-white">{label}</Text>
      )}
    </Pressable>
  );
}
