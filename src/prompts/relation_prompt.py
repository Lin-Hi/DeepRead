"""
/**
 * [IN]: relation_template.md（Prompt 内容来源）
 * [OUT]: get_relation_prompt() - 返回完整关系推断 Prompt 字符串
 * [POS]: 被 canvas_builder.py 消费，用于推断文献间关系
 * [PROTOCOL]: 修改 Prompt 内容 -> 只编辑 relation_template.md，无需改动本文件
 */
"""
from pathlib import Path

# Prompt 模板文件路径（与本文件同目录）
_TEMPLATE_PATH = Path(__file__).parent / "relation_template.md"


def _load_template() -> str:
    """运行时从 .md 文件加载 Prompt 模板"""
    try:
        return _TEMPLATE_PATH.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Prompt template not found: {_TEMPLATE_PATH}\n"
            "请确保 relation_template.md 存在于 src/prompts/ 目录下。"
        )


def get_relation_prompt(papers: list) -> str:
    """
    构建用于文献关系推断的完整 Prompt。

    Prompt 模板从 relation_template.md 实时读取，
    修改格式只需编辑该文件，无需改动 Python 代码。

    Args:
        papers: 文献列表，每项包含 citekey, title, abstract, methodology 等

    Returns:
        完整的 Prompt 字符串
    """
    template = _load_template()
    papers_context = format_papers_for_relation(papers)
    return template.replace("{papers_context}", papers_context)


def format_papers_for_relation(papers: list) -> str:
    """
    格式化文献列表用于关系推断 Prompt

    Args:
        papers: 文献列表，每项包含 citekey, title, abstract, methodology 等

    Returns:
        格式化后的字符串
    """
    context_parts = []
    for i, paper in enumerate(papers, 1):
        part = f"""[{i}] Citekey: {paper.get('citekey', 'unknown')}
Title: {paper.get('title', 'N/A')}
Abstract: {paper.get('abstract', 'N/A')[:500]}...
Methodology: {paper.get('methodology', 'N/A')[:300]}...
Keywords: {', '.join(paper.get('keywords', []))}
"""
        context_parts.append(part)

    return "\n---\n".join(context_parts)


# 向后兼容：保留 RELATION_PROMPT 变量（惰性加载）
def __getattr__(name: str):
    if name == "RELATION_PROMPT":
        return _load_template()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
