import numpy as np
import pytest

from po_agent_core.routing.tokenizer import CharTokenizer


def test_tokenize_pads_to_batch_max_len() -> None:
    tokenizer = CharTokenizer(vocab_size=64)
    matrix = tokenizer.tokenize(["abcd", "ab"])
    assert matrix.shape == (2, 4)
    assert matrix.dtype == np.int64
    # 两个文档共享前缀字符 → 前 2 列 id 相同，短文档后 2 列为 0（padding）
    assert matrix[0, 0] == matrix[1, 0]
    assert matrix[0, 1] == matrix[1, 1]
    assert matrix[1, 2] == 0
    assert matrix[1, 3] == 0


def test_tokenize_single_string_and_empty_list() -> None:
    tokenizer = CharTokenizer(vocab_size=64)
    assert tokenizer.tokenize("abc").shape == (1, 3)
    assert tokenizer.tokenize([]).shape == (0, 1)


def test_tokenize_empty_string_row_is_all_padding() -> None:
    tokenizer = CharTokenizer(vocab_size=64)
    matrix = tokenizer.tokenize(["", "ab"])
    assert matrix.shape == (2, 2)
    assert (matrix[0] == 0).all()


def test_tokenize_filters_whitespace_and_is_deterministic() -> None:
    tokenizer = CharTokenizer(vocab_size=64)
    a = tokenizer.tokenize(["你 好\t世界"], pad=False)
    b = tokenizer.tokenize(["你好世界"], pad=False)
    np.testing.assert_array_equal(a, b)
    # 空白被过滤后应与无空白文本等长
    assert a.shape == (1, 4)


def test_ids_within_vocab_range_and_nonzero() -> None:
    tokenizer = CharTokenizer(vocab_size=8)
    matrix = tokenizer.tokenize(["中文路由测试" * 20], pad=False)
    assert matrix.size
    assert (matrix >= 1).all()
    assert (matrix < 8).all()


def test_invalid_vocab_size_rejected() -> None:
    with pytest.raises(ValueError):
        CharTokenizer(vocab_size=1)


def test_save_load_roundtrip(tmp_path) -> None:
    tokenizer = CharTokenizer(vocab_size=128)
    path = tmp_path / "tokenizer.json"
    tokenizer.save(path)
    loaded = CharTokenizer.load(path)
    assert loaded.vocab_size == 128
    np.testing.assert_array_equal(
        tokenizer.tokenize(["一致性校验"], pad=False),
        loaded.tokenize(["一致性校验"], pad=False),
    )
