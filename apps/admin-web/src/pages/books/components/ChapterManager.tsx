import { PlusOutlined } from '@ant-design/icons';
import {
  ModalForm,
  ProFormDigit,
  ProFormText,
  ProFormTextArea,
} from '@ant-design/pro-components';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  Button,
  Card,
  message,
  Popconfirm,
  Space,
  Table,
  Typography,
} from 'antd';
import { useState } from 'react';
import {
  type BookChapter,
  type ChapterRequest,
  createChapter,
  deleteChapter,
  getChapters,
  updateChapter,
} from '@/services/book';

const ChapterManager: React.FC<{ bookId: number }> = ({ bookId }) => {
  const [messageApi, contextHolder] = message.useMessage();
  const queryClient = useQueryClient();
  const [editTarget, setEditTarget] = useState<BookChapter | null>(null);
  const [modalOpen, setModalOpen] = useState(false);

  const { data, isLoading } = useQuery({
    queryKey: ['book-chapters', bookId],
    queryFn: () => getChapters(bookId),
  });
  const chapters = data?.data ?? [];

  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: ['book-chapters', bookId] });
    queryClient.invalidateQueries({ queryKey: ['book', bookId] });
  };

  const createMutation = useMutation({
    mutationFn: (body: ChapterRequest) => createChapter(bookId, body),
    onSuccess: () => {
      messageApi.success('章节创建成功');
      setModalOpen(false);
      invalidate();
    },
    onError: (err: Error) => messageApi.error(err.message || '创建失败'),
  });

  const updateMutation = useMutation({
    mutationFn: (vars: { chapterId: number; body: ChapterRequest }) =>
      updateChapter(bookId, vars.chapterId, vars.body),
    onSuccess: () => {
      messageApi.success('章节更新成功');
      setEditTarget(null);
      invalidate();
    },
    onError: (err: Error) => messageApi.error(err.message || '更新失败'),
  });

  const deleteMutation = useMutation({
    mutationFn: (chapterId: number) => deleteChapter(bookId, chapterId),
    onSuccess: () => {
      messageApi.success('章节已删除');
      invalidate();
    },
    onError: (err: Error) => messageApi.error(err.message || '删除失败'),
  });

  const columns = [
    {
      title: '序号',
      dataIndex: 'chapterIndex',
      width: 70,
    },
    {
      title: '章节标题',
      dataIndex: 'title',
      ellipsis: true,
      render: (_: unknown, record: BookChapter) => (
        <Typography.Link onClick={() => setEditTarget(record)}>
          {record.title}
        </Typography.Link>
      ),
    },
    {
      title: '字数',
      dataIndex: 'wordCount',
      width: 90,
      render: (_: unknown, record: BookChapter) =>
        record.wordCount.toLocaleString(),
    },
    {
      title: '更新时间',
      dataIndex: 'updatedAt',
      width: 170,
      render: (_: unknown, record: BookChapter) =>
        record.updatedAt?.replace('T', ' ').slice(0, 19) ?? '-',
    },
    {
      title: '操作',
      key: 'action',
      width: 130,
      render: (_: unknown, record: BookChapter) => (
        <Space size="small">
          <a onClick={() => setEditTarget(record)}>编辑</a>
          <Popconfirm
            title="确认删除"
            description={`确定要删除章节「${record.title}」吗？`}
            okText="确认"
            cancelText="取消"
            okButtonProps={{ danger: true }}
            onConfirm={() => deleteMutation.mutate(record.id)}
          >
            <a style={{ color: '#ff4d4f' }}>删除</a>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <>
      {contextHolder}
      <Card
        title="章节管理"
        style={{ marginBottom: 16 }}
        extra={
          <Button
            type="primary"
            size="small"
            icon={<PlusOutlined />}
            onClick={() => setModalOpen(true)}
          >
            新建章节
          </Button>
        }
      >
        <Table<BookChapter>
          rowKey="id"
          size="small"
          loading={isLoading}
          dataSource={chapters}
          columns={columns}
          pagination={{ pageSize: 10, showSizeChanger: true }}
        />

        {/* 新建章节 */}
        <ModalForm<ChapterRequest>
          title="新建章节"
          width={720}
          open={modalOpen}
          onOpenChange={setModalOpen}
          modalProps={{ destroyOnClose: true, maskClosable: false }}
          submitter={{
            searchConfig: { submitText: '保存', resetText: '取消' },
          }}
          onFinish={async (values) => {
            await createMutation.mutateAsync(values);
            return true;
          }}
        >
          <ProFormText
            name="title"
            label="章节标题"
            placeholder="请输入章节标题"
            rules={[{ required: true, message: '请输入章节标题' }]}
          />
          <ProFormDigit
            name="chapterIndex"
            label="章节序号"
            min={1}
            placeholder="留空则自动排在最后"
            tooltip="留空则自动排在最后"
          />
          <ProFormTextArea
            name="content"
            label="正文内容"
            placeholder="请输入章节正文"
            fieldProps={{ rows: 10 }}
          />
        </ModalForm>

        {/* 编辑章节 */}
        <ModalForm<ChapterRequest>
          title={`编辑章节${editTarget ? `：第${editTarget.chapterIndex}章` : ''}`}
          width={720}
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
                  title: editTarget.title,
                  chapterIndex: editTarget.chapterIndex,
                  content: editTarget.content ?? '',
                }
              : undefined
          }
          onFinish={async (values) => {
            if (editTarget) {
              await updateMutation.mutateAsync({
                chapterId: editTarget.id,
                body: values,
              });
            }
            return true;
          }}
        >
          <ProFormText
            name="title"
            label="章节标题"
            placeholder="请输入章节标题"
            rules={[{ required: true, message: '请输入章节标题' }]}
          />
          <ProFormDigit name="chapterIndex" label="章节序号" min={1} />
          <ProFormTextArea
            name="content"
            label="正文内容"
            placeholder="请输入章节正文"
            fieldProps={{ rows: 10 }}
          />
        </ModalForm>
      </Card>
    </>
  );
};

export default ChapterManager;
