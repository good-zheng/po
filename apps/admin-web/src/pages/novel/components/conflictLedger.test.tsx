import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import type { ReactNode } from 'react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

/**
 * 冲突台账与设定冲突预览的回归用例。
 *
 * 钉住四件容易静默坏掉的事：
 * ①`/novel/**` 的页码是 0 基，传 1 会让台账在数据不足一页时永远空白；
 * ②编辑一条设定要把自己 excludeId 掉，否则「改自己的值」会被报成与自己撞车；
 * ③台账的 `?bookId=` 深链必须真的落到查询参数里，创作台跳过来的作者才不用重选作品；
 * ④裁定采纳后要失效 `novel-canon`，否则台账说「已采纳」而设定面板还是旧的。
 */

const mocks = vi.hoisted(() => ({
  query: new URLSearchParams(''),
  push: vi.fn(),
  getBooks: vi.fn(),
  getChapters: vi.fn(),
  getFindings: vi.fn(),
  adjudicateFinding: vi.fn(),
  getCanon: vi.fn(),
  getCanonConflicts: vi.fn(),
  createCanon: vi.fn(),
  updateCanon: vi.fn(),
  retireCanon: vi.fn(),
  getCanonEntry: vi.fn(),
  getChapter: vi.fn(),
  getChapterImpact: vi.fn(),
  getChapterRevisions: vi.fn(),
  updateChapter: vi.fn(),
}));

vi.mock('@/services/novel', () => ({
  getBooks: mocks.getBooks,
  getChapters: mocks.getChapters,
  getFindings: mocks.getFindings,
  adjudicateFinding: mocks.adjudicateFinding,
  getCanon: mocks.getCanon,
  getCanonConflicts: mocks.getCanonConflicts,
  createCanon: mocks.createCanon,
  updateCanon: mocks.updateCanon,
  retireCanon: mocks.retireCanon,
  getCanonEntry: mocks.getCanonEntry,
  getChapter: mocks.getChapter,
  getChapterImpact: mocks.getChapterImpact,
  getChapterRevisions: mocks.getChapterRevisions,
  updateChapter: mocks.updateChapter,
}));
vi.mock('@umijs/max', () => ({
  history: { push: mocks.push },
  useSearchParams: () => [mocks.query, vi.fn()],
}));

import NovelReviewList from '../review';
import CenterPanel from '../studio/CenterPanel';
import CanonPanel from './CanonPanel';
import FindingTable from './FindingTable';

const canonRow = {
  id: 41,
  bookId: 7,
  kind: 'character',
  subjectKey: 'char:shenqing',
  predicate: 'eye_color',
  objectText: '蓝色',
  authority: 'author',
  status: 'confirmed',
  validFromChapter: 1,
  validUntilChapter: null,
};

const chapterRow = {
  id: 55,
  bookId: 7,
  chapterIndex: 3,
  title: '第三章',
  content: '她的眼睛是灰蓝色的',
  wordCount: 11,
  status: 'committed',
  revision: 2,
};

const findingRow = {
  id: 12,
  bookId: 7,
  chapterId: 55,
  chapterIndex: 3,
  chapterTitle: '第三章',
  chapterStatus: 'committed',
  revision: 2,
  code: 'attribute_conflict',
  severity: 'major',
  checker: 'rule',
  status: 'open',
  evidenceQuote: '她的眼睛是灰蓝色的',
  explanation: '同主同谓两个值',
};

function renderWithQuery(ui: ReactNode) {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });
  return render(
    <QueryClientProvider client={client}>{ui}</QueryClientProvider>,
  );
}

/**
 * 弹窗字段按 id 取，但搜索表单里也有同名的「实体键」输入框，
 * 所以必须锁在 .ant-modal 里，否则填的是表格上面那份表单。
 */
function modalField(id: string) {
  const body = document.querySelector('.ant-modal-body') as HTMLElement;
  return body.querySelector(`#${id}`) as HTMLInputElement;
}

function fill(id: string, value: string) {
  fireEvent.change(modalField(id), { target: { value } });
}

beforeEach(() => {
  vi.clearAllMocks();
  mocks.query = new URLSearchParams('');
  mocks.getBooks.mockResolvedValue({
    data: { content: [{ id: 7, title: '代码之隙' }], totalElements: 1 },
  });
  mocks.getChapters.mockResolvedValue({
    data: [
      {
        id: 55,
        bookId: 7,
        chapterIndex: 3,
        title: '第三章',
        wordCount: 10,
        status: 'committed',
        revision: 2,
      },
    ],
  });
  mocks.getFindings.mockResolvedValue({
    data: { content: [findingRow], totalElements: 1 },
  });
  mocks.getCanon.mockResolvedValue({
    data: { content: [canonRow], totalElements: 1 },
  });
  mocks.getCanonConflicts.mockResolvedValue({ data: [] });
  mocks.getChapter.mockResolvedValue({ data: chapterRow });
  mocks.createCanon.mockResolvedValue({ data: canonRow });
  mocks.updateCanon.mockResolvedValue({ data: canonRow });
  mocks.adjudicateFinding.mockResolvedValue({ data: { status: 'rejected' } });
});

