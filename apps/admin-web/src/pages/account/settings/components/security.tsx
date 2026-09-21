import {
  ModalForm,
  ProFormDependency,
  ProFormText,
} from '@ant-design/pro-components';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useModel } from '@umijs/max';
import { Button, List, message } from 'antd';
import React, { useState } from 'react';
import {
  changePassword,
  getCurrentUser,
  updateCurrentUser,
} from '@/services/user';

/** 手机号脱敏：138****8293 */
const maskPhone = (phone?: string | null) =>
  phone ? `${phone.slice(0, 3)}****${phone.slice(-4)}` : '';

/** 邮箱脱敏：a***@example.com */
const maskEmail = (email?: string | null) => {
  if (!email || !email.includes('@')) return '';
  const [name, domain] = email.split('@');
  return `${name.slice(0, 1)}***@${domain}`;
};

/** 新密码强度：按字符类型与长度粗略评估 */
const getPasswordStrength = (pwd?: string) => {
  if (!pwd) return null;
  let types = 0;
  if (/[a-z]/.test(pwd)) types += 1;
  if (/[A-Z]/.test(pwd)) types += 1;
  if (/\d/.test(pwd)) types += 1;
  if (/[^a-zA-Z0-9]/.test(pwd)) types += 1;
  if (pwd.length < 6) return { label: '弱', color: '#ff4d4f' };
  if (pwd.length >= 10 && types >= 3) {
    return { label: '强', color: '#52c41a' };
  }
  if (types >= 2) return { label: '中', color: '#faad14' };
  return { label: '弱', color: '#ff4d4f' };
};

type ContactField = 'phoneNumber' | 'email';

const SecurityView: React.FC = () => {
  const { setInitialState } = useModel('@@initialState');
  const queryClient = useQueryClient();
  const [messageApi, contextHolder] = message.useMessage();
  const [passwordVisible, setPasswordVisible] = useState(false);
  const [contactField, setContactField] = useState<ContactField | null>(null);

  // 与基本设置共享同一查询缓存，一处修改两处同步
  const { data: currentUser } = useQuery({
    queryKey: ['profile-current-user'],
    queryFn: () => getCurrentUser().then((res) => res.data),
  });

  /** 同步查询缓存与全局 currentUser（顶栏昵称头像） */
  const syncUser = (patch: { phoneNumber?: string; email?: string }) => {
    queryClient.setQueryData(
      ['profile-current-user'],
      (old?: { phoneNumber?: string | null; email?: string | null }) =>
        old ? { ...old, ...patch } : old,
    );
    setInitialState((s) => ({
      ...s,
      currentUser: {
        ...s?.currentUser,
        ...(patch.phoneNumber !== undefined
          ? { phoneNumber: patch.phoneNumber }
          : {}),
        ...(patch.email !== undefined ? { email: patch.email } : {}),
      },
    }));
  };

  const passwordMutation = useMutation({
    mutationFn: (data: { oldPassword: string; newPassword: string }) =>
      changePassword(data, { skipErrorHandler: true }),
    onSuccess: () => {
      setPasswordVisible(false);
      messageApi.success('密码修改成功，请重新登录');
      // 修改密码后强制重新登录：清 token、清全局状态、跳登录页
      localStorage.removeItem('token');
      setInitialState((s) => ({ ...s, currentUser: undefined }));
      setTimeout(() => {
        window.location.href = '/user/login';
      }, 1200);
    },
    onError: (err: Error) => {
      messageApi.error(err.message || '密码修改失败');
    },
  });

  const contactMutation = useMutation({
    mutationFn: (data: { phoneNumber?: string; email?: string }) =>
      updateCurrentUser(data, { skipErrorHandler: true }),
    onSuccess: (_res, variables) => {
      setContactField(null);
      messageApi.success('修改成功');
      syncUser(variables);
    },
    onError: (err: Error) => {
      messageApi.error(err.message || '修改失败');
    },
  });

  const contactItems: {
    field: ContactField;
    title: string;
    description: string;
  }[] = [
    {
      field: 'phoneNumber',
      title: '密保手机',
      description: currentUser?.phoneNumber
        ? `已绑定手机：${maskPhone(currentUser.phoneNumber)}`
        : '未绑定手机号，绑定后可用于找回账户',
    },
    {
      field: 'email',
      title: '备用邮箱',
      description: currentUser?.email
        ? `已绑定邮箱：${maskEmail(currentUser.email)}`
        : '未绑定邮箱，绑定后可用于找回账户',
    },
  ];

  return (
    <>
      {contextHolder}
      <List
        itemLayout="horizontal"
        dataSource={[
          {
            title: '账户密码',
            description: '定期更换密码有助于保护账户安全',
            actions: [
              <Button
                key="Modify"
                type="link"
                onClick={() => setPasswordVisible(true)}
              >
                修改
              </Button>,
            ],
          },
          ...contactItems.map((item) => ({
            title: item.title,
            description: item.description,
            actions: [
              <Button
                key="Modify"
                type="link"
                onClick={() => setContactField(item.field)}
              >
                修改
              </Button>,
            ],
          })),
        ]}
        renderItem={(item) => (
          <List.Item actions={item.actions}>
            <List.Item.Meta title={item.title} description={item.description} />
          </List.Item>
        )}
      />

      <ChangePasswordModal
        visible={passwordVisible}
        loading={passwordMutation.isPending}
        onCancel={() => setPasswordVisible(false)}
        onFinish={async (values) => {
          await passwordMutation.mutateAsync(values);
          return true;
        }}
      />

      <ContactFieldModal
        field={contactField}
        initialValue={
          contactField === 'phoneNumber'
            ? (currentUser?.phoneNumber ?? '')
            : (currentUser?.email ?? '')
        }
        loading={contactMutation.isPending}
        onCancel={() => setContactField(null)}
        onFinish={async (value) => {
          await contactMutation.mutateAsync(
            contactField === 'phoneNumber'
              ? { phoneNumber: value }
              : { email: value },
          );
          return true;
        }}
      />
    </>
  );
};

