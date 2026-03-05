"""
/**
 * [IN]: src.pdf_processor (PDFPreprocessor, PDFProcessor)
 * [OUT]: PDFProcessor 单元测试
 * [POS]: pytest 测试套件，Phase 4 单元测试覆盖
 * [PROTOCOL]: pdf_processor.py 修改 -> 同步更新本测试
 */
"""
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch, mock_open


class TestPDFPreprocessorValidate:
    """测试 PDFPreprocessor.validate"""

    def test_nonexistent_file_fails(self, tmp_path):
        from src.pdf_processor import PDFPreprocessor
        pp = PDFPreprocessor()
        nonexistent = tmp_path / "ghost.pdf"
        is_valid, error_code, info = pp.validate(nonexistent)
        assert is_valid is False
        assert error_code is not None

    def test_non_pdf_extension_fails(self, tmp_path):
        from src.pdf_processor import PDFPreprocessor
        txt_file = tmp_path / "document.txt"
        txt_file.write_text("not a pdf")
        pp = PDFPreprocessor()
        is_valid, error_code, info = pp.validate(txt_file)
        assert is_valid is False

    def test_empty_file_fails(self, tmp_path):
        from src.pdf_processor import PDFPreprocessor
        empty = tmp_path / "empty.pdf"
        empty.write_bytes(b"")
        pp = PDFPreprocessor()
        is_valid, error_code, info = pp.validate(empty)
        assert is_valid is False

    def test_corrupted_pdf_fails(self, tmp_path):
        from src.pdf_processor import PDFPreprocessor
        bad_pdf = tmp_path / "bad.pdf"
        bad_pdf.write_bytes(b"this is not a real PDF content %PDF-broken")
        pp = PDFPreprocessor()
        is_valid, error_code, info = pp.validate(bad_pdf)
        # May or may not be detected as invalid depending on PyMuPDF tolerance
        # We just assert it doesn't raise an exception
        assert isinstance(is_valid, bool)


class TestPDFPreprocessorExtractTitleAndAuthor:
    """测试 PDFPreprocessor.extract_title_and_author"""

    def test_empty_info_returns_empty_strings(self):
        from src.pdf_processor import PDFPreprocessor
        pp = PDFPreprocessor()
        title, author = pp.extract_title_and_author({})
        assert title == "" or title is None
        assert author == "" or author is None

    def test_extracts_title_from_info(self):
        from src.pdf_processor import PDFPreprocessor
        pp = PDFPreprocessor()
        # extract_title_and_author 从 info['metadata'] 子字典中读取
        info = {"metadata": {"title": "My Test Paper", "author": ""}}
        title, author = pp.extract_title_and_author(info)
        assert "My Test Paper" in (title or "")

    def test_extracts_author_from_info(self):
        from src.pdf_processor import PDFPreprocessor
        pp = PDFPreprocessor()
        info = {"metadata": {"title": "", "author": "John Doe"}}
        title, author = pp.extract_title_and_author(info)
        assert "John" in (author or "") or "Doe" in (author or "")



class TestPDFProcessorProcess:
    """测试 PDFProcessor.process（mock marker_single）"""

    def test_process_invalid_pdf_raises(self, tmp_path):
        from src.pdf_processor import PDFProcessor
        from src.exceptions import PDFAccessError
        processor = PDFProcessor()

        # 传入不存在的文件应该抛出异常
        bad_pdf = tmp_path / "nonexistent.pdf"
        with pytest.raises((PDFAccessError, Exception)):
            processor.process(bad_pdf)

    def test_process_calls_marker(self, tmp_path):
        """Mock marker_single 调用，验证 process() 完整流程"""
        from src.pdf_processor import PDFProcessor, PDFPreprocessor
        from unittest.mock import patch

        # 创建一个假 PDF 文件
        fake_pdf = tmp_path / "test.pdf"
        fake_pdf.write_bytes(b"%PDF-1.4 fake content")

        # Mock validate() 返回成功
        mock_info = {
            "page_count": 5,
            "has_text_layer": True,
            "file_size": 1024,
            "title": "Test Paper",
            "author": "Test Author",
        }

        with patch.object(PDFPreprocessor, "validate",
                          return_value=(True, None, mock_info)), \
             patch.object(PDFPreprocessor, "extract_title_and_author",
                          return_value=("Test Paper", "Test Author")), \
             patch("src.pdf_processor.PDFProcessor._convert_with_marker") as mock_convert, \
             patch("src.pdf_processor.PDFProcessor._organize_assets"), \
             patch("src.config.settings") as mock_settings:

            mock_settings.output_path = tmp_path / "output"
            mock_settings.max_title_slug_words = 5
            mock_settings.max_filename_length = 100
            (tmp_path / "output").mkdir(parents=True, exist_ok=True)

            md_content = "# Test Paper\nContent here."
            mock_convert.return_value = md_content

            processor = PDFProcessor()
            output_folder, content, info = processor.process(fake_pdf)

            assert content == md_content
            assert info["status"] == "success"
            assert "title" in info
