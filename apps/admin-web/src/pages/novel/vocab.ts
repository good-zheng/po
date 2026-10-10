import type {
  CanonAuthority,
  CanonKind,
  CanonStatus,
  FindingSeverity,
  FindingStatus,
} from '@po/types';

/**
 * 小说模块显示词表：一个枚举一张表，标签与 AntD 颜色只在这里定义一次。
 *
 * `rejected` 在设定侧读「已否决」、在冲突侧读「已驳回」——两者客体不同、动作也不同：
 * 前者是作者否决一条设定，后者是作者驳回闸门报出的冲突，共用一个词会让作者找错对象。
 * 章节状态是作者手上那份稿子的状态，任务阶段是生成流水线的档位，二者不得共用词语：
 * 所以 `awaiting_review` 读「待闸门」、`committed` 读「已入库」，
 * 「待复核」「已定稿」从此只指章节状态。
 */

export type BadgeStatus =
  | 'default'
  | 'error'
  | 'processing'
  | 'success'
  | 'warning';

export type VocabEntry = {
  readonly label: string;
  readonly color: string;
};

export type BadgeVocabEntry = VocabEntry & { readonly badge: BadgeStatus };

export type BookStatusKey = 'ongoing' | 'completed' | 'paused';
export type ChapterStatusKey = 'draft' | 'pending_review' | 'committed';
export type CheckerKey = 'rule' | 'judge';
export type JobStageKey =
  | 'queued'
  | 'writing'
  | 'gating'
  | 'awaiting_review'
  | 'committed'
  | 'failed';

export const bookStatusMap: Record<string, VocabEntry> = {
  ongoing: { label: '连载中', color: 'processing' },
  completed: { label: '已完结', color: 'success' },
  paused: { label: '暂停更新', color: 'warning' },
} as const satisfies Record<BookStatusKey, VocabEntry>;

export const chapterStatusMap: Record<string, VocabEntry> = {
  draft: { label: '草稿', color: 'default' },
  pending_review: { label: '待复核', color: 'warning' },
  committed: { label: '已定稿', color: 'success' },
} as const satisfies Record<ChapterStatusKey, VocabEntry>;

export const canonStatusMap: Record<string, VocabEntry> = {
  confirmed: { label: '已确认', color: 'green' },
  disputed: { label: '存疑', color: 'orange' },
  todo: { label: '缺口', color: 'gold' },
  rejected: { label: '已否决', color: 'red' },
} as const satisfies Record<CanonStatus, VocabEntry>;

export const findingStatusMap: Record<string, VocabEntry> = {
  open: { label: '待裁定', color: 'processing' },
  adopted: { label: '已采纳', color: 'success' },
  rejected: { label: '已驳回', color: 'default' },
  waived: { label: '已豁免', color: 'blue' },
  orphaned: { label: '已失效', color: 'default' },
} as const satisfies Record<FindingStatus, VocabEntry>;

export const severityMap: Record<string, BadgeVocabEntry> = {
  blocker: { label: '阻断', color: 'error', badge: 'error' },
  major: { label: '重要', color: 'warning', badge: 'warning' },
  minor: { label: '轻微', color: 'default', badge: 'default' },
} as const satisfies Record<FindingSeverity, BadgeVocabEntry>;

export const checkerMap: Record<string, VocabEntry> = {
  rule: { label: '规则闸门', color: 'default' },
  judge: { label: '语义裁判', color: 'default' },
} as const satisfies Record<CheckerKey, VocabEntry>;

export const canonKindMap: Record<string, VocabEntry> = {
  world_rule: { label: '世界规则', color: 'default' },
  character: { label: '角色', color: 'default' },
  relation: { label: '关系', color: 'default' },
  location: { label: '地点', color: 'default' },
  item: { label: '物品', color: 'default' },
  theme: { label: '主题', color: 'default' },
  style: { label: '文风', color: 'default' },
} as const satisfies Record<CanonKind, VocabEntry>;

export const jobStageMap: Record<string, VocabEntry> = {
  queued: { label: '排队中', color: 'default' },
  writing: { label: '写作中', color: 'default' },
  gating: { label: '闸门校验', color: 'default' },
  awaiting_review: { label: '待闸门', color: 'default' },
  committed: { label: '已入库', color: 'default' },
  failed: { label: '已失败', color: 'default' },
} as const satisfies Record<JobStageKey, VocabEntry>;

export const canonAuthorityMap: Record<string, BadgeVocabEntry> = {
  author: { label: '作者裁定', color: 'default', badge: 'success' },
  text: { label: '原文抽取', color: 'default', badge: 'processing' },
  model: { label: '模型自证', color: 'default', badge: 'default' },
} as const satisfies Record<CanonAuthority, BadgeVocabEntry>;

export const toOptions = (
  map: Record<string, VocabEntry>,
): { value: string; label: string }[] =>
  Object.entries(map).map(([value, entry]) => ({ value, label: entry.label }));

export const toValueEnum = (
  map: Record<string, VocabEntry>,
): Record<string, { text: string }> =>
  Object.fromEntries(
    Object.entries(map).map(([key, entry]) => [key, { text: entry.label }]),
  );
