import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { history } from '@umijs/max';
import {
  Alert,
  Button,
  Card,
  Descriptions,
  Empty,
  Input,
  Modal,
  message,
  Radio,
  Select,
  Skeleton,
  Space,
  Tag,
  Typography,
} from 'antd';
import { useEffect, useMemo, useState } from 'react';
import {
  type BookChapter,
  type CanonEntry,
  type ChapterRevision,
  getCanon,
  getChapter,
  getChapterImpact,
  getChapterRevisions,
  getFindings,
  type SearchCanonHit,
  updateChapter,
} from '@/services/novel';
import {
  canonAuthorityMap,
  canonStatusMap,
  chapterStatusMap,
  checkerMap,
  findingStatusMap,
  severityMap,
} from '../vocab';
import { diffLines } from './lineDiff';

const { TextArea } = Input;

/**
 * 中栏 · 正文（§10.3）：只认生成链路一条来源，这里只负责看与改。
 *
 * 三条约束落在这里：
 * ①改正文必带影响面提示——保存成功后立刻读 impact（受影响的后章 + 出处失效的断言）；
 * ②版本历史只随正文变（`revision` 由服务端加），diff 取任意两版；
 * ③断言出处用 `[canon#N]` 编号在装配期是临时的、不落库，所以这里显示的是
 *   「出处标在本章的断言」，点它把依据原句在正文里的位置核对出来。
 */
