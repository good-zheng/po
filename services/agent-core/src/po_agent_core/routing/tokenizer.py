"""字符级 tokenizer（semantic-router BM25Encoder 稀疏编码用）。

semantic-router 默认的 ``PretrainedTokenizer`` 需要从 HuggingFace 下载
BERT 权重（网络依赖 + 磁盘开销），且 BERT 词表对中文并不友好。
中文路由语料以字符为最小语义单位，字符级 BM25 是标准做法，
因此这里提供一个纯本地、确定性的字符哈希 tokenizer：

- id 0 保留为 padding/unknown；
- 每个字符哈希到 ``[1, vocab_size)``，vocab 大小固定，
  fit 与 query 阶段无需重建词表，杜绝形状漂移。
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

from semantic_router.tokenizers import BaseTokenizer

_PAD_ID = 0


class CharTokenizer(BaseTokenizer):
    def __init__(self, vocab_size: int = 8192) -> None:
        super().__init__()
        if vocab_size < 2:
            raise ValueError("vocab_size must be >= 2")
        self._vocab_size = vocab_size

    @property
    def vocab_size(self) -> int:
        return self._vocab_size

    @property
    def config(self) -> dict[str, Any]:
        return {"vocab_size": self._vocab_size}

    def save(self, path: str | Path) -> None:
        if isinstance(path, str):
            path = Path(path)
        with path.open("w", encoding="utf-8") as fp:
            json.dump(self.config, fp)

    @classmethod
    def load(cls, path: str | Path) -> CharTokenizer:
        if isinstance(path, str):
            path = Path(path)
        with path.open(encoding="utf-8") as fp:
            config = json.load(fp)
        return cls(**config)

    def _char_id(self, char: str) -> int:
        """字符 → 词表 id 的稳定哈希映射。

        同一字符在任何进程、任何批次都得到同一 id（sha256 取前 4 字节），
        这是 BM25 词频统计可复现的前提；取模落在 [1, vocab_size)，
        因为 0 被保留给 padding/unknown。
        """
        digest = hashlib.sha256(char.encode("utf-8")).digest()
        return int.from_bytes(digest[:4], "big") % (self._vocab_size - 1) + 1

    def tokenize(
        self, texts: str | list[str], pad: bool = True
    ) -> np.ndarray:
        """把文本转为 ``(n_docs, max_len)`` 的字符 id 矩阵。

        ``pad=True`` 时短文档以 0 右填充到批内最长；空串文档至少占一列 0，
        保证输出恒为二维矩阵（BM25Encoder 的 ``_tf`` 依赖此形状）。
        """
        if isinstance(texts, str):
            texts = [texts]
        if not texts:
            return np.zeros((0, 1), dtype=np.int64)
        encoded = [
            [self._char_id(ch) for ch in text if not ch.isspace()] for text in texts
        ]
        if pad:
            max_len = max((len(ids) for ids in encoded), default=1)
            rows = [ids + [_PAD_ID] * (max_len - len(ids)) for ids in encoded]
        else:
            rows = encoded
        return np.array(rows, dtype=np.int64)
