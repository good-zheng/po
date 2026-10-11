import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import type { ReactNode } from 'react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

/**
 * 冲突与设定读法的回归用例：这一组只验「发给服务端的参数长什么样」。
 *
 * 起因是三处分页 off-by-one——后端 `/novel/**` 的页码是 0 基，前端传了 `page: 1`，
 * 于是设定出处、本章冲突、待采纳提议三块面板在数据不足一页时恒为空白，
 * 而空白看起来像「确实没有冲突」，作者不会察觉。这里把 0 基钉成断言。
 * 同理，本章冲突必须带 `chapterId`、出处设定必须带 `sourceChapterId`：
 * 在前端 filter 一页数据等于悄悄截断。
 *
 * 最后两条验「裁定完别只刷新自己那一块」：采纳写的是 canon_entry，中栏的设定卡读
 * `['novel-canon', bookId, …]` 这份缓存，台账和提议卡都必须一起失效它，否则作者会在
 * 同一屏里看到「已采纳」和「采纳前的设定」并存。
 */

const mocks = vi.hoisted(() => ({
  search: new URLSearchParams(''),
  params: { bookId: '7' } as Record<string, string>,
  getBook: vi.fn(),
  getCanon: vi.fn(),
  getCanonEntry: vi.fn(),
  getChapter: vi.fn(),
  getChapterImpact: vi.fn(),
  getChapterRevisions: vi.fn(),
  getChapters: vi.fn(),
  getFindings: vi.fn(),
  getProposals: vi.fn(),
  getChatTicket: vi.fn(),
  getStyleProfile: vi.fn(),
  searchNovel: vi.fn(),
  updateChapter: vi.fn(),
  updateStyleProfile: vi.fn(),
  createProposal: vi.fn(),
  adoptProposal: vi.fn(),
  dismissProposal: vi.fn(),
  getCanonConflicts: vi.fn(),
}));

vi.mock('@/services/novel', () => ({
  getBook: mocks.getBook,
  getCanon: mocks.getCanon,
  getCanonEntry: mocks.getCanonEntry,
  getChapter: mocks.getChapter,
  getChapterImpact: mocks.getChapterImpact,
  getChapterRevisions: mocks.getChapterRevisions,
  getChapters: mocks.getChapters,
  getFindings: mocks.getFindings,
  getProposals: mocks.getProposals,
  getChatTicket: mocks.getChatTicket,
  getStyleProfile: mocks.getStyleProfile,
  searchNovel: mocks.searchNovel,
  updateChapter: mocks.updateChapter,
  updateStyleProfile: mocks.updateStyleProfile,
  createProposal: mocks.createProposal,
  adoptProposal: mocks.adoptProposal,
  dismissProposal: mocks.dismissProposal,
  getCanonConflicts: mocks.getCanonConflicts,
}));
// useNovelChat 只在发送时建连，这里只需要它引用的 WS 地址常量存在
vi.mock('../../chatbot/service', () => ({
  CHAT_WS_URL: 'ws://localhost:5090/ws/chat',
}));
vi.mock('@umijs/max', () => ({
  history: { push: vi.fn() },
  useParams: () => mocks.params,
  useSearchParams: () => [mocks.search, vi.fn()],
}));

import CenterPanel from './CenterPanel';
import NovelStudio from './index';
import RightPanel from './RightPanel';

const emptyPage = { data: { content: [], totalElements: 0 } };

const chapter = (id: number, chapterIndex: number, title: string) => ({
  id,
  bookId: 7,
  chapterIndex,
  title,
  content: `${title}的正文。`,
  wordCount: 12,
  status: 'committed',
  revision: 1,
});

const proposalRow = {
  id: 31,
  bookId: 7,
  sessionId: 's-1',
  kind: 'character',
  subjectKey: 'char:shenqing',
  predicate: 'eye_color',
  objectText: '灰蓝色',
  asOfChapter: 3,
  validFromChapter: 2,
  basisQuote: '她眨了眨眼',
  status: 'pending',
};

/** 中栏那条按出处章取设定的查询被重发了几次 */
const sourceCanonCalls = () =>
  mocks.getCanon.mock.calls.filter(([, q]) => q?.sourceChapterId === 55).length;

