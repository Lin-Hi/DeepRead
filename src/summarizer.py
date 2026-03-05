"""
/**
 * [IN]: config.settings, exceptions, prompts.summary_prompt, openai
 * [OUT]: Summarizer 类 - 生成并解析文献总结
 *         阶段1：literature_note_template.md → LLM → Summary.md（Markdown，直接写入）
 *         阶段2：用正则表达式基于层级结构解析 Summary.md 内容 → Canvas 字段 dict
 * [POS]: 被 main.py 调用，在 PDF 处理后生成 AI 总结
 * [PROTOCOL]: 修改 Summary 格式 -> 编辑 literature_note_template.md
 *             修改 Canvas 提取逻辑 -> 同步更新 _extract_canvas_data 和 canvas_builder
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
    """AI 总结器：两阶段生成文献总结"""

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
        两阶段生成文献总结。

        阶段1：用 literature_note_template.md 生成完整 Markdown → 写入 Summary.md
        阶段2：从 Summary.md 内容中用 JSON prompt 提取 Canvas 字段

        Args:
            markdown_content: PDF 转换后的 Markdown 全文
            output_path: Summary.md 输出路径
            research_context: 可选的研究领域上下文

        Returns:
            Canvas 所需字段的 dict（包含 title/methodology/key_findings 等）
        """
        # ── 阶段1：生成 Markdown Summary ─────────────────────────────
        prompt = get_summary_prompt(markdown_content, research_context)
        summary_md = self._call_with_retry(prompt)

        # 清理可能的代码块包裹（LLM 有时会加 ```markdown ... ```）
        summary_md = self._strip_code_fence(summary_md)

        # 直接写入 Summary.md（保留 LLM 的 Markdown 结构）
        output_path.write_text(summary_md, encoding="utf-8")

        # ── 阶段2：提取 Canvas JSON ───────────────────────────────────
        canvas_data = self._extract_canvas_data(summary_md)
        return canvas_data

    def _strip_code_fence(self, text: str) -> str:
        """移除 LLM 可能包裹的代码块标记"""
        text = text.strip()
        for fence in ("```markdown", "```md", "```"):
            if text.startswith(fence):
                text = text[len(fence):]
                if text.endswith("```"):
                    text = text[:-3]
                return text.strip()
        return text

    def _extract_canvas_data(self, summary_md: str) -> dict:
        """基于 literature_note_template.md 的结构直接从 Summary.md 提取 Canvas 所需字段（正则表达式解析，无需 LLM）"""
        import re
        data = {
            "citekey": "", "title": "", "year": "", "first_author": "",
            "journal": "", "abstract": "", "hypothesis": "",
            "research_gap_hypothesis": "", "methodology": "",
            "key_findings": "", "critical_analysis": "",
            "connections": "", "action_items": "", "key_takeaway": ""
        }

        # 1. 提取元数据 (YAML 和 Metadata 区块)
        m_citekey = re.search(r"citekey:\s*(.*)", summary_md)
        if m_citekey: data["citekey"] = m_citekey.group(1).strip()

        for key in ["Title", "Year", "Journal", "FirstAuthor"]:
            m = re.search(rf"\*\*{key}\*\*::\s*(.*)", summary_md)
            if m:
                field = "first_author" if key == "FirstAuthor" else key.lower()
                data[field] = m.group(1).strip()

        # 2. 提取 Abstract (支持 "Abstract" 或 "摘要")
        m_abstract = re.search(r"> #### (?:Abstract|摘要)\s*\n*(.*?)\n+(?:##|###)", summary_md, re.DOTALL)
        if m_abstract:
            data["abstract"] = m_abstract.group(1).replace("\n>", "\n").replace(">", "").strip()

        # 3. 按主要章节分割提取
        sections_map = {
            "研究缺口与假设": "research_gap_hypothesis",
            "方法论与证据基础": "methodology",
            "核心机制与发现": "key_findings",
            "批判性分析": "critical_analysis",
            "关联与整合": "connections",
            "行动项与后续步骤": "action_items"
        }

        parts = re.split(r'\n###\s+', "\n" + summary_md)
        for part in parts[1:]:
            lines = part.strip().split("\n")
            header = lines[0].strip()
            content = "\n".join(lines[1:]).strip()

            for zh_name, en_key in sections_map.items():
                if zh_name in header:
                    content = re.split(r'\r?\n## ', "\n" + content)[0].strip()
                    data[en_key] = content
                    break


        # 4. 提取 Hypothesis（从 research_gap_hypothesis 中进一步细分）
        if "核心假设" in data["research_gap_hypothesis"]:
            parts_hypo = data["research_gap_hypothesis"].split("核心假设")
            data["hypothesis"] = parts_hypo[-1].strip().strip("#").strip()

        # 5. 提取 Key Takeaway
        m_takeaway = re.search(r"\*\*(?:核心要点|Key Takeaway)\*\*[:：]\s*(.*)", summary_md)
        if m_takeaway:
            data["key_takeaway"] = m_takeaway.group(1).strip()

        return data


    def _call_with_retry(self, prompt: str) -> str:
        """调用 LLM，失败时重试"""
        for attempt in range(self.max_retries):
            try:
                return self._call_llm(prompt)
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise LLMRequestError(f"Failed to generate summary: {e}")
                time.sleep(5 * (attempt + 1))

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

    def _parse_json_response(self, response: str) -> dict:
        """解析 LLM JSON 响应为字典"""
        try:
            if "```json" in response:
                start = response.find("```json") + 7
                end = response.find("```", start)
                json_str = response[start:end].strip()
            elif "```" in response:
                start = response.find("```") + 3
                end = response.find("```", start)
                json_str = response[start:end].strip()
            else:
                json_str = response.strip()

            return json.loads(json_str)
        except json.JSONDecodeError as e:
            raise LLMValidationError(f"Invalid JSON response: {e}", raw_response=response)

    # ── 以下方法保留向后兼容（测试用） ────────────────────────────────

    def _parse_response(self, response: str) -> dict:
        """向后兼容：解析 JSON 响应（仅用于测试）"""
        return self._parse_json_response(response)

    def _validate_summary(self, summary: dict) -> list:
        """验证必填字段，返回缺失字段列表"""
        required_fields = [
            "citekey", "title", "abstract", "hypothesis",
            "methodology", "key_findings"
        ]
        return [f for f in required_fields if not summary.get(f)]

    def _format_summary_md(self, summary: dict) -> str:
        """向后兼容：格式化 Summary 为 Markdown（仅用于测试）"""
        lines = [
            "---",
            f"citekey: {summary.get('citekey', '')}",
            "status: read",
            f"dateread: {time.strftime('%Y-%m-%d')}",
            "---",
            "",
            f"> {summary.get('abstract', '')}",
            "",
            "> **Key Takeaway**: "
            f"{summary.get('key_takeaway', '')}",
        ]
        return "\n".join(lines)
