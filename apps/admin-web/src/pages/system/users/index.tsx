import { PlusOutlined } from '@ant-design/icons';
import type { ActionType, ProColumns } from '@ant-design/pro-components';
import { PageContainer, ProTable } from '@ant-design/pro-components';
import { useMutation } from '@tanstack/react-query';
import { useModel } from '@umijs/max';
import { Badge, Button, Modal, message, Space, Tag } from 'antd';
import { useRef, useState } from 'react';
import { deleteUser, getUsers, type UserItem } from '@/services/user';
import UserFormModal from './components/UserFormModal';

const roleRender = (role: string) => {
  const map: Record<string, { label: string; color: string }> = {
    superadmin: { label: '超级管理员', color: 'gold' },
    admin: { label: '管理员', color: 'blue' },
    user: { label: '普通用户', color: 'default' },
  };
  const item = map[role];
  return item ? <Tag color={item.color}>{item.label}</Tag> : role;
};

const statusRender = (status: string) => {
  const map: Record<
    string,
    { label: string; badge: 'success' | 'error' | 'default' }
  > = {
    active: { label: '启用', badge: 'success' },
    suspended: { label: '禁用', badge: 'error' },
    inactive: { label: '未激活', badge: 'default' },
    invited: { label: '已邀请', badge: 'default' },
  };
  const item = map[status];
  if (!item) return status;
  return <Badge status={item.badge} text={item.label} />;
};

const UserManagement: React.FC = () => {
  const actionRef = useRef<ActionType>(null);
  const [messageApi, contextHolder] = message.useMessage();
  const { initialState } = useModel('@@initialState');

  const operatorRole = initialState?.currentUser?.role;
  const operatorId = Number(initialState?.currentUser?.id);
  const isSuperAdmin = operatorRole === 'superadmin';

  const [modalVisible, setModalVisible] = useState(false);
  const [currentRow, setCurrentRow] = useState<UserItem | undefined>();

  const delMutation = useMutation({
    mutationFn: deleteUser,
    onSuccess: () => {
      messageApi.success('删除成功');
      actionRef.current?.reloadAndRest?.();
    },
    onError: (err: Error) => {
      messageApi.error(err.message || '删除失败');
    },
  });

  const handleDelete = (record: UserItem) => {
    Modal.confirm({
      title: '确认删除用户',
      content: `确定要删除用户「${record.username}」吗？该操作不可恢复。`,
      okText: '确认删除',
      cancelText: '取消',
      okButtonProps: { danger: true },
      onOk: () => delMutation.mutate(record.id),
    });
  };

  /** 管理员不能操作超级管理员；任何人不能操作自己（删除场景） */
  const canOperate = (record: UserItem) => {
    if (record.role === 'superadmin' && !isSuperAdmin) return false;
    return true;
  };
  const isSelf = (record: UserItem) => record.id === operatorId;

  const columns: ProColumns<UserItem>[] = [
    {
      title: '用户名',
      dataIndex: 'username',
      ellipsis: true,
      width: 140,
    },
    {
      title: '昵称',
      dataIndex: 'nickname',
      ellipsis: true,
      width: 120,
      search: false,
      render: (_, record) => record.nickname || '-',
    },
    {
      title: '邮箱',
      dataIndex: 'email',
      ellipsis: true,
      width: 200,
      search: false,
      render: (_, record) => record.email || '-',
    },
    {
      title: '手机号',
      dataIndex: 'phoneNumber',
      width: 130,
      search: false,
      render: (_, record) => record.phoneNumber || '-',
    },
    {
      title: '角色',
      dataIndex: 'role',
      width: 120,
      search: false,
      render: (_, record) => roleRender(record.role),
    },
    {
      title: '状态',
      dataIndex: 'status',
      width: 100,
      search: false,
      render: (_, record) => statusRender(record.status),
    },
    {
      title: '创建时间',
      dataIndex: 'createTime',
      valueType: 'dateTime',
      width: 170,
      search: false,
    },
    {
      title: '操作',
      valueType: 'option',
      width: 120,
      render: (_, record) => {
        if (!canOperate(record)) {
          return <span style={{ color: '#999' }}>-</span>;
        }
        return (
          <Space size="small">
            <a
              onClick={() => {
                setCurrentRow(record);
                setModalVisible(true);
              }}
            >
              编辑
            </a>
            {!isSelf(record) && (
              <a
                style={{ color: '#ff4d4f' }}
                onClick={() => handleDelete(record)}
              >
                删除
              </a>
            )}
          </Space>
        );
      },
    },
  ];

  return (
    <>
      {contextHolder}
      <PageContainer>
        <ProTable<UserItem>
          headerTitle="用户管理"
          actionRef={actionRef}
          rowKey="id"
          search={{ labelWidth: 'auto' }}
          pagination={{ defaultPageSize: 10, showSizeChanger: true }}
          toolBarRender={() => [
            <Button
              key="create"
              type="primary"
              icon={<PlusOutlined />}
              onClick={() => {
                setCurrentRow(undefined);
                setModalVisible(true);
              }}
            >
              新建用户
            </Button>,
          ]}
          request={async (params) => {
            const { current = 1, pageSize = 10, username } = params;
            try {
              const res = await getUsers({
                page: current - 1, // 后端分页从 0 开始
                size: pageSize,
                keyword: username || undefined,
              });
              const page = res.data;
              return {
                data: page.content,
                success: true,
                total: page.totalElements,
              };
            } catch (err: unknown) {
              const errorMsg = err instanceof Error ? err.message : '加载失败';
              messageApi.error(errorMsg);
              return { data: [], success: false, total: 0 };
            }
          }}
          columns={columns}
        />
      </PageContainer>

      <UserFormModal
        visible={modalVisible}
        operatorRole={operatorRole}
        operatorId={operatorId}
        currentRow={currentRow}
        onCancel={() => {
          setModalVisible(false);
          setCurrentRow(undefined);
        }}
        onFinish={() => {
          setModalVisible(false);
          setCurrentRow(undefined);
          actionRef.current?.reloadAndRest?.();
        }}
      />
    </>
  );
};

export default UserManagement;
