import { useMutation } from '@tanstack/react-query';
import {
  Alert,
  Button,
  Card,
  Input,
  Modal,
  message,
  Space,
  Tag,
  Typography,
} from 'antd';
import { useState } from 'react';
import {
  adoptProposal,
  type CanonEntry,
  createProposal,
  dismissProposal,
  getCanonConflicts,
  type ProposalRequest,
} from '@/services/novel';
import type { ProposalPayload } from './useNovelChat';

const { TextArea } = Input;

/**
 * 一张待采纳的设定提议卡（D8「只谈不写」的落点）。
 *
 * 卡是 WS 帧的视图，库里还没有它：`proposal` 帧只上浮事件，落库由这里的
 * `POST /novel/proposals` 完成，状态恒为 pending（入参类型里也没有 status/authority）。
 * 采纳走冲突预览：同主同谓且值不同的已生效断言必须先摆给作者看，
 * 服务端撞车时一条不落（§10.5-④）。
 */
const ProposalCard: React.FC<{
  bookId: number;
  payload: ProposalPayload;
  /** 已经在 `canon_proposal` 里的卡（来自待办列表）：跳过 POST，直接裁定 */
  existingId?: number;
  onDecided: () => void;
}> = ({ bookId, payload, existingId, onDecided }) => {
  const [messageApi, contextHolder] = message.useMessage();
  const [dismissOpen, setDismissOpen] = useState(false);
  const [basis, setBasis] = useState('');
  const [conflicts, setConflicts] = useState<CanonEntry[] | null>(null);

  const request: ProposalRequest = {
    bookId,
    sessionId: payload.sessionId,
    asOfChapter: payload.asOfChapter,
    kind: payload.kind,
    subjectKey: payload.subjectKey,
    predicate: payload.predicate,
    objectText: payload.objectText,
    validFromChapter: payload.validFromChapter,
    basisQuote: payload.basisQuote,
  };

  const saveMutation = useMutation({
    mutationFn: () => createProposal(request),
    onError: (err: Error) => messageApi.error(err.message || '提议入台账失败'),
  });

  const adoptMutation = useMutation({
    mutationFn: (vars: { proposalId: number; closeAssertionIds?: number[] }) =>
      adoptProposal(vars.proposalId, {
        closeAssertionIds: vars.closeAssertionIds,
      }),
    onSuccess: () => {
      messageApi.success('已采纳为设定条目（来源：作者裁定）');
      setConflicts(null);
      onDecided();
    },
    onError: (err: Error) => messageApi.error(err.message || '采纳失败'),
  });

  const dismissMutation = useMutation({
    mutationFn: (vars: { proposalId: number; basis: string }) =>
      dismissProposal(vars.proposalId, { basis: vars.basis }),
    onSuccess: () => {
      messageApi.success('已驳回，理由已留档');
      setDismissOpen(false);
      setBasis('');
      onDecided();
    },
    onError: (err: Error) => messageApi.error(err.message || '驳回失败'),
  });

  const doAdopt = async (closeAssertionIds?: number[]) => {
    const proposalId = existingId ?? (await saveMutation.mutateAsync()).data.id;
    if (!proposalId) {
      messageApi.error('提议未落库，无法采纳');
      return;
    }
    adoptMutation.mutate({ proposalId, closeAssertionIds });
  };

  const onAdoptClick = async () => {
    let list: CanonEntry[] = [];
    try {
      const res = await getCanonConflicts(bookId, {
        subjectKey: request.subjectKey,
        predicate: request.predicate,
        objectText: request.objectText,
        asOfChapter: request.asOfChapter,
      });
      list = res.data ?? [];
    } catch (err) {
      // 预览读不到不等于没有冲突：让作者决定要不要继续，而不是静默直采
      messageApi.warning(
        `${err instanceof Error ? err.message : '冲突预览失败'}；可稍后在「设定」页复核`,
      );
      await doAdopt();
      return;
    }
    if (list.length > 0) {
      setConflicts(list);
      return;
    }
    await doAdopt();
  };

  const card = (
    <Card
      size="small"
      title={
        <Space size={4}>
          <Tag color="blue">{payload.kind ?? 'fact'}</Tag>
          <span>待采纳提议</span>
        </Space>
      }
      style={{ marginBottom: 8 }}
    >
      <Typography.Paragraph style={{ marginBottom: 4 }}>
        <Typography.Text strong>{payload.subjectKey}</Typography.Text>
        {' · '}
        {payload.predicate}
        {' · '}
        {payload.objectText}
      </Typography.Paragraph>
      <Typography.Paragraph
        type="secondary"
        style={{ marginBottom: 4, fontSize: 12 }}
      >
        生效自第 {payload.validFromChapter ?? payload.asOfChapter ?? '-'}{' '}
        章（参照章 {payload.asOfChapter ?? '-'}）
      </Typography.Paragraph>
      {payload.basisQuote && (
        <Typography.Paragraph
          type="secondary"
          style={{ marginBottom: 8, fontSize: 12 }}
        >
          依据：「{payload.basisQuote}」
        </Typography.Paragraph>
      )}
      <Space>
        <Button
          type="primary"
          size="small"
          loading={saveMutation.isPending || adoptMutation.isPending}
          onClick={() => void onAdoptClick()}
        >
          采纳
        </Button>
        <Button size="small" onClick={() => setDismissOpen(true)}>
          驳回
        </Button>
      </Space>
    </Card>
  );

  return (
    <>
      {contextHolder}
      {card}
      <Modal
        title="与已生效设定撞车"
        open={!!conflicts}
        okText="覆盖并闭旧区间"
        cancelText="先不采纳"
        okButtonProps={{
          danger: true,
          loading: adoptMutation.isPending,
        }}
        onCancel={() => setConflicts(null)}
        onOk={() =>
          void doAdopt(
            (conflicts ?? []).map((item) => item.id).filter((id) => id > 0),
          )
        }
      >
        <Alert
          type="warning"
          showIcon
          style={{ marginBottom: 12 }}
          message="采纳会写下新设定条目并关闭下列旧条目的生效区间；不覆盖则服务端一条不落。"
        />
        {conflicts?.map((item) => (
          <Typography.Paragraph key={item.id} style={{ marginBottom: 4 }}>
            <Typography.Text code>#{item.id}</Typography.Text> {item.subjectKey}{' '}
            · {item.predicate} · {item.objectText}（第 {item.validFromChapter}
            {item.validUntilChapter ? `~${item.validUntilChapter}` : ' 章起'}，
            {item.authority}）
          </Typography.Paragraph>
        ))}
      </Modal>
      <Modal
        title="驳回理由"
        open={dismissOpen}
        okText="确认驳回"
        cancelText="取消"
        okButtonProps={{
          danger: true,
          disabled: basis.trim().length === 0,
          loading: saveMutation.isPending || dismissMutation.isPending,
        }}
        onCancel={() => setDismissOpen(false)}
        onOk={async () => {
          const proposalId =
            existingId ?? (await saveMutation.mutateAsync()).data.id;
          if (!proposalId) {
            messageApi.error('提议未落库，无法驳回');
            return;
          }
          dismissMutation.mutate({ proposalId, basis: basis.trim() });
        }}
      >
        <TextArea
          rows={3}
          maxLength={200}
          showCount
          value={basis}
          onChange={(e) => setBasis(e.target.value)}
          placeholder="为什么不采纳这条设定（必填，会留在台账里）"
        />
      </Modal>
    </>
  );
};

export default ProposalCard;
