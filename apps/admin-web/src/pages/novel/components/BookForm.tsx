import {
  ProForm,
  ProFormSelect,
  ProFormText,
  ProFormTextArea,
} from '@ant-design/pro-components';
import { useQuery } from '@tanstack/react-query';
import { Button, Divider, Form, Space } from 'antd';
import { useMemo } from 'react';
import { type Book, type BookRequest, getBookGenres } from '@/services/novel';
import { bookStatusMap, toOptions } from '../vocab';

type BookFormProps = {
  initialValues: Partial<BookRequest>;
  submitting: boolean;
  onSubmit: (values: BookRequest) => Promise<void>;
};

export function buildBookInitialValues(book?: Book): Partial<BookRequest> {
  if (!book) {
    return { status: 'ongoing' };
  }
  return {
    title: book.title,
    description: book.description ?? '',
    coverImage: book.coverImage ?? '',
    genre: book.genre ?? undefined,
    author: book.author ?? '',
    status: book.status,
  };
}

const BookForm: React.FC<BookFormProps> = ({
  initialValues,
  submitting,
  onSubmit,
}) => {
  const [form] = Form.useForm<BookRequest>();

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

  return (
    <ProForm<BookRequest>
      form={form}
      layout="vertical"
      initialValues={initialValues}
      submitter={false}
      onFinish={async (values) => {
        await onSubmit(values);
        return true;
      }}
    >
      <Divider plain titlePlacement="left">
        基本信息
      </Divider>
      <ProFormText
        name="title"
        label="书名"
        placeholder="请输入书名"
        rules={[{ required: true, message: '请输入书名' }]}
      />
      <div style={{ display: 'flex', gap: 16 }}>
        <ProFormSelect
          name="genre"
          label="类型"
          placeholder="请选择类型"
          options={genreOptions}
          style={{ flex: 1 }}
          allowClear
        />
        <ProFormSelect
          name="status"
          label="创作状态"
          options={toOptions(bookStatusMap)}
          rules={[{ required: true, message: '请选择创作状态' }]}
          style={{ flex: 1 }}
        />
      </div>
      <ProFormText name="author" label="作者" placeholder="请输入作者名" />
      <ProFormTextArea
        name="description"
        label="简介"
        placeholder="请输入作品简介"
        fieldProps={{ rows: 4 }}
      />
      <ProFormText
        name="coverImage"
        label="封面图 URL"
        placeholder="图片链接"
      />

      <Form.Item style={{ marginTop: 24, marginBottom: 0 }}>
        <Space style={{ display: 'flex', justifyContent: 'flex-end' }}>
          <Button onClick={() => window.history.back()}>取消</Button>
          <Button
            type="primary"
            loading={submitting}
            onClick={() => form.submit()}
          >
            保存
          </Button>
        </Space>
      </Form.Item>
    </ProForm>
  );
};

export default BookForm;
