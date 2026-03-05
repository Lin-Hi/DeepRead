"""
/**
 * [IN]: literature_note_template.md（Prompt 内容来源）
 * [OUT]: get_summary_prompt() - 返回完整 LLM Prompt 字符串
 * [POS]: 被 summarizer.py 消费
 * [PROTOCOL]: 修改 Prompt 内容 -> 只编辑 literature_note_template.md，无需改动本文件
 *             修改输出字段结构 -> 同步更新 summarizer._parse_response 和 canvas_builder
 */
"""
from pathlib import Path
from typing import Optional

# Prompt 模板文件路径（与本文件同目录）
_TEMPLATE_PATH = Path(__file__).parent / "literature_note_template.md"


def _load_template() -> str:
    """运行时从 .md 文件加载 Prompt 模板"""
    try:
        return _TEMPLATE_PATH.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Prompt template not found: {_TEMPLATE_PATH}\n"
            "请确保 literature_note_template.md 存在于 src/prompts/ 目录下。"
        )


def get_summary_prompt(markdown_content: str, research_context: Optional[str] = None) -> str:
    """
    构建用于生成 Summary 的完整 Prompt。

    Prompt 模板从 literature_note_template.md 实时读取，
    修改格式只需编辑该文件，无需改动 Python 代码。
    """
    template = _load_template()

    context_section = ""
    if research_context:
        context_section = f"\n## Research Context Guidelines\n{research_context}\n"

    return f"{template}\n{context_section}\n## Paper Content\n{markdown_content}"


# 向后兼容：保留 SUMMARY_PROMPT 变量（惰性加载）
# 注意：直接使用 get_summary_prompt() 是推荐方式
def __getattr__(name: str) -> str:
    if name == "SUMMARY_PROMPT":
        return _load_template()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
