import { PlusOutlined } from '@ant-design/icons';
import type { ActionType, ProColumns } from '@ant-design/pro-components';
import { PageContainer, ProTable } from '@ant-design/pro-components';
import { useMutation, useQuery } from '@tanstack/react-query';
import { history } from '@umijs/max';
import { Badge, Button, Modal, message, Space, Tag } from 'antd';
import { useRef } from 'react';
import {
  deleteRecipe,
  getRecipeCategories,
  getRecipes,
  type Recipe,
} from '@/services/recipe';

const difficultyMap: Record<number, { text: string; color: string }> = {
  1: { text: '简单', color: 'green' },
  2: { text: '中等', color: 'orange' },
  3: { text: '困难', color: 'red' },
};

const RecipeList: React.FC = () => {
  const actionRef = useRef<ActionType>(null);
  const [messageApi, contextHolder] = message.useMessage();

  // 预加载分类用于列筛选
  const { data: categoriesRes } = useQuery({
    queryKey: ['recipe-categories'],
    queryFn: getRecipeCategories,
    staleTime: 5 * 60 * 1000,
  });
  const categoryOptions =
    categoriesRes?.data?.map((c) => ({ label: c.name, value: c.id })) ?? [];

  // 删除 mutation
  const delMutation = useMutation({
    mutationFn: deleteRecipe,
    onSuccess: () => {
      messageApi.success('删除成功');
      actionRef.current?.reloadAndRest?.();
    },
    onError: (err: Error) => {
      messageApi.error(err.message || '删除失败');
    },
  });

  const handleDelete = (record: Recipe) => {
    Modal.confirm({
      title: '确认删除',
      content: `确定要删除菜谱「${record.title}」吗？此操作为软删除，数据可恢复。`,
      okText: '确认',
      cancelText: '取消',
      okButtonProps: { danger: true },
      onOk: () => delMutation.mutate(record.id),
    });
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
      title: '分类',
      dataIndex: 'category',
      valueType: 'select',
      fieldProps: {
        mode: 'multiple',
        options: categoryOptions,
      },
      render: (_, record) => record.category ?? '-',
      search: true,
    },
    {
      title: '难度',
      dataIndex: 'difficulty',
      valueType: 'select',
      valueEnum: {
        1: { text: '简单', status: 'Success' },
        2: { text: '中等', status: 'Warning' },
        3: { text: '困难', status: 'Error' },
      },
      render: (_, record) => {
        const d = difficultyMap[record.difficulty];
        return d ? <Tag color={d.color}>{d.text}</Tag> : record.difficulty;
      },
      search: false,
    },
    {
      title: '准备(分钟)',
      dataIndex: 'prepTime',
      valueType: 'digit',
      search: false,
      render: (_, record) => record.prepTime ?? '-',
      width: 110,
    },
    {
      title: '烹饪(分钟)',
      dataIndex: 'cookTime',
      valueType: 'digit',
      search: false,
      render: (_, record) => record.cookTime ?? '-',
      width: 110,
    },
    {
      title: '份数',
      dataIndex: 'servings',
      search: false,
      render: (_, record) => record.servings ?? '-',
      width: 70,
    },
    {
      title: '公开',
      dataIndex: 'isPublic',
      valueType: 'select',
      valueEnum: {
        true: { text: '公开', status: 'Success' },
        false: { text: '私密', status: 'Default' },
      },
      render: (_, record) => (
        <Badge
          status={record.isPublic ? 'success' : 'default'}
          text={record.isPublic ? '公开' : '私密'}
        />
      ),
      search: false,
      width: 80,
    },
    {
      title: '点赞',
      dataIndex: 'likesCount',
      search: false,
      sorter: true,
      width: 80,
    },
    {
      title: '创建时间',
      dataIndex: 'createdAt',
      valueType: 'dateTime',
      search: false,
      sorter: true,
      width: 170,
    },
    {
      title: '操作',
      valueType: 'option',
      width: 140,
      render: (_, record) => (
        <Space size="small">
          <a onClick={() => history.push(`/recipes/detail/${record.id}`)}>
            详情
          </a>
          <a onClick={() => history.push(`/recipes/edit/${record.id}`)}>编辑</a>
          <a style={{ color: '#ff4d4f' }} onClick={() => handleDelete(record)}>
            删除
          </a>
        </Space>
      ),
    },
  ];

  return (
    <>
      {contextHolder}
      <PageContainer>
        <ProTable<Recipe>
          headerTitle="菜谱管理"
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
            <Button
              key="create"
              type="primary"
              icon={<PlusOutlined />}
              onClick={() => history.push('/recipes/create')}
            >
              新建菜谱
            </Button>,
          ]}
          request={async (params) => {
            const {
              current = 1,
              pageSize = 20,
              title,
              difficulty,
              isPublic,
              category,
            } = params;
            try {
              const res = await getRecipes({
                page: current - 1, // 后端分页从 0 开始
                size: pageSize,
                keyword: title || undefined,
                categoryIdStr: category ? category.join(',') : undefined,
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
    </>
  );
};

export default RecipeList;
