# DeepRead Source Code

本目录包含 DeepRead 项目的核心源代码模块。

## 文件结构

```
src/
├── main.py              # 主脚本入口，命令行交互
├── config.py            # 配置管理（pydantic-settings）
├── exceptions.py        # 统一异常类定义
├── utils.py             # 工具函数集
├── state_tracker.py     # 状态追踪（增量更新）
├── pdf_processor.py     # PDF 处理（Marker 调用）
├── summarizer.py        # AI 总结（LLM 请求）
├── canvas_builder.py    # Canvas 生成（Obsidian 格式）
└── prompts/             # Prompt 模板
    ├── __init__.py
    ├── summary_prompt.py
    └── relation_prompt.py
```

## 模块依赖关系

```
main.py
├── config.py (被所有模块导入)
├── exceptions.py
├── utils.py
├── state_tracker.py
│   └── config.py
├── pdf_processor.py
│   ├── config.py
│   ├── exceptions.py
│   └── utils.py
├── summarizer.py
│   ├── config.py
│   ├── exceptions.py
│   └── prompts/
└── canvas_builder.py
    ├── config.py
    ├── utils.py
    └── state_tracker.py (读取已处理文献列表)
```

## 使用方式

### 作为模块导入

```python
from src.config import settings
from src.pdf_processor import PDFProcessor
from src.summarizer import Summarizer
```

### 命令行运行

```bash
# 交互模式
python -m src.main

# 批量处理
python -m src.main --batch

# 指定文件
python -m src.main --file paper1.pdf paper2.pdf

# 强制重新处理
python -m src.main --force
```

## 编码规范

- 使用类型注解
- 函数不超过 30 行
- 文件不超过 800 行
- 使用文件头注释标记 [IN]/[OUT]/[POS]/[PROTOCOL]
