import { Ionicons } from '@expo/vector-icons';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import * as ImagePicker from 'expo-image-picker';
import { useRouter } from 'expo-router';
import { useState } from 'react';
import {
  KeyboardAvoidingView,
  Platform,
  Pressable,
  ScrollView,
  Text,
  View,
} from 'react-native';

import { FormError, SubmitButton, TextField } from '@/components/form';
import { ScreenHeader } from '@/components/screen-header';
import { ApiError, resolveAssetUrl } from '@/lib/api/client';
import { updateProfile, uploadAvatar } from '@/lib/api/users';
import { useAuth } from '@/lib/auth/auth-context';
import { Image } from '@/lib/nativewind';
import { userKeys } from '@/lib/query-keys';

export default function ProfileEditScreen() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const { user, refreshUser } = useAuth();

  const [nickname, setNickname] = useState(user?.nickname ?? '');
  const [phoneNumber, setPhoneNumber] = useState(user?.phoneNumber ?? '');
  const [email, setEmail] = useState(user?.email ?? '');
  const [formError, setFormError] = useState<string | null>(null);

  const avatarMutation = useMutation({
    mutationFn: uploadAvatar,
    onError: (error) => {
      setFormError(
        error instanceof ApiError
          ? error.message
          : '头像上传失败，请稍后再试。',
      );
    },
    onSuccess: async () => {
      await refreshUser();
      await queryClient.invalidateQueries({ queryKey: userKeys.me() });
    },
  });

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

  const pickAvatar = async () => {
    const result = await ImagePicker.launchImageLibraryAsync({
      allowsEditing: true,
      aspect: [1, 1],
      mediaTypes: ['images'],
      quality: 0.8,
    });

    if (result.canceled) {
      return;
    }

    avatarMutation.mutate(result.assets[0].uri);
  };

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
      <ScreenHeader subtitle="头像、昵称、手机号、邮箱" title="编辑资料" />
      <ScrollView
        contentContainerClassName="gap-4 px-5 pb-8"
        keyboardShouldPersistTaps="handled"
      >
        <View className="items-center py-2">
          <Pressable
            accessibilityLabel="更换头像"
            accessibilityRole="button"
            className="active:opacity-80"
            disabled={avatarMutation.isPending}
            onPress={() => void pickAvatar()}
          >
            {resolveAssetUrl(user?.avatar) ? (
              <Image
                accessibilityLabel="当前头像"
                className="h-20 w-20 rounded-full bg-stone-200 dark:bg-stone-800"
                contentFit="cover"
                source={resolveAssetUrl(user?.avatar)}
                transition={150}
              />
            ) : (
              <View className="h-20 w-20 items-center justify-center rounded-full bg-brand-50 dark:bg-stone-800">
                <Ionicons color="#ea580c" name="person" size={36} />
              </View>
            )}
            <View className="absolute bottom-0 right-0 h-6 w-6 items-center justify-center rounded-full bg-brand-600">
              {avatarMutation.isPending ? (
                <Ionicons color="#ffffff" name="sync" size={13} />
              ) : (
                <Ionicons color="#ffffff" name="camera" size={13} />
              )}
            </View>
          </Pressable>
          <Text className="mt-2 text-xs text-stone-500 dark:text-stone-400">
            {avatarMutation.isPending ? '正在上传头像…' : '点击更换头像'}
          </Text>
        </View>
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