describe('设定面板 · 写入前的冲突预览', () => {
  it('列表按 0 基页码取第一页', async () => {
    renderWithQuery(<CanonPanel bookId={7} />);
    await waitFor(() => expect(mocks.getCanon).toHaveBeenCalled());
    expect(mocks.getCanon).toHaveBeenCalledWith(
      7,
      expect.objectContaining({ page: 0 }),
    );
  });

  it('新增设定时不带 excludeId（还没有「自己」可排除）', async () => {
    renderWithQuery(<CanonPanel bookId={7} />);
    fireEvent.click(screen.getByRole('button', { name: /新增设定/ }));
    fill('subjectKey', 'char:shenqing');
    fill('predicate', 'eye_color');
    fill('objectText', '灰蓝色');
    fireEvent.click(screen.getByRole('button', { name: /保存为作者设定/ }));

    await waitFor(() => expect(mocks.getCanonConflicts).toHaveBeenCalled());
    expect(mocks.getCanonConflicts).toHaveBeenCalledWith(
      7,
      expect.objectContaining({
        subjectKey: 'char:shenqing',
        objectText: '灰蓝色',
      }),
    );
    expect(mocks.getCanonConflicts.mock.calls[0][1].excludeId).toBeUndefined();
    // 预览没有撞车就直接落库，不让作者多点一次确认
    await waitFor(() => expect(mocks.createCanon).toHaveBeenCalled());
  });

  it('编辑已有设定时把自己排除在撞车之外', async () => {
    renderWithQuery(<CanonPanel bookId={7} />);
    await waitFor(() => expect(screen.getByText('编辑')).toBeInTheDocument());
    fireEvent.click(screen.getByText('编辑'));
    fireEvent.click(screen.getByRole('button', { name: /保存为作者设定/ }));

    await waitFor(() => expect(mocks.getCanonConflicts).toHaveBeenCalled());
    expect(mocks.getCanonConflicts.mock.calls[0][1].excludeId).toBe(41);
    await waitFor(() => expect(mocks.updateCanon).toHaveBeenCalled());
  });

  it('撞车时不落库，把旧条目摆给作者看', async () => {
    mocks.getCanonConflicts.mockResolvedValue({ data: [canonRow] });
    renderWithQuery(<CanonPanel bookId={7} />);
    fireEvent.click(screen.getByRole('button', { name: /新增设定/ }));
    fill('subjectKey', 'char:shenqing');
    fill('predicate', 'eye_color');
    fill('objectText', '灰蓝色');
    fireEvent.click(screen.getByRole('button', { name: /保存为作者设定/ }));

    await waitFor(() =>
      expect(screen.getAllByText(/同主同谓的已生效设定条目有/).length),
    );
    expect(mocks.createCanon).not.toHaveBeenCalled();
  });
});

