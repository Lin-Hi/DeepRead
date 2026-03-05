# DeepRead - 学术论文阅读与知识可视化系统

> 从 PDF 文献到 Obsidian 知识图谱的自动化工作流

## 项目简介

DeepRead 是一个面向学术研究者的智能文献处理工具，旨在帮助研究者高效阅读、理解和整理学术文献。通过 AI 驱动的内容提取和可视化技术，将传统 PDF 文献转化为结构化的知识图谱，激发批判性思维和跨文献关联发现。

### 核心功能

1. **PDF → Markdown 智能转换**
   - 使用 Marker（整合 pdftext + Surya OCR）实现高精度文本提取
   - 支持双栏排版、公式、表格等复杂布局识别
   - 自动提取并保存图片资源

2. **AI 驱动的内容总结**
   - 基于自定义规则自动生成中英双语文献总结
   - 提取研究问题、方法论、主要发现、逻辑链等关键信息
   - 生成标准化的 Summary.md 格式

3. **Obsidian Canvas 知识图谱**
   - 单篇文献的知识卡片可视化（6 类节点：元数据、研究问题、方法论、主要发现、局限性、个人思考）
   - 总图谱自动增量更新，展示文献间关系
   - 支持引用关系、改进关系、对比关系的自动推断

4. **增量处理与状态追踪**
   - 基于文件 hash 的增量更新机制
   - 断点续传支持，随时中断随时恢复
   - UNNAMED_[num] 兜底命名策略

## 快速开始

### 环境要求

- Python 3.10+
- Conda 环境（推荐）
- NVIDIA GPU（可选，用于加速 OCR）

### 安装步骤

1. **克隆仓库**
```bash
git clone <repository-url>
cd DeepRead
```

2. **创建 Conda 环境**
```bash
conda create -n deepread python=3.10
conda activate deepread
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **配置 API Key**
```bash
cp .env.example .env
# 编辑 .env 文件，填入你的阿里百炼 API Key
```

5. **准备 PDF 文件**
```bash
# 将需要处理的 PDF 放入 input-pdfs/ 目录
mv your-paper.pdf input-pdfs/
```

### 使用方法

#### 交互模式（默认）
```bash
python src/main.py
# 输入文件名（如 paper.pdf），空行结束
```

#### 批量处理
```bash
python src/main.py --batch
# 自动处理 input-pdfs/ 中所有未处理的 PDF
```

#### 指定文件
```bash
python src/main.py --file paper1.pdf paper2.pdf
```

#### 强制重新处理
```bash
python src/main.py --force
# 忽略 state.json，重新处理所有文件
```

#### 重建总图谱
```bash
python src/main.py --rebuild-map
# 根据已处理的文献重新生成 MasterMap.canvas
```

## 项目结构

```
DeepRead/
├── .deepread/              # 状态文件（隐藏目录）
│   ├── state.json          # 处理状态追踪
│   └── cache/              # LLM 响应缓存
│
├── input-pdfs/             # 待处理 PDF 输入目录
│
├── 00-KnowledgeMap/        # 总图谱目录
│   └── MasterMap.canvas    # 所有文献的宏观知识图谱
│
├── 01-Literature/          # 文献处理目录
│   └── [year]-[author]-[title]/
│       ├── [year]-[author]-[title].md      # 全文 Markdown
│       ├── [year]-[author]-[title].canvas  # 知识卡片
│       ├── Summary.md                       # AI 总结
│       └── assets/                          # 图片资源
│
├── src/                    # 源代码目录
│   ├── main.py             # 主脚本入口
│   ├── config.py           # 配置管理
│   ├── state_tracker.py    # 状态追踪模块
│   ├── pdf_processor.py    # PDF 处理模块
│   ├── summarizer.py       # AI 总结模块
│   ├── canvas_builder.py   # Canvas 生成模块
│   ├── utils.py            # 公共工具
│   ├── exceptions.py       # 统一异常类
│   └── prompts/            # Prompt 模板
│       ├── summary_prompt.py
│       └── relation_prompt.py
│
├── tests/                  # 测试代码目录
├── logs/                   # 日志文件目录
├── reports/                # 技术验证报告目录
├── README.md               # 本文件
├── CLAUDE.md               # Claude Code 行为准则
├── RESEARCH_CONTEXT.md     # 研究领域规则
└── requirements.txt        # 依赖列表
```

## 完整运行示例 (End-to-End Example)

为了清晰演示 DeepRead 从文献进入到可视化卡片产出的实际效果，项目中已内建了一篇经典计算机科学文献作为免配数据的开箱即用示例。以下是完全还原体验的流程：

### 1. 确认示例数据
这篇文献已内置于项目中。在运行之前，确保你可以看到该文件：
- 路径: `input-pdfs/3510611.pdf`
- 来源: *[Serverless Computing: One Step Forward, Two Steps Back](https://dl.acm.org/doi/10.1145/3510611)*

### 2. 执行入口命令
配置好 `.env` 并激活 `conda` 环境后，执行命令：
```bash
python -m src.main --file 3510611.pdf
```
> [!TIP]
> 此时你会观察到由独立分发日志模块接管的规范化控制台提醒，大模型的请求链路（约耗时几十秒以防并发限流）以及 OCR 解析反馈。同时，滚动日志会写入 `logs/`。

### 3. 验收可视化成果
执行完毕，请前往 `01-Literature/`（根据实际解析后的年份前缀）对应目录验收资产：

- **`[...].md`**: 格式被规整修复的全文 Markdown 文档。
- **`Summary.md`**:  大模型抽取的核心要点与逻辑链条。
- **`assets/`**: 精准剪裁的插图。
- **`[...].canvas` (核心高能)**: 用 Obsidian 本地客户端打开此文件，你将体验到以这篇文献为核心铺开的六角属性知识图谱！

---

## 产出物结构详述

### 单篇文献处理后生成：

```
01-Literature/2017-Vaswani-AttentionIsAllYouNeed/
├── 2017-Vaswani-AttentionIsAllYouNeed.md         # 全文 Markdown
├── assets/
│   ├── _page_3_Figure_0.png
│   └── _page_5_Figure_1.png
├── 2017-Vaswani-AttentionIsAllYouNeed.canvas     # 知识卡片
└── Summary.md                                    # AI 总结
```

### Summary.md 包含字段：

- **Citation**: APA 格式引用
- **Metadata**: 标题、年份、期刊、作者等信息
- **Abstract**: 2-3 句核心贡献摘要
- **Research Gap & Hypothesis**: 研究缺口与假设
- **方法论与技术选择**: 研究类型、关键技术及选择理由
- **Key Mechanisms & Findings**: 关键机制与发现
- **逻辑链 (Logic Chain)**: 从研究问题到结论的推理链条
- **Critical Analysis**: 优势、局限性与开放问题
- **Connections & Integration**: 实际应用与个人相关性
- **Action Items**: 后续行动项

## 技术栈

- **PDF 处理**: marker-pdf, surya-ocr, pdftext, pymupdf
- **LLM 服务**: 阿里百炼 (OpenAI 兼容协议)
- **配置管理**: pydantic-settings
- **布局算法**: dagre-python
- **测试框架**: pytest

## 配置说明

编辑 `.env` 文件配置以下选项：

```env
# API 配置（必填）
API_KEY=sk-your-api-key-here
API_BASE_URL=https://coding.dashscope.aliyuncs.com/v1
MODEL=kimi-k2.5

