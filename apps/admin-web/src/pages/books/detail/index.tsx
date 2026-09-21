import { ArrowLeftOutlined, EditOutlined } from '@ant-design/icons';
import { PageContainer } from '@ant-design/pro-components';
import { useQuery } from '@tanstack/react-query';
import { history, useParams } from '@umijs/max';
import {
  Button,
  Card,
  Descriptions,
  Empty,
  Image,
  Result,
  Skeleton,
  Tag,
  Typography,
} from 'antd';
import dayjs from 'dayjs';
import { getBook, getBookGenres } from '@/services/book';
import { statusColorMap, statusOptions } from '../components/BookForm';
import ChapterManager from '../components/ChapterManager';
import CharacterManager from '../components/CharacterManager';

const formatDateTime = (value?: string) =>
  value ? dayjs(value).format('YYYY-MM-DD HH:mm:ss') : '-';

const BookDetail: React.FC = () => {
  const params = useParams<{ id: string }>();
  const id = Number(params.id);
  const validId = Number.isFinite(id) && id > 0;

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ['book', id],
    queryFn: () => getBook(id),
    enabled: validId,
  });

  const { data: genresRes } = useQuery({
    queryKey: ['book-genres'],
    queryFn: getBookGenres,
    staleTime: 5 * 60 * 1000,
  });
  const genreLabelMap: Record<string, string> = {};
  genresRes?.data?.forEach((g) => {
    genreLabelMap[g.value] = g.label;
  });

  const book = data?.data;
  const statusText = book
    ? (statusOptions.find((s) => s.value === book.status)?.label ?? book.status)
    : '';

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
  } else if (isError || !book) {
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
      <>
        <Card title="基本信息" style={{ marginBottom: 16 }}>
          <div style={{ display: 'flex', gap: 24, flexWrap: 'wrap' }}>
            <div style={{ flex: '0 0 200px' }}>
              {book.coverImage ? (
                <Image
                  src={book.coverImage}
                  alt={book.title}
                  style={{ width: 200, borderRadius: 8, objectFit: 'cover' }}
                />
              ) : (
                <Empty
                  description="暂无封面"
                  style={{
                    width: 200,
                    height: 260,
                    border: '1px dashed #d9d9d9',
                    borderRadius: 8,
                  }}
                />
              )}
            </div>
            <div style={{ flex: 1, minWidth: 320 }}>
              {book.description && (
                <Typography.Paragraph
                  type="secondary"
                  style={{ marginBottom: 16 }}
                >
                  {book.description}
                </Typography.Paragraph>
              )}
              <Descriptions column={2} size="small">
                <Descriptions.Item label="类型">
                  {book.genre ? (
                    <Tag color="purple">
                      {genreLabelMap[book.genre] ?? book.genre}
                    </Tag>
                  ) : (
                    '-'
                  )}
                </Descriptions.Item>
                <Descriptions.Item label="创作状态">
                  <Tag color={statusColorMap[book.status] ?? 'default'}>
                    {statusText}
                  </Tag>
                </Descriptions.Item>
                <Descriptions.Item label="作者">
                  {book.author ?? '-'}
                </Descriptions.Item>
                <Descriptions.Item label="总字数">
                  {book.wordCount.toLocaleString()}
                </Descriptions.Item>
                <Descriptions.Item label="创建时间">
                  {formatDateTime(book.createdAt)}
                </Descriptions.Item>
                <Descriptions.Item label="更新时间">
                  {formatDateTime(book.updatedAt)}
                </Descriptions.Item>
              </Descriptions>
            </div>
          </div>
        </Card>

        <ChapterManager bookId={book.id} />

        <CharacterManager bookId={book.id} />
      </>
    );
  }

  return (
    <PageContainer
      title={book?.title ?? '书籍详情'}
      extra={[
        <Button
          key="back"
          icon={<ArrowLeftOutlined />}
          onClick={() => history.push('/books/list')}
        >
          返回列表
        </Button>,
        <Button
          key="edit"
          type="primary"
          icon={<EditOutlined />}
          disabled={!book}
          onClick={() => history.push(`/books/edit/${id}`)}
        >
          编辑
        </Button>,
      ]}
    >
      {content}
    </PageContainer>
  );
};

export default BookDetail;
