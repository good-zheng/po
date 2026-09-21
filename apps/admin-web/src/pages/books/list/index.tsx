import { PlusOutlined } from '@ant-design/icons';
import type { ActionType, ProColumns } from '@ant-design/pro-components';
import { PageContainer, ProTable } from '@ant-design/pro-components';
import { useMutation, useQuery } from '@tanstack/react-query';
import { history } from '@umijs/max';
import { Button, Modal, message, Space, Tag } from 'antd';
import { useMemo, useRef } from 'react';
import {
  type Book,
  deleteBook,
  getBookGenres,
  getBooks,
} from '@/services/book';
import { statusColorMap, statusOptions } from '../components/BookForm';

const genreColorMap: Record<string, string> = {
  fantasy: 'purple',
  wuxia: 'gold',
  scifi: 'blue',
  romance: 'magenta',
  mystery: 'volcano',
  history: 'geekblue',
  urban: 'cyan',
  game: 'green',
  horror: 'red',
  other: 'default',
};

const BookList: React.FC = () => {
  const actionRef = useRef<ActionType>(null);
  const [messageApi, contextHolder] = message.useMessage();

  // 预加载类型字典用于列筛选
  const { data: genresRes } = useQuery({
    queryKey: ['book-genres'],
    queryFn: getBookGenres,
    staleTime: 5 * 60 * 1000,
  });
  const genreOptions = useMemo(
    () =>
      genresRes?.data?.map((g) => ({ label: g.label, value: g.value })) ?? [],
    [genresRes],
  );
  const genreLabelMap = useMemo(() => {
    const map: Record<string, string> = {};
    genresRes?.data?.forEach((g) => {
      map[g.value] = g.label;
    });
    return map;
  }, [genresRes]);

  // 删除 mutation
  const delMutation = useMutation({
    mutationFn: deleteBook,
    onSuccess: () => {
      messageApi.success('删除成功');
      actionRef.current?.reloadAndRest?.();
    },
    onError: (err: Error) => {
      messageApi.error(err.message || '删除失败');
    },
  });

  const handleDelete = (record: Book) => {
    Modal.confirm({
      title: '确认删除',
      content: `确定要删除书籍「${record.title}」吗？其所有章节与角色将一并软删除。`,
      okText: '确认',
      cancelText: '取消',
      okButtonProps: { danger: true },
      onOk: () => delMutation.mutate(record.id),
    });
  };

  const columns: ProColumns<Book>[] = [
    {
      title: '书名',
      dataIndex: 'title',
      ellipsis: true,
      width: 200,
      render: (_, record) => (
        <a onClick={() => history.push(`/books/detail/${record.id}`)}>
          {record.title}
        </a>
      ),
    },
    {
      title: '类型',
      dataIndex: 'genre',
      valueType: 'select',
      fieldProps: { options: genreOptions },
      render: (_, record) =>
        record.genre ? (
          <Tag color={genreColorMap[record.genre] ?? 'default'}>
            {genreLabelMap[record.genre] ?? record.genre}
          </Tag>
        ) : (
          '-'
        ),
      width: 100,
    },
    {
      title: '状态',
      dataIndex: 'status',
      valueType: 'select',
      valueEnum: {
        ongoing: { text: '连载中', status: 'Processing' },
        completed: { text: '已完结', status: 'Success' },
        paused: { text: '暂停更新', status: 'Warning' },
      },
      render: (_, record) => (
        <Tag color={statusColorMap[record.status] ?? 'default'}>
          {statusOptions.find((s) => s.value === record.status)?.label ??
            record.status}
        </Tag>
      ),
      width: 110,
    },
    {
      title: '作者',
      dataIndex: 'author',
      ellipsis: true,
      search: false,
      render: (_, record) => record.author ?? '-',
      width: 120,
    },
    {
      title: '总字数',
      dataIndex: 'wordCount',
      search: false,
      sorter: true,
      width: 100,
      render: (_, record) => record.wordCount.toLocaleString(),
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
      title: '更新时间',
      dataIndex: 'updatedAt',
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
          <a onClick={() => history.push(`/books/detail/${record.id}`)}>详情</a>
          <a onClick={() => history.push(`/books/edit/${record.id}`)}>编辑</a>
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
        <ProTable<Book>
          headerTitle="小说管理"
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
              onClick={() => history.push('/books/create')}
            >
              新建书籍
            </Button>,
          ]}
          request={async (params) => {
            const { current = 1, pageSize = 20, title, genre, status } = params;
            try {
              const res = await getBooks({
                page: current - 1, // 后端分页从 0 开始
                size: pageSize,
                keyword: title || undefined,
                genre: genre || undefined,
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
    </>
  );
};

export default BookList;
