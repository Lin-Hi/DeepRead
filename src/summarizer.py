"""
/**
 * [IN]: config.settings, exceptions, prompts.summary_prompt, openai
 * [OUT]: Summarizer 类 - LLM 请求封装、字段验证、Summary.md 生成
 * [POS]: 被 main.py 调用，在 PDF 处理后生成 AI 总结
 * [PROTOCOL]: 修改 Prompt -> 测试输出质量 -> 更新 RESEARCH_CONTEXT.md
 */
"""
import json
import time
from pathlib import Path
from typing import Optional

from openai import OpenAI

from src.config import settings
from src.exceptions import LLMRequestError, LLMValidationError
from src.prompts.summary_prompt import get_summary_prompt


class Summarizer:
    """AI 总结器：调用 LLM 生成结构化文献总结"""

    def __init__(self):
        self.client = OpenAI(
            api_key=settings.api_key,
            base_url=settings.api_base_url
        )
        self.model = settings.model
        self.max_retries = settings.max_retries

    def generate_summary(
        self,
        markdown_content: str,
        output_path: Path,
        research_context: Optional[str] = None
    ) -> dict:
        """
        生成单篇文献的 Summary

        Args:
            markdown_content: Markdown 格式的论文全文
            output_path: Summary.md 输出路径
            research_context: 可选的研究领域上下文

        Returns:
            解析后的 Summary 字典
        """
        # 构建 Prompt
        prompt = get_summary_prompt(markdown_content, research_context)

        # 调用 LLM（带重试）
        for attempt in range(self.max_retries):
            try:
                response = self._call_llm(prompt)
                summary_data = self._parse_response(response)

                # 验证必填字段
                missing = self._validate_summary(summary_data)
                if missing:
                    if attempt < self.max_retries - 1:
                        # 补充请求
                        supplement_prompt = self._build_supplement_prompt(
                            markdown_content, summary_data, missing
                        )
                        response = self._call_llm(supplement_prompt)
                        supplement_data = self._parse_response(response)
                        summary_data.update(supplement_data)
                    else:
                        raise LLMValidationError(
                            f"Missing required fields after {self.max_retries} retries: {missing}",
                            missing_fields=missing
                        )

                # 写入 Summary.md
                self._write_summary_md(summary_data, output_path)

                return summary_data

            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise LLMRequestError(f"Failed to generate summary: {e}")
                time.sleep(5 * (attempt + 1))  # 指数退避

    def _call_llm(self, prompt: str) -> str:
        """调用 LLM API"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a research assistant specialized in academic paper analysis."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=4000
        )
        return response.choices[0].message.content

    def _parse_response(self, response: str) -> dict:
        """解析 LLM 响应为字典"""
        # 尝试提取 JSON 部分
        try:
            # 查找 ```json 代码块
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
            elif "```" in response:
                json_start = response.find("```") + 3
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
            else:
                json_str = response.strip()

            return json.loads(json_str)
        except json.JSONDecodeError as e:
            raise LLMValidationError(f"Invalid JSON response: {e}", raw_response=response)

    def _validate_summary(self, summary: dict) -> list:
        """验证必填字段，返回缺失字段列表"""
        required_fields = [
            "citekey", "title", "abstract", "hypothesis",
            "methodology", "key_findings"
        ]
        return [f for f in required_fields if not summary.get(f)]

    def _build_supplement_prompt(
        self,
        markdown_content: str,
        partial_summary: dict,
        missing_fields: list
    ) -> str:
        """构建补充请求 Prompt"""
        return f"""
基于以下论文内容，请补充以下缺失字段：{', '.join(missing_fields)}

已提取的信息：
{json.dumps(partial_summary, ensure_ascii=False, indent=2)}

论文内容：
{markdown_content[:5000]}...

请以 JSON 格式返回仅包含缺失字段的对象。
"""

    def _write_summary_md(self, summary: dict, output_path: Path):
        """将 Summary 写入 Markdown 文件"""
        content = self._format_summary_md(summary)
        output_path.write_text(content, encoding='utf-8')

    def _format_summary_md(self, summary: dict) -> str:
        """格式化 Summary 为 Markdown"""
        lines = [
            "---",
            f"citekey: {summary.get('citekey', '')}",
            "status: read",
            f"dateread: {time.strftime('%Y-%m-%d')}",
            "---",
            "",
            "> #### Citation",
            f"> {summary.get('citation', '')}",
            "",
            "> #### Synthesis",
            f"> **Contribution**:: {summary.get('contribution', '')}",
            f"> **Related**:: {summary.get('related_concepts', '')}",
            "",
            "> #### Metadata",
            f"> **Title**:: {summary.get('title', '')}",
            f"> **Year**:: {summary.get('year', '')}",
            f"> **Journal**:: {summary.get('journal', '')}",
            f"> **FirstAuthor**:: {summary.get('first_author', '')}",
            "> **ItemType**:: journalArticle",
            "",
            "> #### Abstract",
            f"> {summary.get('abstract', '')}",
            "",
            "## Notes",
            "",
            "### 🚀 Research Gap & Hypothesis",
            summary.get('research_gap_hypothesis', ''),
            "",
            "### 🔬 Methodology",
            summary.get('methodology', ''),
            "",
            "### 📊 Key Findings",
            summary.get('key_findings', ''),
            "",
            "### 🔗 Logic Chain",
            summary.get('logic_chain', ''),
            "",
            "### 🎯 Critical Analysis",
            summary.get('critical_analysis', ''),
            "",
            "### 🔗 Connections & Integration",
            summary.get('connections', ''),
            "",
            "### 📋 Action Items",
            summary.get('action_items', ''),
            "",
            "## Summary & Conclusion",
            f"> **Key Takeaway**: {summary.get('key_takeaway', '')}",
        ]
        return '\n'.join(lines)
