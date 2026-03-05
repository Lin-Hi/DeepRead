"""
/**
 * [IN]: src.utils (normalize_filename, compute_file_hash, format_citekey, etc.)
 * [OUT]: utils 模块单元测试
 * [POS]: pytest 测试套件，Phase 4 单元测试覆盖
 * [PROTOCOL]: utils.py 新增函数 -> 同步添加对应测试用例
 */
"""
import hashlib
import tempfile
from pathlib import Path

import pytest

from src.utils import (
    compute_file_hash,
    format_citekey,
    normalize_filename,
    sanitize_path_component,
    truncate_text,
    estimate_token_count,
    get_unique_folder_name,
)


# ─── normalize_filename ──────────────────────────────────────────────────────

class TestNormalizeFilename:
    def test_standard_input(self):
        result = normalize_filename(
            title="Serverless Computing A Survey",
            year="2026",
            first_author="John Smith"
        )
        assert result.startswith("2026")
        assert "Smith" in result
        assert "Serverless" in result

    def test_empty_title(self):
        result = normalize_filename(title="", year="2024", first_author="Alice Wang")
        assert "2024" in result
        assert "Wang" in result

    def test_empty_author(self):
        result = normalize_filename(
            title="Deep Learning Basics", year="2023", first_author=""
        )
        assert "2023" in result
        assert "DeepLearning" in result or "Deep" in result

    def test_all_empty(self):
        result = normalize_filename(title="", year="", first_author="")
        assert result == ""

    def test_special_characters_removed(self):
        result = normalize_filename(
            title='Paper: On "Quotes" & <Symbols>',
            year="2025",
            first_author="Li Wei"
        )
        assert "<" not in result
        assert ">" not in result
        assert '"' not in result

    def test_max_length_respected(self):
        long_title = "A" * 200
        result = normalize_filename(title=long_title, year="2024", first_author="Bob")
        assert len(result) <= 100


# ─── compute_file_hash ───────────────────────────────────────────────────────

class TestComputeFileHash:
    def test_returns_string(self, tmp_path):
        test_file = tmp_path / "test.pdf"
        test_file.write_bytes(b"hello world")
        result = compute_file_hash(test_file)
        assert isinstance(result, str)
        assert len(result) == 16  # 取前16位

    def test_same_content_same_hash(self, tmp_path):
        f1 = tmp_path / "a.pdf"
        f2 = tmp_path / "b.pdf"
        f1.write_bytes(b"identical content")
        f2.write_bytes(b"identical content")
        assert compute_file_hash(f1) == compute_file_hash(f2)

    def test_different_content_different_hash(self, tmp_path):
        f1 = tmp_path / "a.pdf"
        f2 = tmp_path / "b.pdf"
        f1.write_bytes(b"content A")
        f2.write_bytes(b"content B")
        assert compute_file_hash(f1) != compute_file_hash(f2)

    def test_empty_file(self, tmp_path):
        f = tmp_path / "empty.pdf"
        f.write_bytes(b"")
        result = compute_file_hash(f)
        assert isinstance(result, str)
        assert len(result) == 16


# ─── format_citekey ──────────────────────────────────────────────────────────

class TestFormatCitekey:
    def test_standard(self):
        result = format_citekey("John Smith", "Deep Learning Overview", "2024")
        assert "Smith" in result
        assert "2024" in result
        assert "Deep" in result

    def test_empty_author(self):
        result = format_citekey("", "Some Title", "2023")
        assert "2023" in result

    def test_empty_all(self):
        result = format_citekey("", "", "")
        assert result == "Unknown"

    def test_no_spaces_in_result(self):
        result = format_citekey("Alice Chen", "My Paper Title", "2025")
        assert " " not in result


# ─── sanitize_path_component ─────────────────────────────────────────────────

class TestSanitizePathComponent:
    def test_removes_windows_illegal_chars(self):
        result = sanitize_path_component('file<>:"/\\|?*name')
        for char in '<>:"/\\|?*':
            assert char not in result

    def test_strips_leading_trailing_dots_spaces(self):
        result = sanitize_path_component("  .test file.  ")
        assert not result.startswith(" ")
        assert not result.startswith(".")

    def test_length_limit(self):
        long_name = "a" * 150
        result = sanitize_path_component(long_name)
        assert len(result) <= 100

    def test_normal_name_unchanged(self):
        result = sanitize_path_component("normal_filename_2024")
        assert result == "normal_filename_2024"


# ─── truncate_text ───────────────────────────────────────────────────────────

class TestTruncateText:
    def test_short_text_unchanged(self):
        assert truncate_text("hello", 100) == "hello"

    def test_long_text_truncated(self):
        result = truncate_text("a" * 200, 50)
        assert len(result) == 50
        assert result.endswith("...")

    def test_custom_suffix(self):
        result = truncate_text("hello world", 8, suffix="…")
        assert result.endswith("…")
        assert len(result) == 8

    def test_exact_length_unchanged(self):
        text = "hello"
        assert truncate_text(text, 5) == text


# ─── estimate_token_count ────────────────────────────────────────────────────

class TestEstimateTokenCount:
    def test_english_text(self):
        count = estimate_token_count("hello world foo bar")
        assert count == 4  # 4 英文单词

    def test_chinese_text(self):
        count = estimate_token_count("你好世界")
        assert count == 8  # 4 个汉字 * 2

    def test_empty_string(self):
        assert estimate_token_count("") == 0

    def test_mixed_text(self):
        count = estimate_token_count("hello 世界")
        assert count > 0


# ─── get_unique_folder_name ──────────────────────────────────────────────────

class TestGetUniqueFolderName:
    def test_no_conflict(self, tmp_path):
        result = get_unique_folder_name("my_folder", tmp_path)
        assert result == "my_folder"

    def test_conflict_adds_suffix(self, tmp_path):
        (tmp_path / "my_folder").mkdir()
        result = get_unique_folder_name("my_folder", tmp_path)
        assert result != "my_folder"
        assert "my_folder" in result

    def test_multiple_conflicts(self, tmp_path):
        (tmp_path / "paper").mkdir()
        (tmp_path / "paper_001").mkdir()
        result = get_unique_folder_name("paper", tmp_path)
        assert result == "paper_002"
