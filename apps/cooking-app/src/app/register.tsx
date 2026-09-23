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

export default function RegisterScreen() {
  const { signUp } = useAuth();
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async () => {
    const trimmedUsername = username.trim();
    const trimmedEmail = email.trim();
    if (!trimmedUsername || !password) {
      setError('请输入用户名和密码');
      return;
    }
    if (password !== confirmPassword) {
      setError('两次输入的密码不一致');
      return;
    }

    setError(null);
    setSubmitting(true);
    try {
      await signUp({
        email: trimmedEmail || undefined,
        password,
        username: trimmedUsername,
      });
    } catch (cause) {
      setError(
        cause instanceof ApiError ? cause.message : '注册失败，请稍后再试。',
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
            创建账号
          </Text>
          <Text className="mt-2 text-sm text-stone-500 dark:text-stone-400">
            注册成功后会自动登录
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
            autoComplete="email"
            keyboardType="email-address"
            label="邮箱（选填）"
            onChangeText={setEmail}
            placeholder="用于找回账号"
            returnKeyType="next"
            textContentType="emailAddress"
            value={email}
          />
          <TextField
            autoComplete="new-password"
            label="密码"
            onChangeText={setPassword}
            placeholder="请输入密码"
            returnKeyType="next"
            secureTextEntry
            textContentType="newPassword"
            value={password}
          />
          <TextField
            autoComplete="new-password"
            label="确认密码"
            onChangeText={setConfirmPassword}
            onSubmitEditing={() => void handleSubmit()}
            placeholder="请再次输入密码"
            returnKeyType="done"
            secureTextEntry
            textContentType="newPassword"
            value={confirmPassword}
          />
          <SubmitButton
            label="注册并登录"
            loading={submitting}
            onPress={() => void handleSubmit()}
          />
        </View>

        <View className="mt-6 flex-row items-center justify-center gap-1">
          <Text className="text-sm text-stone-500 dark:text-stone-400">
            已有账号？
          </Text>
          <Link
            className="text-sm font-semibold text-brand-600 dark:text-brand-500"
            href="/login"
          >
            去登录
          </Link>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}
