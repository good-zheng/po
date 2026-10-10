import { PlusOutlined } from '@ant-design/icons';
import {
  ModalForm,
  ProFormDigit,
  ProFormSelect,
  ProFormTextArea,
} from '@ant-design/pro-components';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Button, Card, message, Segmented, Space, Table, Tag } from 'antd';
import { useState } from 'react';
import {
  createForeshadow,
  type ForeshadowItem,
  type ForeshadowRequest,
  getForeshadows,
  updateForeshadow,
} from '@/services/novel';

const foreshadowStatusMap: Record<string, { label: string; color: string }> = {
  opened: { label: '未回收', color: 'warning' },
  paid: { label: '已回收', color: 'success' },
  abandoned: { label: '已放弃', color: 'default' },
};

const statusOptions = [
  { value: 'opened', label: '未回收' },
  { value: 'paid', label: '已回收' },
  { value: 'abandoned', label: '已放弃' },
];

/** 伏笔账是「读者会记得」的东西：埋了不还会变成烂尾，所以欠账必须常驻视野 */
const ForeshadowPanel: React.FC<{ bookId: number }> = ({ bookId }) => {
  const [messageApi, contextHolder] = message.useMessage();
  const queryClient = useQueryClient();
  const [status, setStatus] = useState<string>('');
  const [editTarget, setEditTarget] = useState<ForeshadowItem | null>(null);
  const [createOpen, setCreateOpen] = useState(false);

  const { data, isLoading } = useQuery({
    queryKey: ['novel-foreshadows', bookId, status],
    queryFn: () => getForeshadows(bookId, status || undefined),
  });
  const rows = data?.data ?? [];

  const invalidate = () =>
    queryClient.invalidateQueries({ queryKey: ['novel-foreshadows', bookId] });

  const saveMutation = useMutation({
    mutationFn: (vars: { foreshadowId?: number; body: ForeshadowRequest }) =>
      vars.foreshadowId == null
        ? createForeshadow(bookId, vars.body)
        : updateForeshadow(bookId, vars.foreshadowId, vars.body),
    onSuccess: () => {
      messageApi.success('伏笔账已更新');
      setEditTarget(null);
      setCreateOpen(false);
      invalidate();
    },
    onError: (err: Error) => messageApi.error(err.message || '保存失败'),
  });

  const columns = [
    { title: '伏笔内容', dataIndex: 'content', ellipsis: true },
    {
      title: '埋设章',
      dataIndex: 'plantedChapter',
      width: 100,
      render: (v: number) => `第 ${v} 章`,
    },
    {
      title: '应收于（弧）',
      dataIndex: 'dueByArc',
      width: 120,
      render: (v?: number | null) => v ?? '-',
    },
    {
      title: '回收章',
      dataIndex: 'payoffChapter',
      width: 100,
      render: (v?: number | null) => (v == null ? '-' : `第 ${v} 章`),
    },
    {
      title: '状态',
      dataIndex: 'status',
      width: 90,
      render: (v: string) => {
        const s = foreshadowStatusMap[v] ?? { label: v, color: 'default' };
        return <Tag color={s.color}>{s.label}</Tag>;
      },
    },
    {
      title: '操作',
      key: 'action',
      width: 70,
      render: (_: unknown, record: ForeshadowItem) => (
        <a onClick={() => setEditTarget(record)}>编辑</a>
      ),
    },
  ];

  const form = (
    <>
      <ProFormTextArea
        name="content"
        label="伏笔内容"
        placeholder="一句话说清读者被许诺了什么"
        fieldProps={{ rows: 3, maxLength: 512, showCount: true }}
        rules={[{ required: true, message: '请输入伏笔内容' }]}
      />
      <ProFormDigit
        name="plantedChapter"
        label="埋设章"
        min={1}
        fieldProps={{ precision: 0 }}
        tooltip="留空按当前最新章登记"
      />
      <ProFormDigit
        name="dueByArc"
        label="应收于第几弧"
        min={1}
        fieldProps={{ precision: 0 }}
        tooltip="逾期不报错，但它就是烂尾清单"
      />
      <ProFormDigit
        name="payoffChapter"
        label="回收章"
        min={1}
        fieldProps={{ precision: 0 }}
        tooltip="填了就把状态切到「已回收」"
      />
      <ProFormSelect name="status" label="状态" options={statusOptions} />
    </>
  );

  return (
    <>
      {contextHolder}
      <Card
        title="伏笔账"
        style={{ marginBottom: 16 }}
        extra={
          <Space>
            <Segmented
              value={status}
              onChange={(v) => setStatus(String(v))}
              options={[
                { label: '全部', value: '' },
                { label: '未回收', value: 'opened' },
                { label: '已回收', value: 'paid' },
                { label: '已放弃', value: 'abandoned' },
              ]}
            />
            <Button
              type="primary"
              size="small"
              icon={<PlusOutlined />}
              onClick={() => setCreateOpen(true)}
            >
              记一笔
            </Button>
          </Space>
        }
      >
        <Table<ForeshadowItem>
          rowKey="id"
          size="small"
          loading={isLoading}
          dataSource={rows}
          columns={columns}
          pagination={{ pageSize: 10, showSizeChanger: true }}
        />

        <ModalForm<ForeshadowRequest>
          title="登记伏笔"
          width={620}
          open={createOpen}
          onOpenChange={setCreateOpen}
          modalProps={{ destroyOnClose: true, maskClosable: false }}
          submitter={{
            searchConfig: { submitText: '保存', resetText: '取消' },
          }}
          initialValues={{ status: 'opened' }}
          onFinish={async (values) => {
            await saveMutation.mutateAsync({ body: values });
            return true;
          }}
        >
          {form}
        </ModalForm>

        <ModalForm<ForeshadowRequest>
          key={editTarget ? `fs-${editTarget.id}` : 'fs-none'}
          title={editTarget ? '编辑伏笔' : ''}
          width={620}
          open={!!editTarget}
          onOpenChange={(open) => {
            if (!open) setEditTarget(null);
          }}
          modalProps={{ destroyOnClose: true, maskClosable: false }}
          submitter={{
            searchConfig: { submitText: '保存', resetText: '取消' },
          }}
          initialValues={
            editTarget
              ? {
                  content: editTarget.content,
                  plantedChapter: editTarget.plantedChapter,
                  dueByArc: editTarget.dueByArc ?? undefined,
                  payoffChapter: editTarget.payoffChapter ?? undefined,
                  status: editTarget.status,
                }
              : undefined
          }
          onFinish={async (values) => {
            if (editTarget) {
              await saveMutation.mutateAsync({
                foreshadowId: editTarget.id,
                body: values,
              });
            }
            return true;
          }}
        >
          {form}
        </ModalForm>
      </Card>
    </>
  );
};

export default ForeshadowPanel;
