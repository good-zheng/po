import { history } from '@umijs/max';
import {
  Alert,
  Button,
  Card,
  Checkbox,
  Input,
  Segmented,
  Space,
  Tag,
  Typography,
} from 'antd';
import { useEffect, useMemo, useState } from 'react';
import { resolveContinueRun } from './chapterRange';
import {
  type NovelInterruptValue,
  type NovelRunContext,
  useNovelRun,
} from './useNovelRun';

const { TextArea } = Input;

type RunMode = 'continue' | 'new';

/**
 * 生成面板：`agent: 'novel'` 那条长链路唯一的浏览器入口。
 *
 * 它刻意不落在三栏里的任何一栏（§10.3 的能力边界：左=查选、中=看改正文、右=只谈不写），
 * 而是从顶栏拉出的抽屉里跑。中栏依旧只走 REST：这一轮即便产出了正文，界面上的流式文本
 * 也只算预览，落库以归档确认后中栏按章节接口读回的为准。
 *
 * 两条入口：
 * - **续写本书**（在工作台里打开时的默认）：这一句直接变成「给当前这本书往后追加第
 *   N+1 章起的几章」，默认一路写完不再问人，句子里的意见（「让陈默先上天台」）会连着
 *   进大纲、场景卡与正文提示词。
 * - **写本新书**：一整本从零开始（构思 → 大纲 → 逐章 → 归档），服务端默认 3 章 /
 *   每章约 1200 字，参数在 `build_novel_agent` 的入参里，不在界面上。
 */
