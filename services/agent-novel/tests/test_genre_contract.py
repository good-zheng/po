"""题材字典的两侧对齐与归一口径。

``schemas.GENRES`` 是 Java ``NovelGenres`` 的镜像，镜像会漂：#44 那次是库里先漂了
（写 label 也能存，筛选按 value 查就凭空少一本），这次是真机跑通三章后被
「无效的小说类型」挡在归档最后一步。所以这里钉两件事——
字典逐条对齐 java 源文件，以及中文原话怎么收敛成 value。
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from po_agent_novel.schemas import GENRES, genre_label, normalize_genre

GENRES_JAVA = (
    Path(__file__).resolve().parents[3]
    / "services/api/novel/src/main/java/com/goodzheng/po/novel/constant/NovelGenres.java"
)


def test_python_genres_mirror_java_dictionary() -> None:
    pairs = re.findall(
        r'new GenreOption\("([^"]+)",\s*"([^"]+)"\)', GENRES_JAVA.read_text(encoding="utf-8")
    )
    assert pairs, f"没从 {GENRES_JAVA.name} 里读到 GenreOption，解析式该修了"
    assert list(pairs) == list(GENRES)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("玄幻", "fantasy"),
        ("其他", "other"),
        ("scifi", "scifi"),  # 已经是 value：原样过，不做二次映射
        ("都市科幻", "scifi"),  # 复合词取中心词（最后一个字典词）
        ("科幻都市", "urban"),
        ("都市科幻（都市异能+赛博救世）", "scifi"),  # 括号说明不参与取词
        ("都市悬疑", "mystery"),
        ("赛博朋克", "other"),  # 对不上字典落「其他」，它是能筛的真实分类
        ("", "other"),
        ("   ", "other"),
    ],
)
def test_normalize_genre(raw: str, expected: str) -> None:
    assert normalize_genre(raw) == expected


def test_genre_label_only_translates_known_values() -> None:
    assert genre_label("scifi") == "科幻"
    # 认不出的原样返回：读侧展示映射没有资格改数据（历史脏行、Mock 里的中文都在这档）
    assert genre_label("玄幻") == "玄幻"
    assert genre_label("") == ""
