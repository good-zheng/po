import { history } from '@umijs/max';
import { Alert, Button, Card, Input, Space, Tag, Typography } from 'antd';
import { useEffect, useState } from 'react';
import { type NovelInterruptValue, useNovelRun } from './useNovelRun';

const { TextArea } = Input;

/**
 * 生成面板：`agent: 'novel'` 那条长链路唯一的浏览器入口。
 *
 * 它刻意不落在三栏里的任何一栏（§10.3 的能力边界：左=查选、中=看改正文、右=只谈不写），
 * 而是从顶栏拉出的抽屉里跑。中栏依旧只走 REST：这一轮即便产出了正文，界面上的流式文本
 * 也只算预览，落库以归档确认后中栏按章节接口读回的为准。
 *
 * 一次运行 = 一整本**新书**（构思 → 大纲 → 逐章 → 归档），服务端默认 3 章 / 每章约 1200 字，
 * 参数在 `build_novel_agent` 的入参里，不在界面上。所以「给当前这本书补一章」不是这里能做的事。
 */
const RunPanel: React.FC<{
  /** 归档成功后的回调：让宿主失效书架缓存（生成产出的是另一本新书） */
  onArchived: (bookId: number) => void;
}> = ({ onArchived }) => {
  const [idea, setIdea] = useState('');
  const [answered, setAnswered] = useState<string | null>(null);
  const run = useNovelRun(onArchived);

  // 新卡到达（或旧卡被答完置空）都重新给出可点状态；恢复成「未回复」而不是留着上一次的标签
  useEffect(() => {
    setAnswered(null);
  }, [run.interrupt]);

  const reply = (value: string, label: string) => {
    setAnswered(label);
    run.answer(value);
  };

  return (
    <Space direction="vertical" size={12} style={{ width: '100%' }}>
      <Alert
        type="info"
        showIcon
        message="这一轮会写一整本新书，不是给当前这本书补章"
        description={
          <Typography.Text style={{ fontSize: 12 }}>
            链路是 构思 → 世界设定 → 大纲 → 逐章写作与两道闸门 → 归档确认；默认
            3 章、每章约 1200
            字，全程数分钟。中途会停下等你拍板两次：场景卡的计划闸门、以及最后的归档确认。
            <strong>没点「确认归档」，正文与正典都不会入库</strong>
            （这是设计，不是失败）。
          </Typography.Text>
        }
      />

      <Card size="small">
        <TextArea
          rows={3}
          value={idea}
          onChange={(e) => setIdea(e.target.value)}
          placeholder="一句话想法：题材 + 主角 + 一个能把故事拧起来的变数"
          disabled={run.phase === 'running' || run.phase === 'connecting'}
        />
        <div
          style={{
            marginTop: 8,
            display: 'flex',
            alignItems: 'center',
            gap: 8,
            justifyContent: 'flex-end',
          }}
        >
          <PhaseTag phase={run.phase} />
          <Button
            type="primary"
            loading={run.phase === 'running' || run.phase === 'connecting'}
            disabled={run.phase === 'awaiting' || !idea.trim()}
            onClick={() => void run.start(idea)}
          >
            {run.phase === 'idle' || run.phase === 'finished'
              ? '开始生成'
              : '重新生成'}
          </Button>
        </div>
        {run.phase === 'awaiting' && (
          <Typography.Text type="warning" style={{ fontSize: 12 }}>
            上方有等你拍板的卡片，回答完才能起新一轮。
          </Typography.Text>
        )}
      </Card>

      {run.errorText && (
        <Alert type="error" showIcon closable message={run.errorText} />
      )}

      {run.notes.length > 0 && (
        <Card size="small" title={`过程（${run.notes.length} 条）`}>
          <div style={{ maxHeight: 200, overflow: 'auto' }}>
            {run.notes.map((note, index) => (
              <Typography.Paragraph
                // 过程行只追加、不重排不删除，同一节点名还会重复出现，
                // 所以「下标 + 文本」在这一屏是稳定且唯一的键。
                // biome-ignore lint/suspicious/noArrayIndexKey: append-only list, duplicates allowed
                key={`${index}-${note}`}
                style={{ fontSize: 12, marginBottom: 2 }}
                type="secondary"
              >
                {note}
              </Typography.Paragraph>
            ))}
          </div>
        </Card>
      )}

      {run.interrupt && (
        <InterruptCard
          value={run.interrupt}
          answered={answered}
          onReply={reply}
        />
      )}

      {run.text && (
        <Card size="small" title="成稿预览（以归档确认后中栏读回的为准）">
          <Typography.Paragraph
            style={{ whiteSpace: 'pre-wrap', maxHeight: 360, overflow: 'auto' }}
          >
            {run.text}
          </Typography.Paragraph>
        </Card>
      )}

      {run.archivedBookId != null && (
        <Alert
          type="success"
          showIcon
          message={`已入库：新书 ID ${run.archivedBookId}`}
          description={
            <Space>
              <Button
                size="small"
                onClick={() =>
                  history.push(`/novel/book/${run.archivedBookId}/studio`)
                }
              >
                打开这本书的工作台
              </Button>
              <Button size="small" onClick={() => history.push('/novel/list')}>
                回书架
              </Button>
            </Space>
          }
        />
      )}
    </Space>
  );
};