const RunPanel: React.FC<{
  /** 归档成功后的回调：宿主按归档的是当前书还是新书决定刷哪些缓存 */
  onArchived: (bookId: number) => void;
  /** 关掉抽屉：续写成功后正文就在中栏，没必要让作者先找入口 */
  onClose?: () => void;
  /** 当前工作台打开的书；不存在时只有「写本新书」一条路 */
  book?: { id: number; title: string };
  /** 这本书已有的章节：只需要章号与「有没有正文」，正文本身不过网 */
  chapters?: { id: number; chapterIndex: number; wordCount: number }[];
}> = ({ onArchived, onClose, book, chapters }) => {
  const [idea, setIdea] = useState('');
  const [answered, setAnswered] = useState<string | null>(null);
  const [mode, setMode] = useState<RunMode>(book ? 'continue' : 'new');
  // 默认「不问」：这条入口的存在理由就是一句话直接出章。勾上它才保留两处人工口。
  const [askFirst, setAskFirst] = useState(false);
  // 归档提示要说对「新增」还是「新书」，用的是发起那一轮时的模式，不是当前选择的
  const [launchedMode, setLaunchedMode] = useState<RunMode | null>(null);
  const run = useNovelRun(onArchived);

  // 游标口径与服务端 countWrittenByBook 一致：数的是**有正文**的章，不是章节行数。
  // 作者在章节管理里留空排下的「待写占位」既不进游标（续写要从它开始并把它填掉），
  // 也不能当「上一章结尾」的取源——按行数算会跳过它往后写，那一章就永久空着。
  const written = useMemo(
    () => (chapters ?? []).filter((item) => item.wordCount > 0).length,
    [chapters],
  );
  // 空行夹在已写章之间时对不上账：续写起点是「有正文的章数 + 1」，会撞上有正文的那一章
  const gaps = useMemo(() => {
    const rows = chapters ?? [];
    const lastWritten = rows.reduce(
      (max, item) =>
        item.wordCount > 0 ? Math.max(max, item.chapterIndex) : max,
      0,
    );
    return rows
      .filter((item) => item.wordCount === 0 && item.chapterIndex < lastWritten)
      .map((item) => item.chapterIndex)
      .sort((a, b) => a - b);
  }, [chapters]);
  const fillsPlaceholder = (chapters ?? []).some(
    (item) => item.wordCount === 0 && item.chapterIndex === written + 1,
  );
  const plan = useMemo(
    () => resolveContinueRun(idea, written),
    [idea, written],
  );
  // 没有当前书就没有「续写」这条路：Segmented 不渲染，mode 也只能是 new
  const isContinue = mode === 'continue' && book != null;

  // 新卡到达（或旧卡被答完置空）都重新给出可点状态；恢复成「未回复」而不是留着上一次的标签
  useEffect(() => {
    setAnswered(null);
  }, [run.interrupt]);

  const reply = (value: string, label: string) => {
    setAnswered(label);
    run.answer(value);
  };

  const submit = () => {
    const context: NovelRunContext = { auto: !askFirst };
    if (isContinue && book) {
      context.bookId = String(book.id);
      if (plan.fromChapter != null) context.fromChapter = plan.fromChapter;
      if (plan.chapterCount != null) context.chapterCount = plan.chapterCount;
      // 结尾原文按章号取最后一条，不按数组下标：宿主传进来的顺序不该被依赖。
      const tail = chapters?.find(
        (item) => item.chapterIndex === written && item.wordCount > 0,
      );
      if (tail) context.tailChapterId = String(tail.id);
    }
    setLaunchedMode(mode);
    void run.start(idea, context);
  };

  return (
    <Space direction="vertical" size={12} style={{ width: '100%' }}>
      {book && (
        <Segmented
          block
          value={mode}
          onChange={(value) => setMode(value as RunMode)}
          options={[
            { label: `续写《${book.title}》`, value: 'continue' },
            { label: '写本新书', value: 'new' },
          ]}
        />
      )}

      <Alert
        type="info"
        showIcon
        message={
          isContinue
            ? '一句话直接出章：这一轮给当前这本书往后追加'
            : '这一轮会写一整本新书，不是给当前这本书补章'
        }
        description={
          <Typography.Text style={{ fontSize: 12 }}>
            {isContinue ? (
              <>
                句子里写明的章号会被读成范围（如「开始创作第三至第十章的内容」），
                没写就按默认 3
                章往后排；其余文字按「对这本书的意见」原样进大纲、
                场景卡与正文提示词。
                <strong>只追加已定稿之后的章，不改写已有正文</strong>。
                已登记的正典会作为硬约束喂给这一轮。
              </>
            ) : (
              <>
                链路是 构思 → 世界设定 → 大纲 → 逐章写作与两道闸门 →
                归档确认；默认 3 章、每章约 1200 字，全程数分钟。
                {askFirst ? (
                  <>
                    <strong>没点「确认归档」，正文与正典都不会入库</strong>
                    （这是设计，不是失败）。
                  </>
                ) : null}
              </>
            )}
            {askFirst
              ? '已勾选「先问我」：场景卡计划闸门与最后的归档确认都会停下等你拍板。'
              : '默认不问：两处人工口自动放行，正文写完即入库。'}
          </Typography.Text>
        }
      />

      <Card size="small">
        <TextArea
          rows={3}
          value={idea}
          onChange={(e) => setIdea(e.target.value)}
          placeholder={
            isContinue
              ? '开始创作第三至第十章的内容；意见可以直接跟在这句后面，例如「让陈默先上天台，别急着暴露身份」'
              : '一句话想法：题材 + 主角 + 一个能把故事拧起来的变数'
          }
          disabled={run.phase === 'running' || run.phase === 'connecting'}
        />
        {isContinue && (
          <Typography.Paragraph
            type="secondary"
            style={{ fontSize: 12, margin: '6px 0 0' }}
          >
            {plan.preview}
            {fillsPlaceholder
              ? `；第 ${written + 1} 章是你留的待写占位，这一轮会按书里已有的设定与大纲把它填掉。`
              : ''}
          </Typography.Paragraph>
        )}
        {isContinue && gaps.length > 0 && (
          <Typography.Paragraph
            type="warning"
            style={{ fontSize: 12, margin: '6px 0 0' }}
          >
            第 {gaps.join('、')}{' '}
            章正文为空却排在已写章之前：续写起点会撞上有正文的章并报「已有正文」。
            请先把这些空位补上或删掉，再来续写。
          </Typography.Paragraph>
        )}
        <div
          style={{
            marginTop: 8,
            display: 'flex',
            alignItems: 'center',
            gap: 8,
            justifyContent: 'flex-end',
          }}
        >
          <Checkbox
            checked={askFirst}
            onChange={(e) => setAskFirst(e.target.checked)}
            disabled={run.phase === 'running' || run.phase === 'connecting'}
          >
            写之前先问我
          </Checkbox>
          <PhaseTag phase={run.phase} />
          <Button
            type="primary"
            loading={run.phase === 'running' || run.phase === 'connecting'}
            disabled={run.phase === 'awaiting' || !idea.trim()}
            onClick={submit}
          >
            {run.phase === 'idle' || run.phase === 'finished'
              ? isContinue
                ? '开始续写'
                : '开始生成'
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
        <Alert
          type="error"
          showIcon
          closable
          message="这一轮没跑成"
          description={
            <Typography.Text style={{ fontSize: 12 }}>
              {run.errorText}
            </Typography.Text>
          }
        />
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
        <Card size="small" title="成稿预览（以中栏按章节接口读回的为准）">
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
          message={
            launchedMode === 'continue'
              ? '已续写入库：新增的章就在这本书的章节里'
              : `已入库：新书 ID ${run.archivedBookId}`
          }
          description={
            <Space>
              {launchedMode === 'continue' && onClose ? (
                <Button size="small" type="primary" onClick={onClose}>
                  关掉抽屉看中栏
                </Button>
              ) : (
                <Button
                  size="small"
                  onClick={() =>
                    history.push(`/novel/book/${run.archivedBookId}/studio`)
                  }
                >
                  打开这本书的工作台
                </Button>
              )}
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
