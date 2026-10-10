import {
  ArrowLeftOutlined,
  BookOutlined,
  RobotOutlined,
  SkinOutlined,
} from '@ant-design/icons';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { history, useParams } from '@umijs/max';
import {
  Button,
  Drawer,
  Empty,
  Result,
  Skeleton,
  Space,
  Typography,
} from 'antd';
import { useEffect, useMemo, useState } from 'react';
import { getBook, getChapters, type SearchCanonHit } from '@/services/novel';
import CenterPanel from './CenterPanel';
import LeftPanel from './LeftPanel';
import RightPanel from './RightPanel';
import RunPanel from './RunPanel';
import StylePanel from './StylePanel';

/**
 * 三栏创作工作台（§10.3、D7/D8）。
 *
 * 三块的能力边界刻意不同：左＝查与选（不改正文），中＝看与改正文，
 * 右＝只谈不写（读正典、出提议卡）。`layout: false` 让这一屏跳出 ProLayout 的
 * mix 菜单，否则三栏会被菜单挤掉。
 *
 * 顶栏两个抽屉是第四个面：文风契约（只读整本书的文体约束）与 AI 生成（`agent: 'novel'`
 * 的长链路入口）。生成不落在三栏里，是因为它写的是**新书**且会连着跑几分钟——
 * 塞进任何一栏都会破坏那一栏「不触发生成」的边界（§10.5 约定 ①）。
 */
const NovelStudio: React.FC = () => {
  const params = useParams<{ bookId: string }>();
  const bookId = Number(params.bookId);
  const validId = Number.isFinite(bookId) && bookId > 0;

  const [selectedChapterId, setSelectedChapterId] = useState<number | null>(
    null,
  );
  const [referenceChapterId, setReferenceChapterId] = useState<number | null>(
    null,
  );
  const [focusCanon, setFocusCanon] = useState<SearchCanonHit | null>(null);
  const [styleOpen, setStyleOpen] = useState(false);
  const [runOpen, setRunOpen] = useState(false);
  const queryClient = useQueryClient();

  const {
    data: bookRes,
    isLoading: bookLoading,
    isError: bookError,
    error,
  } = useQuery({
    queryKey: ['book', bookId],
    queryFn: () => getBook(bookId),
    enabled: validId,
  });
  const book = bookRes?.data;

  const { data: chaptersRes } = useQuery({
    queryKey: ['book-chapters', bookId],
    queryFn: () => getChapters(bookId),
    enabled: validId,
  });
  const chapters = useMemo(
    () =>
      [...(chaptersRes?.data ?? [])].sort(
        (a, b) => a.chapterIndex - b.chapterIndex,
      ),
    [chaptersRes],
  );

  useEffect(() => {
    if (selectedChapterId == null && chapters.length > 0) {
      setSelectedChapterId(chapters[0].id);
    }
  }, [chapters, selectedChapterId]);

  const reference =
    chapters.find((item) => item.id === referenceChapterId) ?? null;

  if (!validId) {
    return (
      <div style={{ padding: 24 }}>
        <Empty description="无效的书籍 ID" />
      </div>
    );
  }
  if (bookLoading) {
    return (
      <div style={{ padding: 24 }}>
        <Skeleton active paragraph={{ rows: 10 }} />
      </div>
    );
  }
  if (bookError || !book) {
    return (
      <Result
        status="404"
        title="加载失败"
        subTitle={
          error instanceof Error ? error.message : '书籍不存在或已被删除'
        }
        extra={<a onClick={() => history.push('/novel/list')}>返回书籍列表</a>}
      />
    );
  }

  return (
    <div
      style={{
        height: '100vh',
        display: 'flex',
        flexDirection: 'column',
        background: '#f5f5f5',
      }}
    >
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 12,
          padding: '8px 16px',
          background: '#fff',
          borderBottom: '1px solid #f0f0f0',
        }}
      >
        <Typography.Text strong style={{ fontSize: 16 }}>
          {book.title}
        </Typography.Text>
        <Typography.Text type="secondary">创作工作台</Typography.Text>
        <Space style={{ marginLeft: 'auto' }}>
          <Button
            icon={<ArrowLeftOutlined />}
            size="small"
            onClick={() => history.push('/novel/list')}
          >
            返回列表
          </Button>
          <Button
            icon={<BookOutlined />}
            size="small"
            onClick={() => history.push(`/novel/book/${bookId}`)}
          >
            书籍详情
          </Button>
          <Button
            icon={<SkinOutlined />}
            size="small"
            onClick={() => setStyleOpen(true)}
          >
            文风契约
          </Button>
          <Button
            icon={<RobotOutlined />}
            size="small"
            type="primary"
            onClick={() => setRunOpen(true)}
          >
            AI 生成
          </Button>
        </Space>
      </div>

      <div
        style={{ flex: 1, display: 'flex', gap: 12, padding: 12, minHeight: 0 }}
      >
        <div style={{ flex: '0 0 340px', minWidth: 0, minHeight: 0 }}>
          <LeftPanel
            bookId={bookId}
            chapters={chapters}
            selectedChapterId={selectedChapterId}
            referenceChapterId={referenceChapterId}
            onSelectChapter={(chapterId) => {
              setSelectedChapterId(chapterId);
              setFocusCanon(null);
            }}
            onSetReference={setReferenceChapterId}
            onPickCanon={(hit) => {
              setFocusCanon(hit);
              if (selectedChapterId == null && chapters.length > 0) {
                setSelectedChapterId(chapters[0].id);
              }
            }}
          />
        </div>
        <div style={{ flex: '1 1 auto', minWidth: 0, minHeight: 0 }}>
          <CenterPanel
            bookId={bookId}
            chapterId={selectedChapterId}
            focusCanon={focusCanon}
            onSaved={() => {
              // 章列表与台账都在服务端被连带改过（版本号、状态、出处重定位）
              setFocusCanon(null);
            }}
          />
        </div>
        <div style={{ flex: '0 0 420px', minWidth: 0, minHeight: 0 }}>
          <RightPanel
            bookId={bookId}
            referenceChapterId={referenceChapterId}
            referenceChapterIndex={reference?.chapterIndex ?? null}
          />
        </div>
      </div>

      <StylePanel
        bookId={bookId}
        open={styleOpen}
        onClose={() => setStyleOpen(false)}
      />

      <Drawer
        title="AI 生成：一句话想法 → 一整本新书"
        size={720}
        open={runOpen}
        onClose={() => setRunOpen(false)}
        destroyOnHidden
      >
        <RunPanel
          onArchived={() => {
            // 归档写的是**另一本书**（save_book 新建书目），所以该刷新的是书架而非当前书。
            // 书籍列表页是 ProTable 自带 request（挂载时自取），这里只需让 react-query
            // 侧唯一的书架缓存（选题用的 books-all）失效。
            queryClient.invalidateQueries({ queryKey: ['books-all'] });
          }}
        />
      </Drawer>
    </div>
  );
};

export default NovelStudio;