const PhaseTag: React.FC<{ phase: string }> = ({ phase }) => {
  const map: Record<string, { color: string; text: string }> = {
    idle: { color: 'default', text: '未开始' },
    connecting: { color: 'processing', text: '连接中' },
    running: { color: 'processing', text: '生成中' },
    awaiting: { color: 'warning', text: '等你拍板' },
    finished: { color: 'success', text: '本轮结束' },
    failed: { color: 'error', text: '本轮中断' },
  };
  const item = map[phase] ?? map.idle;
  return <Tag color={item.color}>{item.text}</Tag>;
};

/**
 * 两处人工口共用一张卡，按 `stage` 分流：`plan_approval` 是计划闸门，
 * 其余（归档确认没有 stage 键）走归档那一套措辞与按钮。
 *
 * 回复词只有「同意类」会被服务端认成放行（`_APPROVE_WORDS`），其余一律按「否」处理，
 * 所以按钮直接发 `yes` / `no`，不让人自由输入——自由输入会让「先看看」这种闲聊
 * 被当成停笔指令，而停笔对这一章不可逆（本章按当前卡定稿并写 `halted_at`）。
 */
const InterruptCard: React.FC<{
  value: NovelInterruptValue;
  answered: string | null;
  onReply: (value: string, label: string) => void;
}> = ({ value, answered, onReply }) => {
  const isPlan = value.stage === 'plan_approval';
  return (
    <Card
      size="small"
      title={
        isPlan ? `计划闸门 · 第 ${value.chapter ?? '?'} 章等你拍板` : '归档确认'
      }
      extra={<Tag color="warning">人工口</Tag>}
    >
      <Space direction="vertical" size={8} style={{ width: '100%' }}>
        <Typography.Paragraph style={{ marginBottom: 0 }}>
          {value.question}
        </Typography.Paragraph>

        {isPlan && value.card_text && (
          <Card size="small" type="inner" title="这张场景卡的原样">
            <Typography.Paragraph
              style={{ whiteSpace: 'pre-wrap', fontSize: 12, marginBottom: 0 }}
            >
              {value.card_text}
            </Typography.Paragraph>
          </Card>
        )}
        {isPlan && (
          <Typography.Text type="secondary" style={{ fontSize: 12 }}>
            未平的冲突 {(value.blockers ?? []).length} 条
            {value.reason ? `（${value.reason}）` : ''}
            {value.unreviewed
              ? ' · 批准后本章会标注为「计划未经完整审查」'
              : ''}
          </Typography.Text>
        )}

        {!isPlan && (
          <Typography.Text type="secondary" style={{ fontSize: 12 }}>
            {value.title ? `《${value.title}》` : ''}
            {value.chapter_count != null ? ` 共 ${value.chapter_count} 章` : ''}
            {(value.frozen ?? []).length > 0
              ? ` · ${value.frozen?.length} 章待人工裁定`
              : ''}
            {value.halted_at != null ? ` · 停笔于第 ${value.halted_at} 章` : ''}
          </Typography.Text>
        )}
        {!isPlan && value.frozen_note && (
          <Typography.Text type="secondary" style={{ fontSize: 12 }}>
            {value.frozen_note}
          </Typography.Text>
        )}
        {!isPlan && value.open_questions && value.open_questions.length > 0 && (
          <Typography.Text type="secondary" style={{ fontSize: 12 }}>
            圣经待答问题：{value.open_questions.join(' / ')}
          </Typography.Text>
        )}

        <Space>
          {answered ? (
            <Typography.Text type="secondary">
              已回复「{answered}」，等本轮收尾后续跑
            </Typography.Text>
          ) : (
            <>
              <Button
                type="primary"
                onClick={() =>
                  onReply('yes', isPlan ? '照这张卡继续写' : '确认归档入库')
                }
              >
                {isPlan ? '照这张卡继续写' : '确认归档入库'}
              </Button>
              <Button
                onClick={() =>
                  onReply('no', isPlan ? '停笔并转归档' : '暂不归档')
                }
              >
                {isPlan ? '停笔并转归档' : '暂不归档'}
              </Button>
            </>
          )}
        </Space>
        {value.hint && (
          <Typography.Text type="secondary" style={{ fontSize: 12 }}>
            {value.hint}
          </Typography.Text>
        )}
      </Space>
    </Card>
  );
};

export default RunPanel;