# 路径配置
INPUT_DIR=input-pdfs
OUTPUT_DIR=01-Literature
KNOWLEDGE_MAP_DIR=00-KnowledgeMap

# 处理配置
MAX_RETRIES=3
TIMEOUT_SECONDS=300
BATCH_SIZE=10

# 日志配置
LOG_LEVEL=INFO
```

## 增量更新机制

系统使用 `.deepread/state.json` 记录处理状态：

1. **文件 Hash**: 计算每个 PDF 的 SHA256 hash
2. **增量判断**:
   - hash 匹配 → 跳过
   - hash 不匹配 → 重新处理
   - 无记录 → 新文件，处理
3. **原子写入**: 防止崩溃导致状态文件损坏
4. **UNNAMED 编号**: 全局递增，删除不回收

## 错误处理

| 场景           | 处理策略                          |
| -------------- | --------------------------------- |
| 单文件处理失败 | 重试 3 次，仍失败则跳过并记录     |
| 批量处理       | 单文件失败不阻塞后续，汇总报告    |
| 加密 PDF       | 跳过，记录 ERR_PDF_DECRYPT_FAILED |
| 损坏 PDF       | 跳过，记录 ERR_PDF_CORRUPTED      |
| LLM 超时       | 指数退避重试（5s, 15s, 60s）      |
| dagre 布局失败 | fallback 到固定模板布局           |

详细日志保存在 `logs/deepread_YYYYMMDD_HHMMSS.log`

## 开发计划

详见 [.claude/plans/20260304-deepread-plan-v5.md](.claude/plans/20260304-deepread-plan-v5.md)

### Phase 1: 项目初始化 ✅
- 创建目录结构
- 编写 README.md
- 编写 RESEARCH_CONTEXT.md
- 创建 .gitignore 和 .env.example

### Phase 1.5: 技术验证 🔄
- Marker 基准测试
- Obsidian Canvas Schema 验证
- LLM 请求策略测试
- dagre 布局验证
- PDF 预处理检查

### Phase 2: 核心功能开发 📋
- 配置模块
- 状态追踪模块
- PDF 处理模块
- AI 总结模块
- Canvas 生成模块

### Phase 3: 工作流整合 📋
- 主脚本开发
- 命令行参数解析
- 错误汇总报告

### Phase 4: 测试与优化 📋
- 单元测试
- 端到端测试
- 性能优化

### Phase 5: 边界用例测试 📋
- 异常 PDF 处理
- LLM 异常测试
- 状态追踪测试

## 贡献指南

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License

## 致谢

- [Marker](https://github.com/VikParuchuri/marker) - 优秀的 PDF 转 Markdown 工具
- [Obsidian](https://obsidian.md/) - 强大的知识管理工具
- [阿里百炼](https://bailian.console.aliyun.com/) - LLM 服务提供商
