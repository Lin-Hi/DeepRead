# DeepRead Prompts Module

本目录包含用于 LLM 的 Prompt 模板。

## 文件职责

| 文件 | 用途 | 被谁消费 |
|------|------|----------|
| `summary_prompt.py` | 生成单篇文献的 Summary.md | `summarizer.py` |
| `relation_prompt.py` | 推断多篇文献之间的关系 | `canvas_builder.py` (总图谱生成时) |

## Prompt 设计原则

1. **结构化输出**: 所有 Prompt 都要求 LLM 返回 JSON 格式
2. **中英双语**: 关键术语保留英文，大段逻辑用中文
3. **可扩展性**: 通过 `get_summary_prompt()` 函数支持自定义字段

## 接口定义

```python
from src.prompts import get_summary_prompt, get_relation_prompt

# 获取 Summary 生成 Prompt
prompt = get_summary_prompt(
    markdown_content="...",
    research_context="..."
)

# 获取关系推断 Prompt
prompt = get_relation_prompt(
    papers_info=[...]
)
```

## 变更协议

- 修改 Prompt 内容 → 检查 `summarizer.py` 的字段解析逻辑
- 添加新 Prompt → 更新本文件文件列表
- 修改输出格式 → 同步更新 `RESEARCH_CONTEXT.md`
