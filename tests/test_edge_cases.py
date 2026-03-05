"""
/**
 * [IN]: pytest, unittest.mock, tempfile, exceptions
 * [OUT]: Edge case tests asserting exceptions
 * [POS]: tests 模块内，保证异常流的防御能力
 * [PROTOCOL]: 增加新异常类型 -> 同步增加边界测试
 */
"""
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from openai import APIConnectionError, APITimeoutError

from src.exceptions import PDFNotFoundError, PDFCorruptedError, LLMRequestError
from src.pdf_processor import PDFPreprocessor
from src.summarizer import Summarizer
from src.config import settings

def test_pdf_not_found(tmp_path):
    preprocessor = PDFPreprocessor()
    non_existent = tmp_path / "ghost.pdf"
    is_valid, err_code, info = preprocessor.validate(non_existent)
    assert is_valid is False
    assert err_code == "ERR_PDF_NOT_FOUND"

def test_pdf_corrupted(tmp_path):
    preprocessor = PDFPreprocessor()
    corrupted_pdf = tmp_path / "bad.pdf"
    # Write invalid PDF signature instead of %PDF-
    corrupted_pdf.write_text("Hello World, not a PDF.", encoding="utf-8")
    
    is_valid, err_code, info = preprocessor.validate(corrupted_pdf)
    assert is_valid is False
    assert err_code == "ERR_PDF_CORRUPTED"

@patch("src.summarizer.OpenAI")
def test_llm_api_connection_error(mock_openai):
    """验证当发生网络错误时，LLM 请求能够正确抛出 LLMRequestError"""
    # 模拟客户端连接错误
    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = APITimeoutError(request=MagicMock())
    mock_openai.return_value = mock_client
    
    # 临时覆盖重试次数以加快测试
    settings.max_retries = 1
    summarizer = Summarizer()
    
    with pytest.raises(LLMRequestError) as exc_info:
        summarizer._call_with_retry("test prompt")
    
    assert "Failed to generate summary" in str(exc_info.value)

@patch("src.summarizer.OpenAI")
def test_llm_api_retry_then_success(mock_openai):
    """验证 LLM 碰到一次超时后重试成功的机制"""
    mock_client = MagicMock()
    
    success_response = MagicMock()
    success_response.choices[0].message.content = "Success data"
    
    # 第一次抛出错误，第二次成功
    mock_client.chat.completions.create.side_effect = [
        APITimeoutError(request=MagicMock()),
        success_response
    ]
    mock_openai.return_value = mock_client
    
    settings.max_retries = 2
    summarizer = Summarizer()
    
    # 为了测试速度，模拟 sleep 并没有实际等待
    with patch("src.summarizer.time.sleep", return_value=None):
        result = summarizer._call_with_retry("test prompt")
    
    assert result == "Success data"
    assert mock_client.chat.completions.create.call_count == 2
