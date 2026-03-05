"""
/**
 * [IN]: pytest, unittest.mock, pathlib, src.main.process_single_pdf, src.exceptions.DeepReadError
 * [OUT]: 测试端到端工作流（E2E Workflow），模拟主干流程与异常拦截
 * [POS]: 在 tests 目录下，由自动化测试触发
 * [PROTOCOL]: 更改主流程编排或输出规则 -> 必须同步更改本文件的行为断言
 */
"""
import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
from src.main import process_single_pdf
from src.exceptions import DeepReadError, PDFAccessError, LLMRequestError

def test_e2e_successful_workflow(temp_output_dir):
    """测试常规处理成功的工作流断言"""
    mock_pdf_processor = MagicMock()
    mock_summarizer = MagicMock()
    mock_canvas_builder = MagicMock()
    mock_state_tracker = MagicMock()

    # 设置依赖行为
    mock_pdf_processor.validate_pdf.return_value = (True, "")
    mock_pdf_processor.extract_metadata.return_value = {
        "title": "Test Title", "year": "2023", "first_author": "John"
    }
    mock_pdf_processor.convert_to_markdown.return_value = "# Abstract\nContent..."
    mock_summarizer.generate_summary.return_value = "citekey: John2023\n..."
    mock_state_tracker.compute_file_hash.return_value = "fakehash123"
    mock_state_tracker.get_file_record.return_value = None

    pdf_path = Path("fake_dir/test_document.pdf")
    
    with patch("src.main.settings") as mock_settings:
        mock_settings.output_path = temp_output_dir
        mock_settings.root_dir = temp_output_dir  # 保持属于同一驱动器层级
        
        success, msg = process_single_pdf(
            pdf_path,
            mock_pdf_processor,
            mock_summarizer,
            mock_canvas_builder,
            mock_state_tracker
        )

    assert success is True
    assert msg == "success"
    mock_pdf_processor.convert_to_markdown.assert_called_once()
    mock_summarizer.generate_summary.assert_called_once()
    mock_canvas_builder.create_paper_canvas.assert_called_once()
    mock_state_tracker.update_file_record.assert_called_once()

def test_e2e_pdf_validation_failure(temp_output_dir):
    """测试 PDF 验证失败情况（如损坏保护）"""
    mock_pdf_processor = MagicMock()
    mock_state_tracker = MagicMock()
    
    mock_pdf_processor.validate_pdf.return_value = (False, "ERR_PDF_CORRUPTED")
    mock_state_tracker.get_file_record.return_value = None

    success, msg = process_single_pdf(
        Path("broken.pdf"),
        mock_pdf_processor,
        MagicMock(),
        MagicMock(),
        mock_state_tracker
    )

    assert success is False
    assert msg == "ERR_PDF_CORRUPTED"
    mock_pdf_processor.convert_to_markdown.assert_not_called()

def test_e2e_llm_request_failure(temp_output_dir):
    """测试在遇到网络或 LLM 异常时的捕捉逻辑"""
    mock_pdf_processor = MagicMock()
    mock_summarizer = MagicMock()
    mock_state_tracker = MagicMock()

    mock_pdf_processor.validate_pdf.return_value = (True, "")
    mock_pdf_processor.extract_metadata.return_value = {"title": "Timeout Paper"}
    mock_pdf_processor.convert_to_markdown.return_value = "# Content"
    mock_summarizer.generate_summary.side_effect = LLMRequestError("ERR_LLM_TIMEOUT")
    mock_state_tracker.get_file_record.return_value = None

    with patch("src.main.settings") as mock_settings:
        mock_settings.output_path = temp_output_dir
        
        success, msg = process_single_pdf(
            Path("timeout.pdf"),
            mock_pdf_processor,
            mock_summarizer,
            MagicMock(),
            mock_state_tracker
        )

    assert success is False
    assert "ERR_LLM_TIMEOUT" in msg
    mock_summarizer.generate_summary.assert_called_once()
