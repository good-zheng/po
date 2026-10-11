import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import type { ReactNode } from 'react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

/**
 * 章节管理的「待写占位」回归用例。
 *
 * 钉住两件只有界面能坏掉的事：
 * ①新建章节不必填标题——标题留空由服务端落成「第 N 章」，序号留空排在最后一章之后，
 *   作者想「先占个位，回头让链路按已有设定发挥」时不该被前端拦在门外；
 * ②正文为空的行要标成「待写」，否则作者看不出哪一章是排期、哪一章已定稿。
 */

const mocks = vi.hoisted(() => ({
  getChapters: vi.fn(),
  createChapter: vi.fn(),
  updateChapter: vi.fn(),
  deleteChapter: vi.fn(),
}));

vi.mock('@/services/novel', () => ({
  getChapters: mocks.getChapters,
  createChapter: mocks.createChapter,
  updateChapter: mocks.updateChapter,
  deleteChapter: mocks.deleteChapter,
}));

import ChapterManager from './ChapterManager';

const written = (id: number, chapterIndex: number) => ({
  id,
  bookId: 7,
  chapterIndex,
  title: `第 ${chapterIndex} 章`,
  content: '正文若干',
  wordCount: 1200,
  status: 'committed',
  revision: 2,
});

const placeholder = {
  id: 74,
  bookId: 7,
  chapterIndex: 4,
  title: '第 4 章',
  content: null,
  wordCount: 0,
  status: 'draft',
  revision: 1,
};

function renderWithQuery(ui: ReactNode) {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });
  return render(
    <QueryClientProvider client={client}>{ui}</QueryClientProvider>,
  );
}

function modal() {
  return document.querySelector('.ant-modal-body') as HTMLElement;
}

function fill(id: string, value: string) {
  fireEvent.change(modal().querySelector(`#${id}`) as HTMLInputElement, {
    target: { value },
  });
}

const submitButton = () => screen.getByRole('button', { name: /保\s*存/ });

beforeEach(() => {
  vi.clearAllMocks();
  mocks.getChapters.mockResolvedValue({
    data: [written(71, 1), written(72, 2), written(73, 3)],
  });
  mocks.createChapter.mockResolvedValue({ data: placeholder });
  mocks.updateChapter.mockResolvedValue({ data: placeholder });
});

describe('ChapterManager · 待写占位', () => {
  it('标题留空也能提交，序号默认排在最后一章之后', async () => {
    renderWithQuery(<ChapterManager bookId={7} />);
    // 先等章树落地：序号预填取的是「最后一章 + 1」，数据没回来时它只能算出 1
    await waitFor(() => expect(screen.getByText('第 3 章')).toBeTruthy());
    fireEvent.click(screen.getByRole('button', { name: /新建章节/ }));
    await waitFor(() => expect(modal()).toBeTruthy());
    expect(
      (modal().querySelector('#chapterIndex') as HTMLInputElement).value,
    ).toBe('4');

    fireEvent.click(submitButton());
    await waitFor(() => expect(mocks.createChapter).toHaveBeenCalledTimes(1));
    const body = mocks.createChapter.mock.calls[0][1] as Record<
      string,
      unknown
    >;
    // 空标题不发给服务端假值：落成「第 N 章」是服务端的唯一口径
    expect(body.title ? String(body.title).trim() : '').toBe('');
    expect(body.chapterIndex).toBe(4);
  });

  it('新建表单先把「留空即占位」说在前面', async () => {
    renderWithQuery(<ChapterManager bookId={7} />);
    fireEvent.click(screen.getByRole('button', { name: /新建章节/ }));
    await waitFor(() => expect(modal()).toBeTruthy());
    expect(mocks.createChapter).not.toHaveBeenCalled();
    const content = modal().querySelector('#content') as HTMLTextAreaElement;
    expect(content.placeholder).toContain('待写占位');
  });

  it('正文为空的行标成「待写」，有正文的不标', async () => {
    mocks.getChapters.mockResolvedValue({
      data: [written(71, 1), written(72, 2), written(73, 3), placeholder],
    });
    renderWithQuery(<ChapterManager bookId={7} />);
    await waitFor(() =>
      expect(screen.getAllByText('第 4 章').length).toBeGreaterThan(0),
    );
    expect(screen.getAllByText('待写')).toHaveLength(1);
  });

  it('编辑时清空标题不再被必填拦住', async () => {
    mocks.getChapters.mockResolvedValue({
      data: [written(71, 1), placeholder],
    });
    renderWithQuery(<ChapterManager bookId={7} />);
    await waitFor(() =>
      expect(screen.getAllByText('第 4 章').length).toBeGreaterThan(0),
    );
    // 标题列是 Typography.Link（无 href，不算 link 角色），点文本节点即冒泡到它的 onClick
    fireEvent.click(screen.getByText('第 4 章'));
    await waitFor(() => expect(modal()).toBeTruthy());
    fill('title', '');
    fireEvent.click(submitButton());
    await waitFor(() => expect(mocks.updateChapter).toHaveBeenCalledTimes(1));
    expect(mocks.updateChapter.mock.calls[0][1]).toBe(74);
  });
});