const withPendingProposal = () => ({
  data: { content: [proposalRow], totalElements: 1 },
});

function renderWithQuery(ui: ReactNode) {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });
  return render(
    <QueryClientProvider client={client}>{ui}</QueryClientProvider>,
  );
}

beforeEach(() => {
  vi.clearAllMocks();
  mocks.search = new URLSearchParams('');
  mocks.params = { bookId: '7' };
  mocks.getBook.mockResolvedValue({
    data: { id: 7, title: '代码之隙', description: '' },
  });
  mocks.getChapters.mockResolvedValue({
    data: [chapter(55, 3, '第三章'), chapter(56, 4, '第四章')],
  });
  mocks.getStyleProfile.mockResolvedValue({ data: {} });
  mocks.searchNovel.mockResolvedValue({ data: { hits: [], canonHits: [] } });
  mocks.getChapter.mockResolvedValue({
    data: {
      id: 55,
      bookId: 7,
      chapterIndex: 3,
      title: '第三章',
      content: '她的眼睛是灰蓝色的。',
      wordCount: 12,
      status: 'draft',
      revision: 2,
    },
  });
  mocks.getCanon.mockResolvedValue(emptyPage);
  mocks.getFindings.mockResolvedValue(emptyPage);
  mocks.getProposals.mockResolvedValue(emptyPage);
  mocks.getChapterImpact.mockResolvedValue({ data: {} });
  mocks.getChapterRevisions.mockResolvedValue({ data: [] });
  mocks.getCanonEntry.mockResolvedValue({ data: null });
  mocks.getCanonConflicts.mockResolvedValue({ data: [] });
  mocks.createProposal.mockResolvedValue({ data: { id: 31 } });
  mocks.adoptProposal.mockResolvedValue({ data: { id: 41 } });
  mocks.dismissProposal.mockResolvedValue({ data: { id: 31 } });
});

describe('创作台中栏 · 按章取冲突与设定出处', () => {
  it('本章冲突带 chapterId，且页码是 0 基', async () => {
    renderWithQuery(
      <CenterPanel
        bookId={7}
        chapterId={55}
        focusCanon={null}
        onSaved={vi.fn()}
      />,
    );
    await waitFor(() => expect(mocks.getFindings).toHaveBeenCalled());
    expect(mocks.getFindings).toHaveBeenCalledWith(
      expect.objectContaining({ bookId: 7, chapterId: 55, page: 0 }),
    );
  });

  it('出处设定按 sourceChapterId 取，而不是拉一页再前端筛', async () => {
    renderWithQuery(
      <CenterPanel
        bookId={7}
        chapterId={55}
        focusCanon={null}
        onSaved={vi.fn()}
      />,
    );
    await waitFor(() => expect(mocks.getCanon).toHaveBeenCalled());
    expect(mocks.getCanon).toHaveBeenCalledWith(
      7,
      expect.objectContaining({ sourceChapterId: 55, page: 0 }),
    );
  });

  it('没有选中章时不去取「第 undefined 章」的冲突', async () => {
    renderWithQuery(
      <CenterPanel
        bookId={7}
        chapterId={null}
        focusCanon={null}
        onSaved={vi.fn()}
      />,
    );
    await waitFor(() => expect(mocks.getChapter).not.toHaveBeenCalled());
    expect(mocks.getFindings).not.toHaveBeenCalled();
    expect(mocks.getCanon).not.toHaveBeenCalled();
  });

  it('左栏点中的设定按 id 单独取，出处不在本章也能拿到依据原句', async () => {
    mocks.getCanonEntry.mockResolvedValue({
      data: {
        id: 900,
        bookId: 7,
        kind: 'character',
        subjectKey: 'char:shenqing',
        predicate: 'eye_color',
        objectText: '灰蓝色',
        authority: 'model',
        status: 'confirmed',
        validFromChapter: 1,
        sourceChapterId: 12,
        evidenceQuote: '她的眼睛是灰蓝色的。',
      },
    });
    renderWithQuery(
      <CenterPanel
        bookId={7}
        chapterId={55}
        focusCanon={
          {
            canonId: 900,
            subjectKey: 'char:shenqing',
            predicate: 'eye_color',
            objectText: '灰蓝色',
            kind: 'character',
          } as never
        }
        onSaved={vi.fn()}
      />,
    );
    await waitFor(() => expect(mocks.getCanonEntry).toHaveBeenCalledWith(900));
    await waitFor(() =>
      expect(screen.getAllByText(/char:shenqing/).length).toBeGreaterThan(0),
    );
  });
});

