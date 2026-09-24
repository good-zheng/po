import type { ActionType, ProColumns } from '@ant-design/pro-components';
import { PageContainer, ProTable } from '@ant-design/pro-components';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Button, Form, Input, InputNumber, Modal, message, Space } from 'antd';
import { useRef, useState } from 'react';
import {
  createRecipeCategory,
  deleteRecipeCategory,
  getRecipeCategories,
  type RecipeCategory,
  type RecipeCategoryRequest,
  updateRecipeCategory,
} from '@/services/recipe';

const CategoryList: React.FC = () => {
  const actionRef = useRef<ActionType>(null);
  const queryClient = useQueryClient();
  const [messageApi, contextHolder] = message.useMessage();
  const [form] = Form.useForm<RecipeCategoryRequest>();
  const [editing, setEditing] = useState<RecipeCategory | null>(null);
  const [modalOpen, setModalOpen] = useState(false);

  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: ['recipe-categories'] });
    actionRef.current?.reload?.();
  };

  const createMutation = useMutation({
    mutationFn: (body: RecipeCategoryRequest) => createRecipeCategory(body),
    onSuccess: () => {
      messageApi.success('创建成功');
      setModalOpen(false);
      invalidate();
    },
    onError: (err: Error) => messageApi.error(err.message || '创建失败'),
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, body }: { id: number; body: RecipeCategoryRequest }) =>
      updateRecipeCategory(id, body),
    onSuccess: () => {
      messageApi.success('更新成功');
      setModalOpen(false);
      invalidate();
    },
    onError: (err: Error) => messageApi.error(err.message || '更新失败'),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => deleteRecipeCategory(id),
    onSuccess: () => {
      messageApi.success('删除成功');
      invalidate();
    },
    onError: (err: Error) => messageApi.error(err.message || '删除失败'),
  });

  const openCreate = () => {
    setEditing(null);
    form.resetFields();
    form.setFieldsValue({ sortOrder: 0 });
    setModalOpen(true);
  };

  const openEdit = (record: RecipeCategory) => {
    setEditing(record);
    form.setFieldsValue({
      name: record.name,
      icon: record.icon ?? undefined,
      description: record.description ?? undefined,
      sortOrder: record.sortOrder,
    });
    setModalOpen(true);
  };

  const handleOk = async () => {
    const values = await form.validateFields();
    const body: RecipeCategoryRequest = {
      name: values.name.trim(),
      icon: values.icon?.trim() || undefined,
      description: values.description?.trim() || undefined,
      sortOrder: values.sortOrder ?? 0,
    };
    if (editing) {
      updateMutation.mutate({ id: editing.id, body });
    } else {
      createMutation.mutate(body);
    }
  };

  const handleDelete = (record: RecipeCategory) => {
    Modal.confirm({
      title: '确认删除',
      content: `确定要删除分类「${record.name}」吗？删除后不再展示。`,
      okText: '删除',
      okButtonProps: { danger: true },
      cancelText: '取消',
      onOk: () => deleteMutation.mutate(record.id),
    });
  };

  const columns: ProColumns<RecipeCategory>[] = [
    {
      title: '分类名称',
      dataIndex: 'name',
      width: 160,
    },
    {
      title: '图标',
      dataIndex: 'icon',
      search: false,
      width: 100,
      render: (_, record) => record.icon || '-',
    },
    {
      title: '描述',
      dataIndex: 'description',
      search: false,
      ellipsis: true,
      render: (_, record) => record.description || '-',
    },
    {
      title: '排序权重',
      dataIndex: 'sortOrder',
      search: false,
      width: 100,
      sorter: (a, b) => (a.sortOrder ?? 0) - (b.sortOrder ?? 0),
    },
    {
      title: '创建时间',
      dataIndex: 'createdAt',
      valueType: 'dateTime',
      search: false,
      width: 170,
    },
    {
      title: '操作',
      valueType: 'option',
      width: 140,
      render: (_, record) => (
        <Space size="small">
          <a onClick={() => openEdit(record)}>编辑</a>
          <a style={{ color: '#ff4d4f' }} onClick={() => handleDelete(record)}>
            删除
          </a>
        </Space>
      ),
    },
  ];

  const submitting = createMutation.isPending || updateMutation.isPending;

  return (
    <>
      {contextHolder}
      <PageContainer>
        <ProTable<RecipeCategory>
          headerTitle="菜谱分类"
          actionRef={actionRef}
          rowKey="id"
          search={{
            labelWidth: 'auto',
            filterType: 'light',
          }}
          pagination={false}
          toolBarRender={() => [
            <Button key="create" type="primary" onClick={openCreate}>
              新建分类
            </Button>,
          ]}
          request={async (params) => {
            const { name } = params;
            try {
              const res = await getRecipeCategories();
              const all = res.data ?? [];
              const filtered = name
                ? all.filter((item) => item.name.includes(name))
                : all;
              return { data: filtered, success: true, total: filtered.length };
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
        title={editing ? `编辑分类「${editing.name}」` : '新建分类'}
        open={modalOpen}
        okText="保存"
        okButtonProps={{ loading: submitting }}
        cancelText="取消"
        onOk={handleOk}
        onCancel={() => setModalOpen(false)}
        destroyOnHidden
      >
        <Form form={form} layout="vertical" preserve={false}>
          <Form.Item
            name="name"
            label="分类名称"
            rules={[
              { required: true, message: '请输入分类名称' },
              { max: 50, message: '不能超过 50 个字符' },
            ]}
          >
            <Input placeholder="如：家常菜" maxLength={50} showCount />
          </Form.Item>
          <Form.Item name="icon" label="图标">
            <Input
              placeholder="Lucide 图标名或 emoji，可留空"
              maxLength={100}
            />
          </Form.Item>
          <Form.Item
            name="description"
            label="描述"
            rules={[{ max: 200, message: '不能超过 200 个字符' }]}
          >
            <Input.TextArea
              rows={2}
              placeholder="分类描述，可留空"
              maxLength={200}
              showCount
            />
          </Form.Item>
          <Form.Item name="sortOrder" label="排序权重">
            <InputNumber min={0} precision={0} style={{ width: '100%' }} />
          </Form.Item>
        </Form>
      </Modal>
    </>
  );
};

export default CategoryList;
