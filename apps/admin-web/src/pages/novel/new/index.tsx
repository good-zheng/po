import { PageContainer } from '@ant-design/pro-components';
import { useMutation } from '@tanstack/react-query';
import { history } from '@umijs/max';
import { Card, message } from 'antd';
import { useMemo } from 'react';
import { type BookRequest, createBook } from '@/services/novel';
import BookForm, { buildBookInitialValues } from '../components/BookForm';

const BookCreate: React.FC = () => {
  const [messageApi, contextHolder] = message.useMessage();

  const createMutation = useMutation({
    mutationFn: (data: BookRequest) => createBook(data),
    onSuccess: (res) => {
      messageApi.success('作品创建成功');
      history.push(`/novel/book/${res.data.id}`);
    },
    onError: (err: Error) => {
      messageApi.error(err.message || '创建失败');
    },
  });

  const initialValues = useMemo(() => buildBookInitialValues(), []);

  return (
    <>
      {contextHolder}
      <PageContainer title="新建作品">
        <Card>
          <BookForm
            initialValues={initialValues}
            submitting={createMutation.isPending}
            onSubmit={async (values) => {
              await createMutation.mutateAsync(values);
            }}
          />
        </Card>
      </PageContainer>
    </>
  );
};

export default BookCreate;
