"""
/**
 * [IN]: src.summarizer (Summarizer), openai (mocked)
 * [OUT]: Summarizer 单元测试
 * [POS]: pytest 测试套件，Phase 4 单元测试覆盖
 * [PROTOCOL]: summarizer.py 修改 -> 同步更新本测试
 */
"""
import json
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch


SAMPLE_SUMMARY = {
    "citekey": "Smith2024Deep",
    "title": "Deep Learning Overview",
    "abstract": "This paper provides an overview of deep learning.",
    "hypothesis": "Deep learning can solve complex problems.",
    "methodology": "Systematic literature review.",
    "key_findings": "State-of-the-art results on benchmarks.",
    "research_gap_hypothesis": "Gap exists in scalability.",
    "logic_chain": "Problem -> Method -> Result",
    "critical_analysis": "Limitations include dataset bias.",
    "connections": "Related to transfer learning.",
    "action_items": "Study attention mechanisms.",
    "key_takeaway": "Deep learning is powerful.",
    "year": "2024",
    "first_author": "John Smith",
    "journal": "Nature ML",
    "citation": "Smith et al., 2024",
    "contribution": "Novel architecture.",
    "related_concepts": "CNN, RNN, Transformer",
}


def _make_mock_openai_response(content: str):
    """构建 Mock OpenAI 响应对象"""
    mock_choice = MagicMock()
    mock_choice.message.content = content
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    return mock_response


class TestSummarizerParseResponse:
    """测试 _parse_response 的 JSON 提取逻辑"""

    def _get_summarizer(self):
        with patch("src.config.settings") as mock_settings:
            mock_settings.api_key = "sk-test"
            mock_settings.api_base_url = "https://api.test.com/v1"
            mock_settings.model = "test-model"
            mock_settings.max_retries = 3
            from src.summarizer import Summarizer
            s = Summarizer.__new__(Summarizer)
            s.model = "test-model"
            s.max_retries = 3
            s.client = MagicMock()
            return s

    def test_parses_plain_json(self):
        s = self._get_summarizer()
        result = s._parse_response(json.dumps({"title": "Test"}))
        assert result["title"] == "Test"

    def test_parses_json_in_code_block(self):
        s = self._get_summarizer()
        raw = '```json\n{"title": "From Code Block"}\n```'
        result = s._parse_response(raw)
        assert result["title"] == "From Code Block"

    def test_parses_json_in_generic_code_block(self):
        s = self._get_summarizer()
        raw = '```\n{"title": "Generic Block"}\n```'
        result = s._parse_response(raw)
        assert result["title"] == "Generic Block"

    def test_raises_on_invalid_json(self):
        from src.exceptions import LLMValidationError
        s = self._get_summarizer()
        with pytest.raises(LLMValidationError):
            s._parse_response("this is not json at all")


class TestSummarizerValidateSummary:
    """测试 _validate_summary 的必填字段检查"""

    def _get_summarizer(self):
        from src.summarizer import Summarizer
        s = Summarizer.__new__(Summarizer)
        s.model = "test-model"
        s.max_retries = 3
        s.client = MagicMock()
        return s

    def test_complete_summary_no_missing(self):
        s = self._get_summarizer()
        missing = s._validate_summary(SAMPLE_SUMMARY)
        assert missing == []

    def test_detects_missing_required_fields(self):
        s = self._get_summarizer()
        incomplete = {"title": "Only Title"}
        missing = s._validate_summary(incomplete)
        assert "abstract" in missing
        assert "methodology" in missing
        assert "key_findings" in missing

    def test_empty_dict_has_all_missing(self):
        s = self._get_summarizer()
        missing = s._validate_summary({})
        assert len(missing) > 0


class TestSummarizerFormatMarkdown:
    """测试 _format_summary_md 输出格式"""

    def _get_summarizer(self):
        from src.summarizer import Summarizer
        s = Summarizer.__new__(Summarizer)
        s.client = MagicMock()
        return s

    def test_contains_citekey_in_frontmatter(self):
        s = self._get_summarizer()
        md = s._format_summary_md(SAMPLE_SUMMARY)
        assert "citekey: Smith2024Deep" in md

    def test_contains_title(self):
        s = self._get_summarizer()
        md = s._format_summary_md(SAMPLE_SUMMARY)
        assert "Deep Learning Overview" in md

    def test_has_yaml_frontmatter_delimiters(self):
        s = self._get_summarizer()
        md = s._format_summary_md(SAMPLE_SUMMARY)
        assert md.startswith("---")
        # 第二个 --- 出现
        assert md.count("---") >= 2

    def test_empty_dict_does_not_raise(self):
        s = self._get_summarizer()
        md = s._format_summary_md({})
        assert isinstance(md, str)


class TestSummarizerGenerateSummary:
    """测试 generate_summary 的完整调用链（全 mock）"""

    def test_successful_generation_writes_file(self, tmp_path):
        with patch("src.config.settings") as mock_settings:
            mock_settings.api_key = "sk-test"
            mock_settings.api_base_url = "https://api.test.com/v1"
            mock_settings.model = "test-model"
            mock_settings.max_retries = 3

            from src.summarizer import Summarizer

            with patch("openai.OpenAI"):
                summarizer = Summarizer()
                summarizer.client = MagicMock()
                summarizer.client.chat.completions.create.return_value = \
                    _make_mock_openai_response(json.dumps(SAMPLE_SUMMARY))

                output_path = tmp_path / "Summary.md"
                result = summarizer.generate_summary(
                    markdown_content="# Paper\nContent.",
                    output_path=output_path
                )

                assert output_path.exists()
                assert isinstance(result, dict)
                assert result.get("title") == SAMPLE_SUMMARY["title"]

    def test_raises_on_persistent_llm_failure(self, tmp_path):
        from src.exceptions import LLMRequestError
        with patch("src.config.settings") as mock_settings:
            mock_settings.api_key = "sk-test"
            mock_settings.api_base_url = "https://api.test.com/v1"
            mock_settings.model = "test-model"
            mock_settings.max_retries = 1

            from src.summarizer import Summarizer
            with patch("openai.OpenAI"):
                summarizer = Summarizer()
                summarizer.max_retries = 1
                summarizer.client = MagicMock()
                summarizer.client.chat.completions.create.side_effect = \
                    Exception("Connection refused")

                with pytest.raises(LLMRequestError):
                    summarizer.generate_summary(
                        markdown_content="# Paper",
                        output_path=tmp_path / "Summary.md"
                    )
