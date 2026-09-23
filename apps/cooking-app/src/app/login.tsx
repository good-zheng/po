import { Link } from 'expo-router';
import { useState } from 'react';
import {
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  Text,
  View,
} from 'react-native';

import { FormError, SubmitButton, TextField } from '@/components/form';
import { ApiError } from '@/lib/api/client';
import { useAuth } from '@/lib/auth/auth-context';

export default function LoginScreen() {
  const { signIn } = useAuth();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async () => {
    const trimmedUsername = username.trim();
    if (!trimmedUsername || !password) {
      setError('请输入用户名和密码');
      return;
    }

    setError(null);
    setSubmitting(true);
    try {
      await signIn(trimmedUsername, password);
    } catch (cause) {
      setError(
        cause instanceof ApiError ? cause.message : '登录失败，请稍后再试。',
      );
      setSubmitting(false);
    }
  };

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      className="flex-1 bg-stone-50 dark:bg-stone-950"
    >
      <ScrollView
        contentContainerClassName="flex-grow justify-center px-6 py-12"
        keyboardShouldPersistTaps="handled"
      >
        <View className="items-center">
          <Text className="text-3xl font-bold text-stone-900 dark:text-stone-50">
            PO 做菜
          </Text>
          <Text className="mt-2 text-sm text-stone-500 dark:text-stone-400">
            登录后开始探索菜谱
          </Text>
        </View>

        <View className="mt-8 gap-4 rounded-3xl bg-white p-5 shadow-sm dark:bg-stone-900">
          <FormError message={error} />
          <TextField
            autoComplete="username"
            label="用户名"
            onChangeText={setUsername}
            placeholder="请输入用户名"
            returnKeyType="next"
            textContentType="username"
            value={username}
          />
          <TextField
            autoComplete="current-password"
            label="密码"
            onChangeText={setPassword}
            onSubmitEditing={() => void handleSubmit()}
            placeholder="请输入密码"
            returnKeyType="done"
            secureTextEntry
            textContentType="password"
            value={password}
          />
          <SubmitButton
            label="登录"
            loading={submitting}
            onPress={() => void handleSubmit()}
          />
        </View>

        <View className="mt-6 flex-row items-center justify-center gap-1">
          <Text className="text-sm text-stone-500 dark:text-stone-400">
            还没有账号？
          </Text>
          <Link
            className="text-sm font-semibold text-brand-600 dark:text-brand-500"
            href="/register"
          >
            立即注册
          </Link>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}
