import { useQuery, useQueryClient } from '@tanstack/react-query';
import {
  Alert,
  Button,
  Card,
  Input,
  Space,
  Spin,
  Tag,
  Tooltip,
  Typography,
} from 'antd';
import { useEffect, useRef, useState } from 'react';
import { type CanonProposal, getProposals } from '@/services/novel';
import ProposalCard from './ProposalCard';
import { useNovelChat } from './useNovelChat';

const { TextArea } = Input;

/**
 * 右栏 · 对话（§10.3）：读正典与已定稿章节，只出提议卡。
 *
 * 这一栏没有任何写正典的入口：卡要经作者点头才成为 `canon_entry(authority=author)`，
 * 正文与生成触发都不在这里（前者在中栏，后者在顶栏「AI 生成」抽屉，且它产出的是新书）。
 * 未采纳的卡也不参与注入——它只活在 `canon_proposal` 与这段会话里。
 */
const RightPanel: React.FC<{
  bookId: number;
  /** 参照章的库 id：作为 `context.chapterId` 发给服务端（决定 as-of） */
  referenceChapterId: number | null;
  referenceChapterIndex: number | null;
}> = ({ bookId, referenceChapterId, referenceChapterIndex }) => {
  const [input, setInput] = useState('');
  const { turns, requesting, connected, errorText, send } = useNovelChat(
    bookId,
    referenceChapterId,
  );
  const bottomRef = useRef<HTMLDivElement | null>(null);
  const queryClient = useQueryClient();

  const { data: pendingRes } = useQuery({
    queryKey: ['novel-proposals', bookId, 'pending'],
    queryFn: () =>
      getProposals({ bookId, status: 'pending', page: 1, size: 20 }),
  });
  const pending: CanonProposal[] = pendingRes?.data?.content ?? [];

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ block: 'end' });
  }, [turns]);

  const submit = () => {
    const text = input.trim();
    if (!text) return;
    // send 是异步的（要先换握手票据再建连），失败原因已经写进 errorText，这里不接住 Promise
    void send(text);
    setInput('');
  };

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: 12,
        height: '100%',
      }}
    >
      <Card size="small">
        <Space direction="vertical" size={2} style={{ width: '100%' }}>
          <Typography.Text type="secondary" style={{ fontSize: 12 }}>
            {referenceChapterIndex != null
              ? `参照章：第 ${referenceChapterIndex} 章（对话按「截至这一章」取设定）`
              : '未选参照章：按已归档章数取设定'}
          </Typography.Text>
          <Typography.Text type="secondary" style={{ fontSize: 12 }}>
            只谈不写：这里不产出正文、不写设定、不触发生成
          </Typography.Text>
          {!connected && (
            <Tag color={requesting ? 'processing' : 'default'}>
              {requesting ? '连接中' : '未连接（发送时自动连）'}
            </Tag>
          )}
        </Space>
      </Card>

      <div style={{ flex: 1, overflow: 'auto' }}>
        {turns.map((turn) =>
          turn.role === 'user' ? (
            <Card key={turn.id} size="small" style={{ marginBottom: 8 }}>
              <Typography.Text>{turn.content}</Typography.Text>
            </Card>
          ) : (
            <Card
              key={turn.id}
              size="small"
              style={{ marginBottom: 8 }}
              title="AI"
            >
              {turn.content ? (
                <Typography.Paragraph style={{ whiteSpace: 'pre-wrap' }}>
                  {turn.content}
                </Typography.Paragraph>
              ) : requesting ? (
                <Spin size="small" />
              ) : (
                <Typography.Text type="secondary">
                  （本轮没有回复内容）
                </Typography.Text>
              )}
              {turn.notes.length > 0 && (
                <Tooltip title={turn.notes.join('\n')}>
                  <Typography.Text type="secondary" style={{ fontSize: 12 }}>
                    过程 {turn.notes.length} 条
                  </Typography.Text>
                </Tooltip>
              )}
              {turn.cards.map((card) => (
                <div key={card.id} style={{ marginTop: 8 }}>
                  <ProposalCard
                    bookId={bookId}
                    payload={card.payload}
                    onDecided={() =>
                      queryClient.invalidateQueries({
                        queryKey: ['novel-proposals', bookId],
                      })
                    }
                  />
                </div>
              ))}
            </Card>
          ),
        )}
        <div ref={bottomRef} />
      </div>

      {errorText && (
        <Alert type="error" showIcon closable message={errorText} />
      )}

      {pending.length > 0 && (
        <Card size="small" title={`待采纳的提议（${pending.length}）`}>
          {pending.map((item) => (
            <div key={item.id} style={{ marginBottom: 4 }}>
              <ProposalCard
                bookId={bookId}
                existingId={item.id}
                payload={{
                  bookId: item.bookId,
                  sessionId: item.sessionId ?? undefined,
                  asOfChapter: item.asOfChapter ?? undefined,
                  kind: item.kind,
                  subjectKey: item.subjectKey,
                  predicate: item.predicate,
                  objectText: item.objectText,
                  validFromChapter: item.validFromChapter ?? undefined,
                  basisQuote: item.basisQuote ?? undefined,
                }}
                onDecided={() =>
                  queryClient.invalidateQueries({
                    queryKey: ['novel-proposals', bookId],
                  })
                }
              />
            </div>
          ))}
        </Card>
      )}

      <Card size="small">
        <TextArea
          rows={3}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="讨论设定、人物、桥段…（要整本新书请走顶栏「AI 生成」）"
          onPressEnter={(e) => {
            if (!e.shiftKey) {
              e.preventDefault();
              submit();
            }
          }}
        />
        <div
          style={{ marginTop: 8, display: 'flex', justifyContent: 'flex-end' }}
        >
          <Button type="primary" loading={requesting} onClick={submit}>
            发送
          </Button>
        </div>
      </Card>
    </div>
  );
};

export default RightPanel;
