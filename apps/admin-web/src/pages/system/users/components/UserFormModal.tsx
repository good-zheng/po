import {
  ModalForm,
  ProFormRadio,
  ProFormText,
} from '@ant-design/pro-components';
import { useMutation } from '@tanstack/react-query';
import { Divider, message } from 'antd';
import {
  createUser,
  type UserItem,
  type UserRequest,
  updateUser,
} from '@/services/user';

type UserFormModalProps = {
  visible: boolean;
  /** 当前操作者角色，用于限制可选角色范围 */
  operatorRole?: string;
  /** 操作者用户 ID，禁止操作自己 */
  operatorId?: number;
  currentRow?: UserItem;
  onCancel: () => void;
  onFinish: () => void;
};

/** 角色选项：superadmin 仅超级管理员可授予 */
const allRoleOptions = [
  { label: '超级管理员', value: 'superadmin' },
  { label: '管理员', value: 'admin' },
  { label: '普通用户', value: 'user' },
];

const adminRoleOptions = [
  { label: '管理员', value: 'admin' },
  { label: '普通用户', value: 'user' },
];

const statusOptions = [
  { label: '启用', value: 'active' },
  { label: '禁用', value: 'suspended' },
];

/** 编辑时可被清空的字段：提交时需显式传空字符串 */
const CLEARABLE_FIELDS = ['nickname', 'email', 'phoneNumber'] as const;

const UserFormModal: React.FC<UserFormModalProps> = ({
  visible,
  operatorRole,
  operatorId,
  currentRow,
  onCancel,
  onFinish,
}) => {
  const isEdit = !!currentRow;
  const isSuperAdmin = operatorRole === 'superadmin';
  const [messageApi, contextHolder] = message.useMessage();

  // 角色选项按操作者权限过滤
  const roleOptions = isSuperAdmin ? allRoleOptions : adminRoleOptions;
  // 编辑目标为超级管理员时，仅超级管理员可修改其角色
  const targetIsSuperAdmin = currentRow?.role === 'superadmin';
  const roleDisabled = !isSuperAdmin && targetIsSuperAdmin;
  // 不能修改自己的角色
  const isSelf = Boolean(
    currentRow && operatorId && currentRow.id === operatorId,
  );

  const createMutation = useMutation({
    mutationFn: createUser,
    onSuccess: () => {
      messageApi.success('用户创建成功');
      onFinish();
    },
    onError: (err: Error) => {
      messageApi.error(err.message || '创建失败');
    },
  });

  const updateMutation = useMutation({
    mutationFn: (data: Partial<UserRequest>) =>
      updateUser(currentRow!.id, data),
    onSuccess: () => {
      messageApi.success('用户更新成功');
      onFinish();
    },
    onError: (err: Error) => {
      messageApi.error(err.message || '更新失败');
    },
  });

  const handleSubmit = async (values: UserRequest) => {
    if (isEdit) {
      const payload: Partial<UserRequest> = { ...values };
      // 自己的角色和状态不可通过编辑修改
      if (isSelf) {
        delete payload.role;
        delete payload.status;
      }
      // 输入框清空后值为 undefined，JSON 序列化时字段会丢失，
      // 后端以 null 判断跳过更新，导致无法清空已有信息；
      // 显式补为空字符串，确保后端能将对应字段置空
      CLEARABLE_FIELDS.forEach((key) => {
        if (payload[key] == null) {
          payload[key] = '';
        }
      });
      await updateMutation.mutateAsync(payload);
    } else {
      await createMutation.mutateAsync(values);
    }
    return true;
  };

  const loading = createMutation.isPending || updateMutation.isPending;

  return (
    <>
      {contextHolder}
      <ModalForm
        title={isEdit ? `编辑用户：${currentRow?.username}` : '新建用户'}
        open={visible}
        modalProps={{
          destroyOnHidden: true,
          onCancel,
          confirmLoading: loading,
        }}
        width={560}
        onFinish={handleSubmit}
        submitter={{ submitButtonProps: { loading } }}
        initialValues={
          isEdit
            ? {
                nickname: currentRow?.nickname ?? '',
                email: currentRow?.email ?? '',
                phoneNumber: currentRow?.phoneNumber ?? '',
                role: currentRow?.role,
                status: currentRow?.status,
              }
            : {
                role: 'user',
                status: 'active',
              }
        }
      >
        {!isEdit && (
          <>
            <ProFormText
              name="username"
              label="用户名"
              placeholder="登录用户名"
              rules={[{ required: true, message: '请输入用户名' }]}
            />
            <ProFormText.Password
              name="password"
              label="初始密码"
              placeholder="留空默认为 123456"
            />
          </>
        )}
        <ProFormText name="nickname" label="昵称" placeholder="显示昵称" />
        <ProFormText name="email" label="邮箱" placeholder="电子邮箱" />
        <ProFormText name="phoneNumber" label="手机号" placeholder="手机号码" />

        <Divider plain>权限与状态</Divider>
        <ProFormRadio.Group
          name="role"
          label="角色"
          options={roleOptions}
          disabled={roleDisabled || isSelf}
          extra={
            (roleDisabled && '仅超级管理员可修改超级管理员的角色') ||
            (isSelf && '不能修改自己的角色')
          }
        />
        <ProFormRadio.Group
          name="status"
          label="状态"
          options={statusOptions}
          disabled={isSelf}
          extra={isSelf ? '不能修改自己的状态' : undefined}
        />

        {isEdit && (
          <>
            <Divider plain>重置密码（可选）</Divider>
            <ProFormText.Password
              name="password"
              label="新密码"
              placeholder="留空则不修改密码"
            />
          </>
        )}
      </ModalForm>
    </>
  );
};

export default UserFormModal;
