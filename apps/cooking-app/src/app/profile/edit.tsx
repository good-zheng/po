import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useRouter } from 'expo-router';
import { useState } from 'react';
import { KeyboardAvoidingView, Platform, ScrollView, View } from 'react-native';

import { FormError, SubmitButton, TextField } from '@/components/form';
import { ScreenHeader } from '@/components/screen-header';
import { ApiError } from '@/lib/api/client';
import { updateProfile } from '@/lib/api/users';
import { useAuth } from '@/lib/auth/auth-context';
import { userKeys } from '@/lib/query-keys';

export default function ProfileEditScreen() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const { user, refreshUser } = useAuth();

  const [nickname, setNickname] = useState(user?.nickname ?? '');
  const [phoneNumber, setPhoneNumber] = useState(user?.phoneNumber ?? '');
  const [email, setEmail] = useState(user?.email ?? '');
  const [formError, setFormError] = useState<string | null>(null);

  const mutation = useMutation({
    mutationFn: updateProfile,
    onError: (error) => {
      setFormError(
        error instanceof ApiError ? error.message : '保存失败，请稍后再试。',
      );
    },
    onSuccess: async () => {
      await refreshUser();
      queryClient.invalidateQueries({ queryKey: userKeys.me() });
      router.back();
    },
  });

  const handleSubmit = () => {
    setFormError(null);
    const trimmedPhone = phoneNumber.trim();
    if (trimmedPhone && !/^1[3-9]\d{9}$/.test(trimmedPhone)) {
      setFormError('手机号格式不正确');
      return;
    }
    mutation.mutate({
      nickname: nickname.trim() || undefined,
      phoneNumber: trimmedPhone,
      email: email.trim() || undefined,
    });
  };

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      className="flex-1 bg-stone-50 dark:bg-stone-950"
    >
      <ScreenHeader subtitle="昵称、手机号、邮箱" title="编辑资料" />
      <ScrollView
        contentContainerClassName="gap-4 px-5 pb-8"
        keyboardShouldPersistTaps="handled"
      >
        <FormError message={formError} />
        <TextField
          label="昵称"
          maxLength={30}
          onChangeText={setNickname}
          placeholder="输入昵称"
          value={nickname}
        />
        <TextField
          keyboardType="phone-pad"
          label="手机号"
          maxLength={11}
          onChangeText={setPhoneNumber}
          placeholder="用于接收通知（选填）"
          value={phoneNumber}
        />
        <TextField
          keyboardType="email-address"
          label="邮箱"
          onChangeText={setEmail}
          placeholder="选填"
          value={email}
        />
        <View className="mt-2">
          <SubmitButton
            label="保存"
            loading={mutation.isPending}
            onPress={handleSubmit}
          />
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}
