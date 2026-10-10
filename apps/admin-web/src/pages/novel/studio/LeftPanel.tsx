import { useQuery } from '@tanstack/react-query';
import {
  Alert,
  Button,
  Card,
  Checkbox,
  Empty,
  Input,
  Space,
  Tag,
  Tree,
  Typography,
} from 'antd';
import { useState } from 'react';
import {
  type BookChapter,
  type SearchCanonHit,
  type SearchScope,
  searchNovel,
} from '@/services/novel';
import { chapterStatusMap } from '../vocab';

const SCOPES: { value: SearchScope; label: string }[] = [
  { value: 'chapter', label: '章节' },
  { value: 'canon', label: '设定' },
  { value: 'alias', label: '称谓' },
];

/**
 * 左栏 · 资料与章节（§10.3）：章树 + 统一检索 + 参照章选择。
 *
 * 参照章决定右栏对话的 as-of 支点，也决定提议卡的生效起点，所以它是「选」出来的、
 * 不是「正在编辑的那一章」——两者刻意分开，避免作者翻到第 8 章改稿时，
 * 讨论上下文悄悄跳到第 8 章之后的视野里。
 */
const LeftPanel: React.FC<{
  bookId: number;
  chapters: BookChapter[];
  selectedChapterId: number | null;
  referenceChapterId: number | null;
  onSelectChapter: (chapterId: number) => void;
  onSetReference: (chapterId: number | null) => void;
  onPickCanon: (hit: SearchCanonHit) => void;
}> = ({
  bookId,
  chapters,
  selectedChapterId,
  referenceChapterId,
  onSelectChapter,
  onSetReference,
  onPickCanon,
}) => {
  const [keyword, setKeyword] = useState('');
  const [query, setQuery] = useState('');
  const [scopes, setScopes] = useState<SearchScope[]>([
    'chapter',
    'canon',
    'alias',
  ]);

  const { data: searchRes, isFetching: searching } = useQuery({
    queryKey: ['novel-search', bookId, query, scopes.join(',')],
    queryFn: () => searchNovel(bookId, { q: query, scope: scopes, size: 8 }),
    enabled: query.trim().length > 0,
  });
  const results = searchRes?.data;

  const reference = chapters.find(
    (item: BookChapter) => item.id === referenceChapterId,
  );

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: 12,
        height: '100%',
        overflow: 'auto',
      }}
    >
      <Card size="small" title="当前参照章">
        {reference ? (
          <Space direction="vertical" size={4} style={{ width: '100%' }}>
            <Typography.Text>
              第 {reference.chapterIndex} 章 · {reference.title}
            </Typography.Text>
            <Typography.Text type="secondary" style={{ fontSize: 12 }}>
              对话与提议卡都按「截至第 {reference.chapterIndex} 章」取设定
            </Typography.Text>
            <Button size="small" onClick={() => onSetReference(null)}>
              取消参照
            </Button>
          </Space>
        ) : (
          <Typography.Text type="secondary">
            未选参照章：对话按已归档章数取设定。在下方章树里点「设为参照」可精确到某一章。
          </Typography.Text>
        )}
      </Card>

      <Card size="small" title="章节" style={{ flex: '0 0 auto' }}>
        {chapters.length === 0 ? (
          <Empty
            description="这本书还没有章节"
            image={Empty.PRESENTED_IMAGE_SIMPLE}
          />
        ) : (
          <Tree
            blockNode
            selectedKeys={selectedChapterId ? [selectedChapterId] : []}
            onSelect={(keys) => {
              const key = keys[0];
              if (typeof key === 'number') onSelectChapter(key);
            }}
            treeData={chapters.map((item) => ({
              key: item.id,
              title: (
                <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                  <Typography.Text ellipsis style={{ maxWidth: 150 }}>
                    第 {item.chapterIndex} 章 {item.title}
                  </Typography.Text>
                  <Tag
                    color={chapterStatusMap[item.status]?.color ?? 'default'}
                  >
                    {chapterStatusMap[item.status]?.label ?? item.status}
                  </Tag>
                  <Typography.Link
                    style={{ marginLeft: 'auto', fontSize: 12 }}
                    onClick={(e) => {
                      e.stopPropagation();
                      onSetReference(
                        referenceChapterId === item.id ? null : item.id,
                      );
                    }}
                  >
                    {referenceChapterId === item.id ? '取消参照' : '设为参照'}
                  </Typography.Link>
                </div>
              ),
            }))}
          />
        )}
      </Card>

      <Card size="small" title="统一检索" style={{ flex: 1 }}>
        <Input.Search
          placeholder="章题 / 正文 / 设定条目 / 人名别名"
          allowClear
          enterButton="搜索"
          value={keyword}
          onChange={(e) => setKeyword(e.target.value)}
          onSearch={(value) => setQuery(value.trim())}
        />
        <Checkbox.Group
          style={{ marginTop: 8, display: 'flex', gap: 8 }}
          value={scopes}
          options={SCOPES.map((s) => ({ label: s.label, value: s.value }))}
          onChange={(vals) => setScopes(vals as SearchScope[])}
        />
        {query && !results && !searching ? (
          <Alert style={{ marginTop: 12 }} type="info" message="没有检索结果" />
        ) : null}
        {results ? (
          <div style={{ marginTop: 12 }}>
            {results.expandedEntityKeys.length > 0 && (
              <Typography.Paragraph type="secondary" style={{ fontSize: 12 }}>
                称谓展开到实体：{results.expandedEntityKeys.join('、')}
              </Typography.Paragraph>
            )}
            {results.chapters.length > 0 && (
              <>
                <Typography.Text strong>
                  章节（{results.chapterTotal}）
                </Typography.Text>
                {results.chapters.map((hit) => (
                  <div key={hit.chapterId} style={{ marginBottom: 8 }}>
                    <Typography.Link
                      onClick={() => onSelectChapter(hit.chapterId)}
                    >
                      第 {hit.chapterIndex ?? '-'} 章 {hit.title}
                    </Typography.Link>
                    <Typography.Paragraph
                      type="secondary"
                      style={{ fontSize: 12, marginBottom: 0 }}
                    >
                      {hit.excerpt}
                    </Typography.Paragraph>
                  </div>
                ))}
              </>
            )}
            {results.canon.length > 0 && (
              <>
                <Typography.Text strong>
                  设定（{results.canonTotal}）
                </Typography.Text>
                {results.canon.map((hit) => (
                  <div key={hit.canonId} style={{ marginBottom: 8 }}>
                    <Typography.Link onClick={() => onPickCanon(hit)}>
                      <Typography.Text code>#{hit.canonId}</Typography.Text>{' '}
                      {hit.subjectKey} · {hit.predicate} · {hit.objectText}
                    </Typography.Link>
                    <Typography.Text type="secondary" style={{ fontSize: 12 }}>
                      {' '}
                      第 {hit.validFromChapter ?? '-'}
                      {hit.validUntilChapter ? `~${hit.validUntilChapter}` : ''}{' '}
                      章 {hit.matchedViaAlias ? '（经称谓命中）' : ''}
                    </Typography.Text>
                  </div>
                ))}
              </>
            )}
            {results.aliases.length > 0 && (
              <>
                <Typography.Text strong>
                  称谓（{results.aliasTotal}）
                </Typography.Text>
                {results.aliases.map((hit) => (
                  <div key={hit.aliasId} style={{ marginBottom: 4 }}>
                    <Typography.Text>
                      「{hit.aliasText}」→ {hit.entityKey}
                    </Typography.Text>
                    <Typography.Text type="secondary" style={{ fontSize: 12 }}>
                      {' '}
                      首现第 {hit.firstSeenChapter ?? '-'} 章
                    </Typography.Text>
                  </div>
                ))}
              </>
            )}
          </div>
        ) : null}
      </Card>
    </div>
  );
};

export default LeftPanel;