describe('创作台右栏 · 待采纳提议', () => {
  it('提议台账按 0 基页码取 pending', async () => {
    renderWithQuery(
      <RightPanel
        bookId={7}
        referenceChapterId={55}
        referenceChapterIndex={3}
      />,
    );
    await waitFor(() => expect(mocks.getProposals).toHaveBeenCalled());
    expect(mocks.getProposals).toHaveBeenCalledWith(
      expect.objectContaining({ bookId: 7, status: 'pending', page: 0 }),
    );
  });

  it('pending 提议渲染成可裁定的卡', async () => {
    mocks.getProposals.mockResolvedValue(withPendingProposal());
    renderWithQuery(
      <RightPanel
        bookId={7}
        referenceChapterId={55}
        referenceChapterIndex={3}
      />,
    );
    await waitFor(() =>
      expect(screen.getByText('待采纳的提议（1）')).toBeInTheDocument(),
    );
    // antd 在两字按钮中间插空格（「采 纳」），按可及名查要用正则而不是字面量
    expect(
      screen.getByRole('button', { name: /^采\s*纳$/ }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole('button', { name: /^驳\s*回$/ }),
    ).toBeInTheDocument();
  });

  /**
   * 采纳会把卡升成 canon_entry，而中栏的「出处标在本章的设定」读的是 ['novel-canon', bookId, …]
   * 这份缓存：不一起失效，作者点完采纳看到的中栏设定仍是采纳前的。
   */
  it('右栏采纳后中栏重取本章设定，两处不是各读各的缓存', async () => {
    mocks.getProposals.mockResolvedValue(withPendingProposal());
    renderWithQuery(
      <>
        <CenterPanel
          bookId={7}
          chapterId={55}
          focusCanon={null}
          onSaved={vi.fn()}
        />
        <RightPanel
          bookId={7}
          referenceChapterId={55}
          referenceChapterIndex={3}
        />
      </>,
    );
    await waitFor(() =>
      expect(mocks.getCanon).toHaveBeenCalledWith(
        7,
        expect.objectContaining({ sourceChapterId: 55 }),
      ),
    );
    await waitFor(() =>
      expect(
        screen.getByRole('button', { name: /^采\s*纳$/ }),
      ).toBeInTheDocument(),
    );
    const before = sourceCanonCalls();

    fireEvent.click(screen.getByRole('button', { name: /^采\s*纳$/ }));
    await waitFor(() =>
      expect(mocks.adoptProposal).toHaveBeenCalledWith(31, {
        closeAssertionIds: undefined,
      }),
    );
    await waitFor(() => expect(sourceCanonCalls()).toBeGreaterThan(before));
  });
});

describe('创作台 · ?chapterId= 深链', () => {
  /** 台账点「第 N 章」跳过来，中栏读的就是那一章的冲突；落在第一章等于没跳 */
  it('带章号时选中那一章，中栏按它取冲突', async () => {
    mocks.search = new URLSearchParams('chapterId=56');
    renderWithQuery(<NovelStudio />);
    await waitFor(() =>
      expect(mocks.getFindings).toHaveBeenCalledWith(
        expect.objectContaining({ chapterId: 56 }),
      ),
    );
  });

  /** 深链的章号可能来自一份已被删改的台账：不能拿它去查「第 999 章」 */
  it('章号不在本书章节里时退回第一章', async () => {
    mocks.search = new URLSearchParams('chapterId=999');
    renderWithQuery(<NovelStudio />);
    await waitFor(() => expect(mocks.getFindings).toHaveBeenCalled());
    await waitFor(() =>
      expect(mocks.getFindings).toHaveBeenCalledWith(
        expect.objectContaining({ chapterId: 55 }),
      ),
    );
  });
});
