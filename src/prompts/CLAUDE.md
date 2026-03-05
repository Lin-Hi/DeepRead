# DeepRead Prompts Module

本目录包含用于 LLM 的 Prompt 模板。

## 文件职责

| 文件                          | 用途                                                      | 被谁消费                           |
| ----------------------------- | --------------------------------------------------------- | ---------------------------------- |
| `summary_prompt.py`           | 运行时加载 `literature_note_template.md`，构建完整 Prompt | `summarizer.py`                    |
| `literature_note_template.md` | **Prompt 内容唯一来源**，用于生成 Summary.md，可直接编辑  | `summary_prompt.py` 动态读取       |
| `relation_prompt.py`          | 运行时加载 `relation_template.md`，构建关系推断 Prompt    | `canvas_builder.py` (总图谱生成时) |
| `relation_template.md`        | **Relation Prompt 内容唯一来源**，可直接编辑              | `relation_prompt.py` 动态读取      |

## Prompt 设计原则

1. **内容与代码分离**: Prompt 内容存储在 `.md` 文件中，Python 文件只负责加载和组装
2. **零代码修改**: 修改 Prompt 格式/内容 → **只编辑 `literature_note_template.md`**，无需动 Python
3. **中英双语**: 关键术语保留英文，大段逻辑用中文
4. **格式自定义**: Summary.md 输出格式完全由模板文件控制，不受代码约束

## 接口定义

```python
from src.prompts import get_summary_prompt

# 获取 Summary 生成 Prompt（自动读取 literature_note_template.md）
prompt = get_summary_prompt(
    markdown_content="...",
    research_context="..."  # 可选
)
```

## 变更协议

- **修改 Prompt 内容/格式** → 直接编辑 `literature_note_template.md`，无需改 Python
- **修改输出字段结构（用于 Canvas）** → 同步更新 `summarizer._parse_response` 和 `canvas_builder`
- **添加新 Prompt 文件** → 新建 `.md` 模板 + 对应 `.py` 加载器，并更新本文件
- **`literature_note_template.md` 缺失** → `get_summary_prompt()` 会抛出 `FileNotFoundError`

## 注意事项

> `summary_prompt.py` 保留了 `SUMMARY_PROMPT` 变量名作为向后兼容（通过 `__getattr__` 惰性加载），
> 但推荐直接调用 `get_summary_prompt()`。
