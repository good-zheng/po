import type { ActionType, ProColumns } from '@ant-design/pro-components';
import { PageContainer, ProTable } from '@ant-design/pro-components';
import { useMutation } from '@tanstack/react-query';
import { history } from '@umijs/max';
import { Badge, Button, Input, Modal, message, Space, Tag } from 'antd';
import { useRef, useState } from 'react';
import { auditRecipe, getReviewRecipes, type Recipe } from '@/services/recipe';

const statusMap: Record<
  string,
  { text: string; badge: 'warning' | 'success' | 'error' }
> = {
  pending: { text: '待审核', badge: 'warning' },
  approved: { text: '已通过', badge: 'success' },
  rejected: { text: '已驳回', badge: 'error' },
};

const difficultyMap: Record<number, { text: string; color: string }> = {
  1: { text: '简单', color: 'green' },
  2: { text: '中等', color: 'orange' },
  3: { text: '困难', color: 'red' },
};

const ReviewList: React.FC = () => {
  const actionRef = useRef<ActionType>(null);
  const [messageApi, contextHolder] = message.useMessage();
  const [rejectTarget, setRejectTarget] = useState<Recipe | null>(null);
  const [rejectReason, setRejectReason] = useState('');

  const auditMutation = useMutation({
    mutationFn: ({
      id,
      action,
      reason,
    }: {
      id: number;
      action: 'approve' | 'reject';
      reason?: string;
    }) => auditRecipe(id, { action, reason }),
    onSuccess: (_data, variables) => {
      messageApi.success(variables.action === 'approve' ? '已通过' : '已驳回');
      actionRef.current?.reload?.();
    },
    onError: (err: Error) => {
      messageApi.error(err.message || '操作失败');
    },
  });

  const handleApprove = (record: Recipe) => {
    Modal.confirm({
      title: '确认通过',
      content: `确定要通过菜谱「${record.title}」吗？通过后将对外公开。`,
      okText: '通过',
      cancelText: '取消',
      onOk: () => auditMutation.mutate({ id: record.id, action: 'approve' }),
    });
  };

  const openRejectModal = (record: Recipe) => {
    setRejectReason('');
    setRejectTarget(record);
  };

  const handleRejectOk = () => {
    if (!rejectTarget) {
      return;
    }
    const reason = rejectReason.trim();
    if (!reason) {
      messageApi.warning('请填写驳回原因');
      return;
    }
    auditMutation.mutate(
      { id: rejectTarget.id, action: 'reject', reason },
      { onSettled: () => setRejectTarget(null) },
    );
  };

  const columns: ProColumns<Recipe>[] = [
    {
      title: '菜谱名称',
      dataIndex: 'title',
      ellipsis: true,
      width: 180,
      render: (_, record) => (
        <a onClick={() => history.push(`/recipes/detail/${record.id}`)}>
          {record.title}
        </a>
      ),
    },
    {
      title: '审核状态',
      dataIndex: 'status',
      valueType: 'select',
      valueEnum: {
        pending: { text: '待审核' },
        approved: { text: '已通过' },
        rejected: { text: '已驳回' },
      },
      width: 110,
      render: (_, record) => {
        const s = record.status ? statusMap[record.status] : undefined;
        return s ? (
          <Badge status={s.badge} text={s.text} />
        ) : (
          <Badge status="default" text="未知" />
        );
      },
    },
    {
      title: '驳回原因',
      dataIndex: 'rejectReason',
      search: false,
      ellipsis: true,
      render: (_, record) => record.rejectReason || '-',
    },
    {
      title: '分类',
      dataIndex: 'category',
      search: false,
      width: 110,
      render: (_, record) => record.category ?? '-',
    },
    {
      title: '难度',
      dataIndex: 'difficulty',
      search: false,
      width: 80,
      render: (_, record) => {
        const d = difficultyMap[record.difficulty];
        return d ? <Tag color={d.color}>{d.text}</Tag> : record.difficulty;
      },
    },
    {
      title: '作者ID',
      dataIndex: 'authorId',
      search: false,
      width: 90,
    },
    {
      title: '点赞',
      dataIndex: 'likesCount',
      search: false,
      width: 70,
    },
    {
      title: '提交时间',
      dataIndex: 'createdAt',
      valueType: 'dateTime',
      search: false,
      sorter: true,
      width: 170,
    },
    {
      title: '操作',
      valueType: 'option',
      width: 200,
      render: (_, record) => (
        <Space size="small">
          <a onClick={() => history.push(`/recipes/detail/${record.id}`)}>
            详情
          </a>
          {record.status !== 'approved' && (
            <a onClick={() => handleApprove(record)}>通过</a>
          )}
          {record.status !== 'rejected' && (
            <a
              style={{ color: '#ff4d4f' }}
              onClick={() => openRejectModal(record)}
            >
              驳回
            </a>
          )}
        </Space>
      ),
    },
  ];

  return (
    <>
      {contextHolder}
      <PageContainer>
        <ProTable<Recipe>
          headerTitle="菜谱审核"
          actionRef={actionRef}
          rowKey="id"
          search={{
            labelWidth: 'auto',
          }}
          pagination={{
            defaultPageSize: 20,
            showSizeChanger: true,
          }}
          toolBarRender={() => [
            <Button key="refresh" onClick={() => actionRef.current?.reload?.()}>
              刷新
            </Button>,
          ]}
          request={async (params) => {
            const { current = 1, pageSize = 20, title, status } = params;
            try {
              const res = await getReviewRecipes({
                page: current - 1,
                size: pageSize,
                keyword: title || undefined,
                status: status || undefined,
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
      <Modal
        title={rejectTarget ? `驳回「${rejectTarget.title}」` : '驳回'}
        open={!!rejectTarget}
        okText="确认驳回"
        okButtonProps={{ danger: true, loading: auditMutation.isPending }}
        cancelText="取消"
        onOk={handleRejectOk}
        onCancel={() => setRejectTarget(null)}
      >
        <Input.TextArea
          rows={3}
          maxLength={200}
          showCount
          placeholder="请填写驳回原因（必填），将展示给菜谱作者"
          value={rejectReason}
          onChange={(e) => setRejectReason(e.target.value)}
        />
      </Modal>
    </>
  );
};

export default ReviewList;
