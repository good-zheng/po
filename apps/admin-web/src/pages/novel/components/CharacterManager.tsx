import { PlusOutlined } from '@ant-design/icons';
import {
  ModalForm,
  ProFormText,
  ProFormTextArea,
} from '@ant-design/pro-components';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  Avatar,
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
  type BookCharacter,
  type CharacterRequest,
  createCharacter,
  deleteCharacter,
  getCharacters,
  updateCharacter,
} from '@/services/novel';

const CharacterManager: React.FC<{ bookId: number }> = ({ bookId }) => {
  const [messageApi, contextHolder] = message.useMessage();
  const queryClient = useQueryClient();
  const [editTarget, setEditTarget] = useState<BookCharacter | null>(null);
  const [modalOpen, setModalOpen] = useState(false);

  const { data, isLoading } = useQuery({
    queryKey: ['book-characters', bookId],
    queryFn: () => getCharacters(bookId),
  });
  const characters = data?.data ?? [];

  const invalidate = () =>
    queryClient.invalidateQueries({ queryKey: ['book-characters', bookId] });

  const createMutation = useMutation({
    mutationFn: (body: CharacterRequest) => createCharacter(bookId, body),
    onSuccess: () => {
      messageApi.success('角色创建成功');
      setModalOpen(false);
      invalidate();
    },
    onError: (err: Error) => messageApi.error(err.message || '创建失败'),
  });

  const updateMutation = useMutation({
    mutationFn: (vars: { characterId: number; body: CharacterRequest }) =>
      updateCharacter(bookId, vars.characterId, vars.body),
    onSuccess: () => {
      messageApi.success('角色更新成功');
      setEditTarget(null);
      invalidate();
    },
    onError: (err: Error) => messageApi.error(err.message || '更新失败'),
  });

  const deleteMutation = useMutation({
    mutationFn: (characterId: number) => deleteCharacter(bookId, characterId),
    onSuccess: () => {
      messageApi.success('角色已删除');
      invalidate();
    },
    onError: (err: Error) => messageApi.error(err.message || '删除失败'),
  });

  const columns = [
    {
      title: '头像',
      dataIndex: 'avatar',
      width: 70,
      render: (_: unknown, record: BookCharacter) => (
        <Avatar src={record.avatar || undefined}>
          {record.name?.slice(0, 1)}
        </Avatar>
      ),
    },
    {
      title: '角色名称',
      dataIndex: 'name',
      width: 160,
      render: (_: unknown, record: BookCharacter) => (
        <Typography.Link onClick={() => setEditTarget(record)}>
          {record.name}
        </Typography.Link>
      ),
    },
    {
      title: '角色介绍',
      dataIndex: 'description',
      ellipsis: true,
      render: (_: unknown, record: BookCharacter) => record.description ?? '-',
    },
    {
      title: '操作',
      key: 'action',
      width: 130,
      render: (_: unknown, record: BookCharacter) => (
        <Space size="small">
          <a onClick={() => setEditTarget(record)}>编辑</a>
          <Popconfirm
            title="确认删除"
            description={`确定要删除角色「${record.name}」吗？`}
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
        title="角色管理"
        extra={
          <Button
            type="primary"
            size="small"
            icon={<PlusOutlined />}
            onClick={() => setModalOpen(true)}
          >
            新建角色
          </Button>
        }
      >
        <Table<BookCharacter>
          rowKey="id"
          size="small"
          loading={isLoading}
          dataSource={characters}
          columns={columns}
          pagination={{ pageSize: 10, showSizeChanger: true }}
        />

        {/* 新建角色 */}
        <ModalForm<CharacterRequest>
          title="新建角色"
          width={560}
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
            name="name"
            label="角色名称"
            placeholder="请输入角色名称"
            rules={[{ required: true, message: '请输入角色名称' }]}
          />
          <ProFormText
            name="avatar"
            label="头像 URL"
            placeholder="图片链接，可留空"
          />
          <ProFormTextArea
            name="description"
            label="角色介绍"
            placeholder="请输入角色介绍"
            fieldProps={{ rows: 4 }}
          />
        </ModalForm>

        {/* 编辑角色 */}
        <ModalForm<CharacterRequest>
          title="编辑角色"
          width={560}
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
                  name: editTarget.name,
                  avatar: editTarget.avatar ?? '',
                  description: editTarget.description ?? '',
                }
              : undefined
          }
          onFinish={async (values) => {
            if (editTarget) {
              await updateMutation.mutateAsync({
                characterId: editTarget.id,
                body: values,
              });
            }
            return true;
          }}
        >
          <ProFormText
            name="name"
            label="角色名称"
            placeholder="请输入角色名称"
            rules={[{ required: true, message: '请输入角色名称' }]}
          />
          <ProFormText
            name="avatar"
            label="头像 URL"
            placeholder="图片链接，可留空"
          />
          <ProFormTextArea
            name="description"
            label="角色介绍"
            placeholder="请输入角色介绍"
            fieldProps={{ rows: 4 }}
          />
        </ModalForm>
      </Card>
    </>
  );
};

export default CharacterManager;
