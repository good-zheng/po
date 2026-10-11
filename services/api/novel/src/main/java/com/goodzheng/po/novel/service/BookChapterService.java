package com.goodzheng.po.novel.service;

import com.goodzheng.po.novel.dto.ChapterRequest;
import com.goodzheng.po.novel.entity.BookChapter;

import java.util.List;

public interface BookChapterService {

    List<BookChapter> list(Long bookId);

    /**
     * 未删除章节数（管理端列表与字数台账用）。
     *
     * <p>单独一条 count 而不是 {@code list(bookId).size()}：一书的正文加起来是百 KB 量级，
     * 而这里只要一个数字。
     *
     * <p>注意它<b>包含</b>正文为空的占位章，因此不能当续写游标——那条读数在
     * {@link #countWrittenByBook}。
     */
    int countByBook(Long bookId);

    /**
     * 有正文的章节数，即续写链路的游标（本轮从「该数 + 1」章起往后追加）。
     *
     * <p>与 {@link #countByBook} 分开的理由是那一行占位章：作者在新建章节里留空标题与正文
     * 排下的「待写」行如果进游标，续写会跳过它往后写，那一章就永久空着，而衔接用的
     * 「上一章结尾」也会读成空串。占位行因此不进游标，等着被 {@link #putByIndex} 就地填掉。
     */
    int countWrittenByBook(Long bookId);

    BookChapter get(Long bookId, Long chapterId);

    /** 手工建章：永远新插一行（章节序号重复由作者自己负责，管理端不在此处拦）。 */
    BookChapter create(Long bookId, ChapterRequest request);

    /**
     * 生成链路的写章入口：按章号落位——同号是占位章就把它填掉，同号已有正文就报错。
     *
     * <p>为什么不复用 {@link #create}：内网写口逐条 insert，续写第二轮会为「第 4 章」再插一行，
     * 于是同一章号有两行、占位章永久空着。为什么不在这里覆盖：已定稿正文的出处是正典断言的
     * 溯源键，静默改写等于把整本书的事实指向一份不再存在的正文。宁可让这一轮红着结束。
     *
     * @param userId 内网调用方带来的人类身份（{@code X-Actor-Uid}），生成链路通常没有终端
     *               用户在场所传 {@code null}；它只进 {@code chapter_revision.created_by}
     */
    BookChapter putByIndex(Long bookId, ChapterRequest request, Long userId);

    /**
     * 唯一的正文写路径：改完必须连带重算（§10.5-③），所以重定位、快照、状态退回都在这一个方法里，
     * 任何入口都没有「只存正文」的选项。
     *
     * @param userId 作者 ID，写进 {@code chapter_revision.created_by}
     */
    BookChapter update(Long bookId, Long chapterId, ChapterRequest request, Long userId);

    void delete(Long bookId, Long chapterId);
}
