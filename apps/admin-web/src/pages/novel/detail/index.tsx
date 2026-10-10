import {
  ArrowLeftOutlined,
  EditOutlined,
  ReadOutlined,
} from '@ant-design/icons';
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
  Tabs,
  Tag,
  Typography,
} from 'antd';
import dayjs from 'dayjs';
import { getBook, getBookGenres } from '@/services/novel';
import AliasPanel from '../components/AliasPanel';
import CanonPanel from '../components/CanonPanel';
import ChapterManager from '../components/ChapterManager';
import CharacterManager from '../components/CharacterManager';
import FindingTable from '../components/FindingTable';
import ForeshadowPanel from '../components/ForeshadowPanel';
import ProgressPanel from '../components/ProgressPanel';
import { bookStatusMap } from '../vocab';

const formatDateTime = (value?: string) =>
  value ? dayjs(value).format('YYYY-MM-DD HH:mm:ss') : '-';

const BookDetail: React.FC = () => {
  const params = useParams<{ bookId: string }>();
  const id = Number(params.bookId);
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
  const statusEntry = book ? bookStatusMap[book.status] : undefined;

  let content: React.ReactNode;
  if (!validId) {
    content = (
      <Card>
        <Empty description="无效的作品 ID" />
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
          error instanceof Error ? error.message : '作品不存在或已被删除'
        }
        extra={<a onClick={() => history.push('/novel/list')}>返回作品列表</a>}
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
                <Descriptions.Item label="状态">
                  <Tag color={statusEntry?.color ?? 'default'}>
                    {statusEntry?.label ?? book.status}
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

        <Tabs
          items={[
            {
              key: 'progress',
              label: '进度',
              children: <ProgressPanel bookId={book.id} />,
            },
            {
              key: 'canon',
              label: '设定',
              children: (
                <Card style={{ marginBottom: 16 }}>
                  <CanonPanel bookId={book.id} />
                </Card>
              ),
            },
            {
              key: 'findings',
              label: '冲突',
              children: (
                <Card style={{ marginBottom: 16 }}>
                  <FindingTable bookId={book.id} />
                </Card>
              ),
            },
            {
              key: 'aliases',
              label: '别名',
              children: <AliasPanel bookId={book.id} />,
            },
            {
              key: 'foreshadows',
              label: '伏笔',
              children: <ForeshadowPanel bookId={book.id} />,
            },
            {
              key: 'chapters',
              label: '章节',
              children: <ChapterManager bookId={book.id} />,
            },
            {
              key: 'characters',
              label: '角色',
              children: <CharacterManager bookId={book.id} />,
            },
          ]}
        />
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
          onClick={() => history.push('/novel/list')}
        >
          返回列表
        </Button>,
        <Button
          key="edit"
          type="primary"
          icon={<EditOutlined />}
          disabled={!book}
          onClick={() => history.push(`/novel/book/${id}/edit`)}
        >
          编辑
        </Button>,
        <Button
          key="studio"
          icon={<ReadOutlined />}
          disabled={!book}
          onClick={() => history.push(`/novel/book/${id}/studio`)}
        >
          创作工作台
        </Button>,
      ]}
    >
      {content}
    </PageContainer>
  );
};

export default BookDetail;
