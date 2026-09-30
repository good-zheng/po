import { CheckOutlined, CloseOutlined } from '@ant-design/icons';
import type { ActionType, ProColumns } from '@ant-design/pro-components';
import { PageContainer, ProTable } from '@ant-design/pro-components';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Badge, Button, Modal, message, Space, Tag } from 'antd';
import { useRef } from 'react';
import { approveUser, getPendingUsers, type UserItem } from '@/services/user';

const roleRender = (role: string) => {
  const map: Record<string, { label: string; color: string }> = {
    superadmin: { label: '超级管理员', color: 'gold' },
    admin: { label: '管理员', color: 'blue' },
    user: { label: '普通用户', color: 'default' },
  };
  const item = map[role];
  return item ? <Tag color={item.color}>{item.label}</Tag> : role;
};

const UserApproval: React.FC = () => {
  const actionRef = useRef<ActionType>(null);
  const [messageApi, contextHolder] = message.useMessage();
  const queryClient = useQueryClient();

  const pendingQuery = useQuery({
    queryKey: ['pendingUsers'],
    queryFn: async () => {
      const res = await getPendingUsers();
      return res.data || [];
    },
  });

  const approveMutation = useMutation({
    mutationFn: ({
      id,
      action,
    }: {
      id: number;
      action: 'approved' | 'rejected';
    }) => approveUser(id, action),
    onSuccess: (_, variables) => {
      messageApi.success(variables.action === 'approved' ? '已通过' : '已拒绝');
      queryClient.invalidateQueries({ queryKey: ['pendingUsers'] });
    },
    onError: (err: Error) => {
      messageApi.error(err.message || '操作失败');
    },
  });

  const handleApprove = (record: UserItem) => {
    Modal.confirm({
      title: '确认通过',
      content: `确定要通过用户「${record.username}」的注册申请吗？`,
      okText: '确认通过',
      cancelText: '取消',
      onOk: () => approveMutation.mutate({ id: record.id, action: 'approved' }),
    });
  };

  const handleReject = (record: UserItem) => {
    Modal.confirm({
      title: '确认拒绝',
      content: `确定要拒绝用户「${record.username}」的注册申请吗？`,
      okText: '确认拒绝',
      cancelText: '取消',
      okButtonProps: { danger: true },
      onOk: () => approveMutation.mutate({ id: record.id, action: 'rejected' }),
    });
  };

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
      render: (_, record) => record.nickname || '-',
    },
    {
      title: '角色',
      dataIndex: 'role',
      width: 120,
      render: (_, record) => roleRender(record.role),
    },
    {
      title: '审批状态',
      dataIndex: 'approvalStatus',
      width: 100,
      render: () => <Badge status="processing" text="待审批" />,
    },
    {
      title: '注册时间',
      dataIndex: 'createTime',
      valueType: 'dateTime',
      width: 170,
    },
    {
      title: '操作',
      valueType: 'option',
      width: 160,
      render: (_, record) => (
        <Space size="small">
          <Button
            type="link"
            size="small"
            icon={<CheckOutlined />}
            style={{ color: '#52c41a' }}
            onClick={() => handleApprove(record)}
          >
            通过
          </Button>
          <Button
            type="link"
            size="small"
            icon={<CloseOutlined />}
            danger
            onClick={() => handleReject(record)}
          >
            拒绝
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <>
      {contextHolder}
      <PageContainer>
        <ProTable<UserItem>
          headerTitle={`待审批用户${pendingQuery.data ? `（${pendingQuery.data.length}）` : ''}`}
          actionRef={actionRef}
          rowKey="id"
          search={false}
          pagination={{ defaultPageSize: 10, showSizeChanger: true }}
          dataSource={pendingQuery.data}
          loading={pendingQuery.isLoading}
          columns={columns}
        />
      </PageContainer>
    </>
  );
};

export default UserApproval;
