import { UploadOutlined } from '@ant-design/icons';
import type { ProFormInstance } from '@ant-design/pro-components';
import { ProForm, ProFormText } from '@ant-design/pro-components';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useModel } from '@umijs/max';
import { Button, message, Upload } from 'antd';
import React from 'react';
import {
  getCurrentUser,
  type ProfileRequest,
  updateCurrentUser,
  uploadAvatar,
} from '@/services/user';
import { DEFAULT_AVATAR } from '@/utils/avatar';
import useStyles from './index.style';

/** 头像大小上限（与后端一致）：2MB */
const MAX_AVATAR_SIZE = 2 * 1024 * 1024;

/** 可被清空的字段：提交时需显式传空字符串 */
const CLEARABLE_FIELDS = ['email', 'phoneNumber'] as const;

const BaseView: React.FC = () => {
  const { styles } = useStyles();
  const formRef = React.useRef<ProFormInstance>(undefined);
  const queryClient = useQueryClient();
  const { setInitialState } = useModel('@@initialState');
  const [messageApi, contextHolder] = message.useMessage();

  const { data: currentUser, isLoading: loading } = useQuery({
    queryKey: ['profile-current-user'],
    queryFn: () => getCurrentUser().then((res) => res.data),
  });

  /** 同步全局 currentUser（顶栏头像/昵称）与本地查询缓存 */
  const syncUser = (user: {
    nickname?: string | null;
    email?: string | null;
    phoneNumber?: string | null;
    avatar?: string | null;
  }) => {
    queryClient.setQueryData(
      ['profile-current-user'],
      (old?: {
        nickname?: string | null;
        email?: string | null;
        phoneNumber?: string | null;
        avatar?: string | null;
      }) => (old ? { ...old, ...user } : old),
    );
    setInitialState((s) => ({
      ...s,
      currentUser: {
        ...s?.currentUser,
        nickname: user.nickname ?? undefined,
        email: user.email ?? undefined,
        phoneNumber: user.phoneNumber ?? undefined,
        avatar: user.avatar ?? undefined,
      },
    }));
  };

  const updateMutation = useMutation({
    mutationFn: (data: ProfileRequest) =>
      updateCurrentUser(data, { skipErrorHandler: true }),
    onSuccess: (res) => {
      messageApi.success('更新基本信息成功');
      syncUser(res.data);
    },
    onError: (err: Error) => {
      messageApi.error(err.message || '更新失败');
    },
  });

  const avatarMutation = useMutation({
    mutationFn: (file: File) => uploadAvatar(file, { skipErrorHandler: true }),
    onSuccess: (res) => {
      messageApi.success('头像上传成功');
      // 后端已将 URL 写入 avatar 字段，直接用返回值同步界面
      syncUser({ avatar: res.data });
    },
    onError: (err: Error) => {
      messageApi.error(err.message || '头像上传失败');
    },
  });

  const handleFinish = async (values: ProfileRequest) => {
    const payload: ProfileRequest = { ...values };
    // 清空的字段值为 undefined，JSON 序列化时字段会丢失，
    // 后端以 null 判断跳过更新；显式补为空字符串确保能清空
    CLEARABLE_FIELDS.forEach((key) => {
      if (payload[key] == null) {
        payload[key] = '';
      }
    });
    await updateMutation.mutateAsync(payload);
    return true;
  };

  const handleAvatarUpload = (file: File) => {
    if (file.size > MAX_AVATAR_SIZE) {
      messageApi.error('头像图片不能超过 2MB');
      return;
    }
    avatarMutation.mutate(file);
  };

  return (
    <div className={styles.baseView}>
      {contextHolder}
      {loading ? null : (
        <>
          <div className={styles.left}>
            <ProForm
              formRef={formRef}
              layout="vertical"
              onFinish={handleFinish}
              submitter={{
                searchConfig: {
                  submitText: '更新基本信息',
                },
                render: (_, dom) => dom[1],
                submitButtonProps: { loading: updateMutation.isPending },
              }}
              initialValues={{
                nickname: currentUser?.nickname ?? '',
                email: currentUser?.email ?? '',
                phoneNumber: currentUser?.phoneNumber ?? '',
              }}
              requiredMark={false}
            >
              <ProFormText
                width="md"
                name="email"
                label="邮箱"
                rules={[{ type: 'email', message: '邮箱格式不正确' }]}
              />
              <ProFormText
                width="md"
                name="nickname"
                label="昵称"
                rules={[
                  {
                    required: true,
                    message: '请输入您的昵称!',
                  },
                ]}
              />
              <ProFormText width="md" name="phoneNumber" label="联系电话" />
            </ProForm>
          </div>
          <div className={styles.right}>
            <AvatarView
              avatar={currentUser?.avatar || DEFAULT_AVATAR}
              uploading={avatarMutation.isPending}
              onUpload={handleAvatarUpload}
            />
          </div>
        </>
      )}
    </div>
  );
};

const AvatarView = ({
  avatar,
  uploading,
  onUpload,
}: {
  avatar: string;
  uploading: boolean;
  onUpload: (file: File) => void;
}) => {
  const { styles } = useStyles();

  return (
    <>
      <div className={styles.avatar_title}>头像</div>
      <div className={styles.avatar}>
        <img src={avatar} alt="avatar" />
      </div>
      <Upload
        showUploadList={false}
        accept="image/jpeg,image/png,image/gif,image/webp"
        beforeUpload={(file) => {
          onUpload(file);
          return false; // 阻止组件自动上传，改为手动调用接口
        }}
      >
        <div className={styles.button_view}>
          <Button loading={uploading}>
            <UploadOutlined />
            更换头像
          </Button>
        </div>
      </Upload>
    </>
  );
};

export default BaseView;
