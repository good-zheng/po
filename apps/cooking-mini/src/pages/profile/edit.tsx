import { useState } from 'react';
import { View, Text, Image, Input, ScrollView } from '@tarojs/components';
import Taro from '@tarojs/taro';
import { AuthGuard } from '@/lib/auth/auth-guard';
import { useAuth } from '@/lib/auth/auth-context';
import { resolveAssetUrl } from '@/lib/api/client';
import { updateProfile, uploadAvatar } from '@/lib/api/users';
import './edit.scss';

const PHONE_PATTERN = /^1[3-9]\d{9}$/;

export default function ProfileEditPage() {
  return (
    <AuthGuard>
      <ProfileEditView />
    </AuthGuard>
  );
}

function ProfileEditView() {
  const { user, refreshUser } = useAuth();
  const [nickname, setNickname] = useState(user?.nickname ?? '');
  const [phoneNumber, setPhoneNumber] = useState(user?.phoneNumber ?? '');
  const [email, setEmail] = useState(user?.email ?? '');
  const [uploading, setUploading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  const avatarUrl = resolveAssetUrl(user?.avatar);

  const pickAvatar = () => {
    if (uploading) return;
    Taro.chooseImage({
      count: 1,
      sizeType: ['compressed'],
      sourceType: ['album', 'camera'],
      success: (res) => {
        const filePath = res.tempFilePaths[0];
        if (!filePath) return;
        setUploading(true);
        setFormError(null);
        uploadAvatar(filePath)
          .then(() => refreshUser())
          .then(() => Taro.showToast({ title: '头像已更新', icon: 'success' }))
          .catch(() => setFormError('头像上传失败，请稍后再试。'))
          .finally(() => setUploading(false));
      },
    });
  };

  const handleSubmit = () => {
    if (saving) return;
    setFormError(null);
    const trimmedPhone = phoneNumber.trim();
    if (trimmedPhone && !PHONE_PATTERN.test(trimmedPhone)) {
      setFormError('手机号格式不正确');
      return;
    }
    setSaving(true);
    updateProfile({
      nickname: nickname.trim() || undefined,
      email: email.trim() || undefined,
      phoneNumber: trimmedPhone,
    })
      .then(() => refreshUser())
      .then(() => {
        Taro.showToast({ title: '已保存', icon: 'success' });
        setTimeout(() => Taro.navigateBack(), 800);
      })
      .catch(() => setFormError('保存失败，请稍后再试。'))
      .finally(() => setSaving(false));
  };

  return (
    <View className="profile-edit">
      <ScrollView className="edit-scroll" scrollY>
        <View className="avatar-block">
          <View className="avatar-wrap" onClick={pickAvatar}>
            {avatarUrl ? (
              <Image className="avatar-img" src={avatarUrl} mode="aspectFill" />
            ) : (
              <View className="avatar-img avatar-placeholder">
                <Text className="avatar-placeholder-icon">{'\u{1F464}'}</Text>
              </View>
            )}
            <View className="avatar-cam">
              <Text className="avatar-cam-icon">{'\u{1F4F7}'}</Text>
            </View>
          </View>
          <Text className="avatar-hint">{uploading ? '正在上传头像…' : '点击更换头像'}</Text>
        </View>

        {formError ? (
          <View className="form-error">
            <Text className="form-error-text">{formError}</Text>
          </View>
        ) : null}

        <View className="field">
          <Text className="field-label">昵称</Text>
          <Input
            className="field-input"
            placeholder="输入昵称"
            maxlength={30}
            value={nickname}
            onInput={(e) => setNickname(e.detail.value)}
          />
        </View>

        <View className="field">
          <Text className="field-label">手机号</Text>
          <Input
            className="field-input"
            placeholder="用于接收通知（选填）"
            type="number"
            maxlength={11}
            value={phoneNumber}
            onInput={(e) => setPhoneNumber(e.detail.value)}
          />
        </View>

        <View className="field">
          <Text className="field-label">邮箱</Text>
          <Input
            className="field-input"
            placeholder="选填"
            value={email}
            onInput={(e) => setEmail(e.detail.value)}
          />
        </View>

        <View className={`save-btn ${saving ? 'save-btn-disabled' : ''}`} onClick={handleSubmit}>
          <Text className="save-text">{saving ? '保存中…' : '保存'}</Text>
        </View>
      </ScrollView>
    </View>
  );
}
