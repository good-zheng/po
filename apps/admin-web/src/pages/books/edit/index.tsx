import { PageContainer } from '@ant-design/pro-components';
import { useMutation, useQuery } from '@tanstack/react-query';
import { history, useParams } from '@umijs/max';
import { Card, Empty, message, Result, Skeleton } from 'antd';
import { useMemo } from 'react';
import { type BookRequest, getBook, updateBook } from '@/services/book';
import BookForm, { buildBookInitialValues } from '../components/BookForm';

const BookEdit: React.FC = () => {
  const params = useParams<{ id: string }>();
  const id = Number(params.id);
  const validId = Number.isFinite(id) && id > 0;
  const [messageApi, contextHolder] = message.useMessage();

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ['book', id],
    queryFn: () => getBook(id),
    enabled: validId,
  });

  const updateMutation = useMutation({
    mutationFn: (data: BookRequest) => updateBook(id, data),
    onSuccess: () => {
      messageApi.success('书籍更新成功');
      history.push(`/books/detail/${id}`);
    },
    onError: (err: Error) => {
      messageApi.error(err.message || '更新失败');
    },
  });

  const initialValues = useMemo(
    () => buildBookInitialValues(data?.data),
    [data],
  );

  let content: React.ReactNode;
  if (!validId) {
    content = (
      <Card>
        <Empty description="无效的书籍 ID" />
      </Card>
    );
  } else if (isLoading) {
    content = (
      <Card>
        <Skeleton active paragraph={{ rows: 8 }} />
      </Card>
    );
  } else if (isError || !data?.data) {
    content = (
      <Result
        status="404"
        title="加载失败"
        subTitle={
          error instanceof Error ? error.message : '书籍不存在或已被删除'
        }
        extra={<a onClick={() => history.push('/books/list')}>返回书籍列表</a>}
      />
    );
  } else {
    content = (
      <Card>
        <BookForm
          key={id}
          initialValues={initialValues}
          submitting={updateMutation.isPending}
          onSubmit={async (values) => {
            await updateMutation.mutateAsync(values);
          }}
        />
      </Card>
    );
  }

  return (
    <>
      {contextHolder}
      <PageContainer title="编辑书籍">{content}</PageContainer>
    </>
  );
};

export default BookEdit;