/** 修改密码弹窗：原密码 + 新密码 + 确认新密码 */
const ChangePasswordModal: React.FC<{
  visible: boolean;
  loading: boolean;
  onCancel: () => void;
  onFinish: (values: {
    oldPassword: string;
    newPassword: string;
  }) => Promise<boolean>;
}> = ({ visible, loading, onCancel, onFinish }) => {
  return (
    <ModalForm
      title="修改密码"
      width={420}
      open={visible}
      onFinish={onFinish}
      modalProps={{ destroyOnHidden: true, onCancel }}
      submitter={{ submitButtonProps: { loading } }}
    >
      <ProFormText.Password
        name="oldPassword"
        label="原密码"
        placeholder="请输入原密码"
        rules={[{ required: true, message: '请输入原密码' }]}
      />
      <ProFormText.Password
        name="newPassword"
        label="新密码"
        placeholder="6-32 位，建议包含字母和数字"
        rules={[
          { required: true, message: '请输入新密码' },
          { min: 6, max: 32, message: '密码长度需在 6-32 位之间' },
        ]}
        extra={
          <ProFormDependency name={['newPassword']}>
            {({ newPassword }) => {
              const strength = getPasswordStrength(newPassword);
              return strength ? (
                <span>
                  密码强度：
                  <span style={{ color: strength.color, fontWeight: 500 }}>
                    {strength.label}
                  </span>
                </span>
              ) : null;
            }}
          </ProFormDependency>
        }
      />
      <ProFormText.Password
        name="confirmPassword"
        label="确认新密码"
        placeholder="请再次输入新密码"
        rules={[
          { required: true, message: '请再次输入新密码' },
          ({ getFieldValue }) => ({
            validator(_, value) {
              if (!value || getFieldValue('newPassword') === value) {
                return Promise.resolve();
              }
              return Promise.reject(new Error('两次输入的密码不一致'));
            },
          }),
        ]}
      />
    </ModalForm>
  );
};

/** 修改密保手机/备用邮箱弹窗 */
const ContactFieldModal: React.FC<{
  field: ContactField | null;
  initialValue: string;
  loading: boolean;
  onCancel: () => void;
  onFinish: (value: string) => Promise<boolean>;
}> = ({ field, initialValue, loading, onCancel, onFinish }) => {
  const isPhone = field === 'phoneNumber';
  return (
    <ModalForm
      title={isPhone ? '修改密保手机' : '修改备用邮箱'}
      width={420}
      open={field !== null}
      onFinish={async (values) => onFinish(String(values.value || ''))}
      modalProps={{ destroyOnHidden: true, onCancel }}
      submitter={{ submitButtonProps: { loading } }}
      initialValues={{ value: initialValue }}
    >
      <ProFormText
        name="value"
        label={isPhone ? '手机号' : '邮箱'}
        placeholder={isPhone ? '请输入手机号' : '请输入邮箱'}
        rules={
          isPhone
            ? [
                { required: true, message: '请输入手机号' },
                {
                  pattern: /^1\d{10}$/,
                  message: '手机号格式不正确',
                },
              ]
            : [
                { required: true, message: '请输入邮箱' },
                { type: 'email', message: '邮箱格式不正确' },
              ]
        }
      />
    </ModalForm>
  );
};

export default SecurityView;