const CenterPanel: React.FC<{
  bookId: number;
  chapterId: number | null;
  focusCanon: SearchCanonHit | null;
  onSaved: () => void;
}> = ({ bookId, chapterId, focusCanon, onSaved }) => {
  const [messageApi, contextHolder] = message.useMessage();
  const queryClient = useQueryClient();
  const [draft, setDraft] = useState('');
  const [title, setTitle] = useState('');
  const [impactChapterId, setImpactChapterId] = useState<number | null>(null);
  const [diffOpen, setDiffOpen] = useState(false);
  const [diffPair, setDiffPair] = useState<[number, number] | null>(null);

  const { data: chapterRes, isLoading } = useQuery({
    queryKey: ['novel-chapter', bookId, chapterId],
    queryFn: () => getChapter(bookId, chapterId as number),
    enabled: chapterId != null,
  });
  const chapter: BookChapter | undefined = chapterRes?.data;

  useEffect(() => {
    setDraft(chapter?.content ?? '');
    setTitle(chapter?.title ?? '');
  }, [chapter?.id, chapter?.content, chapter?.title]);

  const { data: canonRes } = useQuery({
    queryKey: ['novel-canon', bookId, 'source'],
    queryFn: () => getCanon(bookId, { page: 1, size: 200 }),
  });
  const chapterAssertions = useMemo(() => {
    const rows = canonRes?.data?.content ?? [];
    const fromChapter = rows.filter(
      (item: CanonEntry) => item.sourceChapterId === chapterId,
    );
    if (!focusCanon) return fromChapter;
    const picked = rows.find((item) => item.id === focusCanon.canonId);
    const merged =
      picked && !fromChapter.some((item) => item.id === picked.id)
        ? [picked, ...fromChapter]
        : fromChapter;
    return merged;
  }, [canonRes, chapterId, focusCanon]);

  const { data: findingsRes } = useQuery({
    queryKey: ['novel-findings', bookId],
    queryFn: () => getFindings({ bookId, page: 1, size: 200 }),
  });
  const chapterFindings = useMemo(
    () =>
      (findingsRes?.data?.content ?? []).filter(
        (f) => f.chapterId === chapterId,
      ),
    [findingsRes, chapterId],
  );

  const { data: impactRes } = useQuery({
    queryKey: ['novel-impact', bookId, impactChapterId],
    queryFn: () => getChapterImpact(bookId, impactChapterId as number),
    enabled: impactChapterId != null,
  });

  const { data: revisionsRes, isFetching: revisionsLoading } = useQuery({
    queryKey: ['novel-revisions', bookId, chapterId],
    queryFn: () => getChapterRevisions(bookId, chapterId as number),
    enabled: diffOpen && chapterId != null,
  });
  const revisions: ChapterRevision[] = revisionsRes?.data ?? [];

  const saveMutation = useMutation({
    mutationFn: () =>
      updateChapter(bookId, chapterId as number, {
        title: title.trim() || (chapter?.title ?? ''),
        chapterIndex: chapter?.chapterIndex,
        content: draft,
      }),
    onSuccess: (res) => {
      messageApi.success('正文已保存');
      queryClient.invalidateQueries({
        queryKey: ['novel-chapter', bookId, chapterId],
      });
      queryClient.invalidateQueries({ queryKey: ['book-chapters', bookId] });
      queryClient.invalidateQueries({
        queryKey: ['novel-revisions', bookId, chapterId],
      });
      queryClient.invalidateQueries({
        queryKey: ['novel-canon', bookId, 'source'],
      });
      queryClient.invalidateQueries({ queryKey: ['novel-findings', bookId] });
      if (res.data?.id) setImpactChapterId(res.data.id);
      onSaved();
    },
    onError: (err: Error) => messageApi.error(err.message || '保存失败'),
  });

  const dirty =
    chapter != null &&
    (draft !== (chapter.content ?? '') || title !== chapter.title);
  const words = draft.replace(/\s/g, '').length;
  const diffResult = useMemo(() => {
    if (!diffPair) return null;
    const byRev = new Map(revisions.map((r) => [r.revision, r]));
    const before = byRev.get(diffPair[0])?.content ?? '';
    const after = byRev.get(diffPair[1])?.content ?? '';
    return diffLines(before, after);
  }, [diffPair, revisions]);

  let body: React.ReactNode;
  if (chapterId == null) {
    body = (
      <Card>
        <Empty
          description="从左侧章节树选一章开始"
          image={Empty.PRESENTED_IMAGE_SIMPLE}
        />
      </Card>
    );
  } else if (isLoading) {
    body = (
      <Card>
        <Skeleton active paragraph={{ rows: 10 }} />
      </Card>
    );
  } else if (!chapter) {
    body = (
      <Card>
        <Empty
          description="章节读取失败"
          image={Empty.PRESENTED_IMAGE_SIMPLE}
        />
      </Card>
    );
  } else {
    const status = chapterStatusMap[chapter.status] ?? {
      label: chapter.status,
      color: 'default',
    };
    body = (
      <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
        <Card
          size="small"
          title={
            <Space size={6}>
              <span>第 {chapter.chapterIndex} 章</span>
              <Tag color={status.color}>{status.label}</Tag>
              <Tag>r{chapter.revision}</Tag>
            </Space>
          }
          extra={
            <Space size={8}>
              <Button size="small" onClick={() => setDiffOpen(true)}>
                版本对比
              </Button>
              <Button
                size="small"
                type="primary"
                disabled={!dirty}
                loading={saveMutation.isPending}
                onClick={() => saveMutation.mutate()}
              >
                保存
              </Button>
            </Space>
          }
        >
          <Input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="章节标题"
            style={{ marginBottom: 8 }}
          />
          <TextArea
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            autoSize={{ minRows: 18, maxRows: 30 }}
            placeholder="本章正文"
          />
          <div style={{ marginTop: 8, display: 'flex', gap: 16 }}>
            <Typography.Text type="secondary">当前 {words} 字</Typography.Text>
            <Typography.Text type="secondary">
              库内 {chapter.wordCount.toLocaleString()} 字
            </Typography.Text>
          </div>
          {dirty && (
            <Alert
              style={{ marginTop: 8 }}
              type="info"
              showIcon
              message="改动已定稿章节会退回「待复核」，并重算所有出处落在本章的设定条目。"
            />
          )}
        </Card>

        <Card size="small" title="闸门状态">
          {chapterFindings.length === 0 ? (
            <Typography.Text type="secondary">
              本章台账暂无冲突记录（当前状态：{' '}
              <Tag color={status.color}>{status.label}</Tag>）
            </Typography.Text>
          ) : (
            <Space direction="vertical" size={4} style={{ width: '100%' }}>
              {chapterFindings.map((f) => (
                <div key={f.id}>
                  <Tag color={severityMap[f.severity]?.color ?? 'default'}>
                    {severityMap[f.severity]?.label ?? f.severity}
                  </Tag>
                  <Typography.Text code>{f.code}</Typography.Text>{' '}
                  <Typography.Text type="secondary" style={{ fontSize: 12 }}>
                    {checkerMap[f.checker]?.label ?? f.checker} ·{' '}
                    {findingStatusMap[f.status]?.label ?? f.status} ·{' '}
                    {f.explanation ?? f.evidenceQuote ?? ''}
                  </Typography.Text>
                </div>
              ))}
              <Typography.Link
                style={{ fontSize: 12 }}
                onClick={() => history.push(`/novel/review?bookId=${bookId}`)}
              >
                去冲突台账裁定
              </Typography.Link>
            </Space>
          )}
        </Card>

        <Card size="small" title="出处标在本章的设定">
          {chapterAssertions.length === 0 ? (
            <Typography.Text type="secondary">
              没有设定条目把出处落在本章——新设定要经生成链路的抽取或右栏提议卡采纳后才会出现。
            </Typography.Text>
          ) : (
            <Space direction="vertical" size={6} style={{ width: '100%' }}>
              {chapterAssertions.map((item) => {
                const quote = item.evidenceQuote ?? '';
                const located = quote.length > 0 && draft.includes(quote);
                return (
                  <div key={item.id}>
                    <Typography.Text code>#{item.id}</Typography.Text>{' '}
                    <Typography.Text strong>{item.subjectKey}</Typography.Text>{' '}
                    · {item.predicate} · {item.objectText}
                    <Typography.Text type="secondary" style={{ fontSize: 12 }}>
                      {' '}
                      （
                      {canonAuthorityMap[item.authority]?.label ??
                        item.authority}{' '}
                      · {canonStatusMap[item.status]?.label ?? item.status}，第{' '}
                      {item.validFromChapter}
                      {item.validUntilChapter
                        ? `~${item.validUntilChapter}`
                        : ' 章起'}
                      ）
                    </Typography.Text>
                    {quote && (
                      <Typography.Paragraph
                        type={located ? 'secondary' : 'danger'}
                        style={{ fontSize: 12, marginBottom: 0 }}
                      >
                        依据「{quote}」
                        {located
                          ? '在当前正文里'
                          : '已不在当前正文里（保存后会进台账）'}
                      </Typography.Paragraph>
                    )}
                  </div>
                );
              })}
            </Space>
          )}
        </Card>

        {impactRes?.data && (
          <Card
            size="small"
            title="这次改动波及谁"
            extra={
              <Button
                size="small"
                type="text"
                onClick={() => setImpactChapterId(null)}
              >
                收起
              </Button>
            }
          >
            <Descriptions column={1} size="small">
              <Descriptions.Item label="受影响的后章">
                {impactRes.data.affectedChapters.length === 0
                  ? '无'
                  : impactRes.data.affectedChapters
                      .map((c) => `第 ${c.chapterIndex} 章 ${c.title ?? ''}`)
                      .join('、')}
              </Descriptions.Item>
              <Descriptions.Item label="出处失效的设定条目">
                {impactRes.data.orphanedAssertions.length === 0
                  ? '无'
                  : impactRes.data.orphanedAssertions
                      .map(
                        (a) => `#${a.canonId} ${a.subjectKey}·${a.predicate}`,
                      )
                      .join('、')}
              </Descriptions.Item>
              <Descriptions.Item label="新增台账行">
                {impactRes.data.orphanedFindings}
              </Descriptions.Item>
              <Descriptions.Item label="当前状态">
                {chapterStatusMap[impactRes.data.status]?.label ??
                  impactRes.data.status}
                （r
                {impactRes.data.revision}）
              </Descriptions.Item>
            </Descriptions>
          </Card>
        )}
      </div>
    );
  }

  return (
    <>
      {contextHolder}
      <div style={{ height: '100%', overflow: 'auto' }}>{body}</div>
      <Modal
        title="版本对比"
        open={diffOpen}
        footer={null}
        width={860}
        onCancel={() => setDiffOpen(false)}
      >
        {revisionsLoading && revisions.length === 0 ? (
          <Skeleton active paragraph={{ rows: 6 }} />
        ) : revisions.length < 2 ? (
          <Empty
            description="这一章只有一个版本"
            image={Empty.PRESENTED_IMAGE_SIMPLE}
          />
        ) : (
          <>
            <Space style={{ marginBottom: 12 }} wrap>
              <Select
                style={{ width: 220 }}
                placeholder="对比基准"
                value={diffPair?.[0]}
                options={revisions.map((r) => ({
                  label: `r${r.revision}${r.current ? '' : '（历史）'}`,
                  value: r.revision,
                }))}
                onChange={(value) =>
                  setDiffPair([value, diffPair?.[1] ?? revisions[0].revision])
                }
              />
              <Radio.Group
                optionType="button"
                value={diffPair?.[1]}
                options={revisions.map((r) => ({
                  label: `r${r.revision}${r.current ? '（当前）' : ''}`,
                  value: r.revision,
                }))}
                onChange={(e) =>
                  setDiffPair([
                    diffPair?.[0] ?? revisions[revisions.length - 1].revision,
                    e.target.value,
                  ])
                }
              />
            </Space>
            <div
              style={{
                maxHeight: 420,
                overflow: 'auto',
                fontFamily: 'monospace',
                fontSize: 12,
              }}
            >
              {diffResult?.map((line) => (
                <div
                  key={line.key}
                  style={{
                    background:
                      line.kind === 'add'
                        ? '#f6ffed'
                        : line.kind === 'del'
                          ? '#fff1f0'
                          : undefined,
                    whiteSpace: 'pre-wrap',
                  }}
                >
                  {line.kind === 'same'
                    ? ' '
                    : line.kind === 'add'
                      ? '+ '
                      : '- '}
                  {line.text || ' '}
                </div>
              ))}
            </div>
          </>
        )}
      </Modal>
    </>
  );
};

export default CenterPanel;