describe('冲突台账 · 筛选与裁定', () => {
  it('单书面板按 0 基页码取台账，并读章节列表做「按章筛」', async () => {
    renderWithQuery(<FindingTable bookId={7} />);
    await waitFor(() => expect(mocks.getFindings).toHaveBeenCalled());
    expect(mocks.getFindings).toHaveBeenCalledWith(
      expect.objectContaining({ bookId: 7, page: 0 }),
    );
    expect(mocks.getChapters).toHaveBeenCalledWith(7);
  });

  it('跨书台账不读某本书的章节列表（章号会串书）', async () => {
    renderWithQuery(<FindingTable />);
    await waitFor(() => expect(mocks.getFindings).toHaveBeenCalled());
    expect(mocks.getChapters).not.toHaveBeenCalled();
  });

  it('选章后台账带 chapterId 重查', async () => {
    renderWithQuery(<FindingTable bookId={7} />);
    await waitFor(() => expect(mocks.getFindings).toHaveBeenCalled());
    // antd 6 的下拉没有 .ant-select-selector 了，控件本体是表单里带字段 id 的 combobox 输入框
    fireEvent.mouseDown(document.querySelector('#chapterId') as HTMLElement);
    // 选项的内外两层 textContent 相同，findAllByText 取内层再点，事件照样冒泡到选项本体
    const optionNodes = await screen.findAllByText('第 3 章 第三章');
    fireEvent.click(optionNodes[optionNodes.length - 1] as HTMLElement);
    fireEvent.click(screen.getByRole('button', { name: /^查\s*询$/ }));
    await waitFor(() =>
      expect(mocks.getFindings).toHaveBeenCalledWith(
        expect.objectContaining({ chapterId: 55 }),
      ),
    );
  });

  it('台账点章节落在创作台的这一章，而不是没有章坐标系的详情页', async () => {
    renderWithQuery(<FindingTable bookId={7} />);
    await waitFor(() =>
      expect(screen.getByText('第 3 章 第三章')).toBeInTheDocument(),
    );
    fireEvent.click(screen.getByText('第 3 章 第三章'));
    expect(mocks.push).toHaveBeenCalledWith(
      '/novel/book/7/studio?chapterId=55',
    );
  });

  it('采纳后失效设定缓存，创作台中栏重新取这一章的断言', async () => {
    // 消费方选中栏 CenterPanel 而不是「设定」Tab 的 CanonPanel：CanonPanel 的列表走
    // ProTable 的 request，不在 React Query 缓存里，只有中栏的 ['novel-canon', bookId, 'source', …]
    // 是真的挂在这份缓存上，失效了才会重发请求。
    // 两处渲染在同一个 QueryClient 上，就是作者在同一屏里看到的「台账 + 本章设定」。
    renderWithQuery(
      <>
        <CenterPanel
          bookId={7}
          chapterId={55}
          focusCanon={null}
          onSaved={() => {}}
        />
        <FindingTable bookId={7} />
      </>,
    );
    await waitFor(() =>
      expect(mocks.getCanon).toHaveBeenCalledWith(
        7,
        expect.objectContaining({ sourceChapterId: 55 }),
      ),
    );
    await waitFor(() => expect(screen.getByText('裁定')).toBeInTheDocument());
    const before = mocks.getCanon.mock.calls.filter(
      (args) => args[1]?.sourceChapterId === 55,
    ).length;

    fireEvent.click(screen.getByText('裁定'));
    fill('subjectKey', 'char:shenqing');
    fill('predicate', 'eye_color');
    fill('objectText', '灰蓝色');
    fireEvent.click(screen.getByRole('button', { name: /提交裁定/ }));

    await waitFor(() =>
      expect(mocks.adjudicateFinding).toHaveBeenCalledWith(
        12,
        expect.objectContaining({ action: 'adopt' }),
      ),
    );
    // 采纳写的就是 canon_entry（插一条新的 + 闭掉被违反的旧区间）：不失效 novel-canon
    // 就会出现「台账说已采纳、本章设定卡还停在采纳前」那种假象
    await waitFor(() =>
      expect(
        mocks.getCanon.mock.calls.filter(
          (args) => args[1]?.sourceChapterId === 55,
        ).length,
      ).toBeGreaterThan(before),
    );
  });

  it('驳回必须带理由，且理由原样进裁定请求', async () => {
    renderWithQuery(<FindingTable bookId={7} />);
    await waitFor(() => expect(screen.getByText('裁定')).toBeInTheDocument());
    fireEvent.click(screen.getByText('裁定'));
    fireEvent.click(screen.getByText('驳回（冲突不成立）'));
    fireEvent.click(screen.getByRole('button', { name: /提交裁定/ }));
    // 没填理由不该发请求（服务端也要求 basis，前端先拦住）
    await waitFor(() =>
      expect(screen.getByText('请填写理由')).toBeInTheDocument(),
    );
    expect(mocks.adjudicateFinding).not.toHaveBeenCalled();

    fireEvent.change(document.getElementById('basis') as HTMLTextAreaElement, {
      target: { value: '闸门把别名当成了两个实体' },
    });
    fireEvent.click(screen.getByRole('button', { name: /提交裁定/ }));
    await waitFor(() => expect(mocks.adjudicateFinding).toHaveBeenCalled());
    expect(mocks.adjudicateFinding).toHaveBeenCalledWith(12, {
      action: 'reject',
      basis: '闸门把别名当成了两个实体',
      assertion: undefined,
    });
  });
});

describe('冲突台账页 · ?bookId= 深链', () => {
  it('带 bookId 时台账收窄到这本书', async () => {
    mocks.query = new URLSearchParams('bookId=7');
    renderWithQuery(<NovelReviewList />);
    await waitFor(() => expect(mocks.getFindings).toHaveBeenCalled());
    expect(mocks.getFindings).toHaveBeenCalledWith(
      expect.objectContaining({ bookId: 7 }),
    );
    // 收窄后就不该再拉全站的书籍列表
    expect(mocks.getBooks).not.toHaveBeenCalled();
  });

  it('不带 bookId 时是跨书台账', async () => {
    renderWithQuery(<NovelReviewList />);
    await waitFor(() => expect(mocks.getFindings).toHaveBeenCalled());
    expect(mocks.getFindings.mock.calls[0][0].bookId).toBeUndefined();
    expect(mocks.getBooks).toHaveBeenCalled();
  });
});
