package com.goodzheng.po.novel.service;

import com.goodzheng.po.novel.dto.SearchResultsView;
import org.springframework.data.domain.Pageable;

import java.util.List;

/**
 * 左栏统一检索（§10.3「构思时快速回查『第 12 章她到底说了什么』」）。
 *
 * <p>一期用 MySQL {@code LIKE} + 别名表展开，不引 ES（§10.7 的「那是第二个基建决策，成本比
 * 整条 N5 大」）。这里的价值不在全文索引，而在<b>一次查询同时穿过三张表</b>：查到断言时
 * 顺带把「阿青」展开成 {@code char:qing} 再去匹配 subject_key，作者不必先想清楚这个称谓属于谁。
 */
public interface NovelSearchService {

    /**
     * @param scopes 需要的检索面，合法值 chapter/canon/alias；空则三者都查。
     *               非法值直接忽略，不报错——左栏的勾选框加一个旧前端不认识的 scope 时，
     *               检索不该整块挂掉。书不存在时三节皆空，不抛异常。
     */
    SearchResultsView search(Long bookId, String query, List<String> scopes, Pageable pageable);
}
