# DeepRead 项目实施计划

**创建日期**: 20260303
**状态**: 待确认
**最后更新**: 20260303

---

## Context（背景）

### 项目目标
构建一个**学术论文阅读与知识可视化系统**，实现从 PDF 文献导入到 Obsidian 知识图谱的自动化工作流。

### 用户核心需求
1. **输入**: 将 PDF 文献放入指定文件夹
2. **转换**: PDF → Markdown（智能布局识别 + 混合提取策略）
3. **理解**: AI 根据自定义规则阅读并提取关键信息
4. **输出**: 生成 Obsidian Canvas JSON（单文献卡片 + 总图谱）

### 使用场景
- 用户正在撰写硕士论文，研究课题：**对比 Azure Serverless 与传统 SpringBoot 在安全性、高并发场景下的稳定性**
- 需要批量阅读相关领域的学术文献，提取方法论、实验设计、逻辑链
- 通过知识图谱发现文献间的关联，激发批判性思维

---

## 关键决策

### 1. PDF → MD 技术方案

**选择：使用 Marker（整合 pdftext + Surya OCR）**

理由：
- Marker 已整合用户提到的 pdftext 和 Surya，无需自建混合管道
- 自动检测 PDF 类型（文本层/扫描件），智能选择提取策略
- 支持表格识别、公式 OCR、布局分析
- 处理速度：50-100 页 PDF 约 2-4 秒，"12 秒/份"对于学术文献合理
- 支持中文（90+ 语言）

**技术栈**:
```
marker-pdf (主管道)
├── pdftext (文本层快速提取)
├── surya-ocr (OCR + 布局分析)
└── surya-table (表格识别)
```

### 2. 文件组织结构

```
DeepRead/
├── .claude/                       # Claude Code 配置
│   └── plans/                     # 计划文件目录
│
├── README.md                      # 项目文档（新建）
├── CLAUDE.md                      # Claude Code 通用行为准则（现有，保留）
├── RESEARCH_CONTEXT.md            # 研究领域规则（新建，替代.claudrules）
│
├── 00-KnowledgeMap/               # 总图谱
│   └── MasterMap.canvas           # 所有文献的宏观知识图谱
│
├── 01-Literature/                 # 文献处理目录
│   ├── [论文标题]/                # 每篇文献独立文件夹
│   │   ├── [论文标题].md          # 全文 Markdown
│   │   ├── assets/                # 图片资源
│   │   │   └── _page_3_Figure_1.png
│   │   ├── [论文标题].canvas      # 该文献的知识卡片
│   │   └── Summary.md             # AI 总结（方法论/逻辑链/研究内容）
│   │
│   └── ...
│
├── input-pdfs/                    # 待处理 PDF 输入目录
│   └── *.pdf
│
└── src/                           # 源代码目录
    ├── pdf_processor.py           # PDF 处理模块
    ├── summarizer.py              # AI 总结模块
    ├── canvas_builder.py          # Canvas 生成模块
    └── main.py                    # 主脚本
```

### 3. 文件名规范策略

**方案：AI 在 PDF→MD 转换时自动重命名**

流程：
1. 从 PDF 元数据或第一页提取论文标题
2. 创建规范化的文件夹名（如 `[论文标题]/`）
3. Token 成本：仅需一次读取操作，无需额外步骤

### 4. 规则文件设计

**同意分开存放**：

| 文件 | 用途 | 内容 |
|------|------|------|
| `CLAUDE.md` | Claude Code 通用行为准则 | 现有的 6 条规则（代码前确认、澄清歧义、测试用例等） |
| `RESEARCH_CONTEXT.md` | 研究领域特定规则 | 课题描述、文献总结字段、可扩展元信息 |

**RESEARCH_CONTEXT.md 结构**:
```markdown
# 研究课题
[动态更新：当前课题描述]

# 文献总结字段

## 文献元数据 (Metadata)
- 标题 (Title)
- 作者 (Authors)
- 年份 (Year)
- 期刊/来源 (Journal/Source)
- DOI/URL

## 研究问题 (Research Problem)
- 核心研究问题
- 研究动机
- 研究目标

## 主要贡献 (Key Contributions)
- 贡献点 1
- 贡献点 2
- 贡献点 3
- (通常 3-5 点)

## 方法论 (Methodology)
- **研究设计 (Research Design)**：研究设计类型（如实验、调查、案例研究等）
- **数据收集 (Data Collection)**：数据收集方法
- **数据分析 (Data Analysis)**：数据分析方法
- **参与者/样本 (Participants/Sample)**：参与者或样本信息
- **工具/仪器 (Tools/Instruments)**：使用的工具或仪器
- **研究步骤 (Procedure)**：研究步骤
- **验证方法 (Validation Methods)**：验证方法

## 逻辑链 (Logic Chain)
- 从研究问题到结论的推理链条
- 关键假设
- 论证结构

## 主要发现 (Key Findings)
- 核心发现 1
- 核心发现 2
- 核心发现 3

## 贡献与局限性 (Contributions & Limitations)
- 理论贡献
- 实践贡献
- 研究局限性
- 未来研究方向

## 关键词 (Keywords)
- 关键词 1
- 关键词 2
- 关键词 3

## 个人思考/笔记 (Personal Notes/Reflections)
- 对该文献的批判性思考
- 与我研究课题的关联
- 可复用的方法
- 产生的新灵感

# 项目元信息
- 技术栈：Azure Serverless vs SpringBoot
- 评估指标：安全性、高并发能力、稳定性
```

### 5. Obsidian Canvas 输出

**双层结构**：

**单个文献 Canvas**（`Paper.canvas`）:

根据 Prompt PDF 的要求，单个文献 Canvas 应包含以下节点和连接：

```
节点结构：
┌─────────────────────────────────────────────────────────────┐
│  Node 1: 文献元数据 (Metadata)                                │
│  - 标题、作者、年份、期刊、DOI                                  │
│  - type: text                                               │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│ Node 2:       │     │ Node 3:       │     │ Node 4:       │
│ 研究问题      │     │ 方法论        │     │ 主要发现      │
│ (Research     │     │ (Methodology) │     │ (Key          │
│  Problem)     │     │               │     │  Findings)    │
└───────────────┘     └───────────────┘     └───────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │ Node 5:           │
                    │ 贡献与局限性      │
                    │ (Contributions &  │
                    │  Limitations)     │
                    └───────────────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │ Node 6:           │
                    │ 个人思考/笔记     │
                    │ (Personal Notes/  │
                    │  Reflections)     │
                    └───────────────────┘

连接关系：
┌─────────────────┬─────────────────┬──────────────────────────┐
│ 源节点          │ 目标节点        │ 连接标签                 │
├─────────────────┼─────────────────┼──────────────────────────┤
│ 文献元数据      │ 研究问题        │ "addresses"              │
│ 文献元数据      │ 方法论          │ "uses"                   │
│ 文献元数据      │ 主要发现        │ "reports"                │
│ 研究问题        │ 方法论          │ "investigated by"        │
│ 研究问题        │ 主要发现        │ "answers"                │
│ 方法论          │ 主要发现        │ "produces"               │
│ 主要发现        │ 贡献与局限性    │ "leads to"               │
│ 贡献与局限性    │ 个人思考        │ "inspires"               │
└─────────────────┴─────────────────┴──────────────────────────┘
```

**Canvas 节点内容生成策略**：
- 第一步：AI 读取 Markdown 全文，生成 `Summary.md`（中文）
- 第二步：从 `Summary.md` 中提取对应字段，填充到 Canvas 节点
- 好处：Summary.md 可作为独立笔记阅读，Canvas 提供可视化导航

**Canvas JSON 格式要求**:
```json
{
  "nodes": [
    {
      "id": "unique-node-id",
      "type": "text",
      "x": number,
      "y": number,
      "width": number,
      "height": number,
      "text": "节点内容（Markdown 格式）",
      "color": "颜色（可选）"
    }
  ],
  "edges": [
    {
      "id": "unique-edge-id",
      "fromNode": "source-node-id",
      "toNode": "target-node-id",
      "fromSide": "right/left/top/bottom",
      "toSide": "right/left/top/bottom",
      "label": "连接标签",
      "color": "线条颜色（可选）"
    }
  ]
}
```

**总图谱 Canvas**（`MasterMap.canvas`）:
- 位置：`00-KnowledgeMap/MasterMap.canvas`
- 节点：每个文献的 `.canvas` 文件（file 类型节点）
- 边：文献间的关系（"基于"、"改进"、"对比"、"引用"）
- 支持按主题分组（group 类型）
- **更新策略**：自动增量更新
  - 每处理一篇新文献，自动在总图谱中添加对应节点
  - AI 分析新文献与已有文献的关系，自动创建连接边
  - 支持手动调整和添加自定义关系

---

### 6. 资源文件命名

**图片资源** (`assets/` 文件夹):
- 命名格式：`_page_[页码]_Figure_[图号].png`
- 示例：`_page_3_Figure_1.png`, `_page_5_Figure_2.png`
- 好处：与 PDF 页码直接对应，便于追溯

---

## 实现计划 Checklist

### Phase 1: 项目初始化

- [ ] **1.1** 创建目录结构
  - [ ] `input-pdfs/`
  - [ ] `00-KnowledgeMap/`
  - [ ] `01-Literature/`
  - [ ] `src/`
- [ ] **1.2** 编写 `README.md`（项目介绍）
- [ ] **1.3** 编写 `RESEARCH_CONTEXT.md`（初始版本，包含详细的文献总结字段）
- [ ] **1.4** 创建 `.gitignore`（如需要）

### Phase 2: 核心功能开发

- [ ] **2.1** PDF 处理模块 (`src/pdf_processor.py`)
  - [ ] 监听 `input-pdfs/` 目录
  - [ ] 调用 Marker 转换 PDF→MD
  - [ ] 从 PDF 提取标题，创建规范化文件夹名
  - [ ] 提取并保存资源图片到 `assets/`
  - [ ] 输出：`[论文标题].md`

- [ ] **2.2** AI 总结模块 (`src/summarizer.py`)
  - [ ] 读取 Markdown 全文
  - [ ] 根据 `RESEARCH_CONTEXT.md` 定义的字段，生成中文总结
  - [ ] 输出字段包括：文献元数据、研究问题、主要贡献、方法论、逻辑链、主要发现、贡献与局限性、关键词、个人思考
  - [ ] 输出：`Summary.md`

- [ ] **2.3** Canvas 生成模块 (`src/canvas_builder.py`)
  - [ ] **单文献 Canvas 生成**:
    - [ ] 从 `Summary.md` 读取对应字段
    - [ ] 生成 6 个节点（元数据、研究问题、方法论、主要发现、贡献与局限性、个人思考）
    - [ ] 生成 8 条边（按预定义连接关系）
    - [ ] 输出：`[论文标题].canvas`
  - [ ] **总图谱 Canvas 更新**:
    - [ ] 扫描 `01-Literature/` 目录
    - [ ] 为每篇文献添加 file 类型节点
    - [ ] AI 分析文献间关系，自动创建连接边
    - [ ] 输出：`00-KnowledgeMap/MasterMap.canvas`

### Phase 3: 工作流整合

- [ ] **3.1** 创建主脚本 (`src/main.py`)
  - [ ] 命令行参数支持
  - [ ] 批量处理模式
  - [ ] 增量更新（跳过已处理文献）
  - [ ] 进度显示
- [ ] **3.2** 创建配置文件 (`config.yaml` 或 `.env`)
  - [ ] 输入/输出路径配置
  - [ ] API 密钥（如使用 LLM）

### Phase 4: 测试与优化

- [ ] **4.1** 使用现有 PDF 测试完整流程
  - [ ] 安装依赖：`pip install marker-pdf surya-ocr pdftext`
  - [ ] 放入 PDF 测试
  - [ ] 验证输出结构
- [ ] **4.2** 验证 Canvas 在 Obsidian 中的显示
  - [ ] 检查 `MasterMap.canvas` 是否正确渲染
  - [ ] 检查单文献 Canvas 是否正确渲染
  - [ ] 检查图片链接是否有效
  - [ ] 检查节点连接是否正确
- [ ] **4.3** 优化处理速度和 token 使用

---

## 关键文件路径

| 文件 | 路径 | 状态 |
|------|------|------|
| README.md | `DeepRead/README.md` | 待创建 |
| RESEARCH_CONTEXT.md | `DeepRead/RESEARCH_CONTEXT.md` | 待创建 |
| PDF 处理器 | `DeepRead/src/pdf_processor.py` | 待创建 |
| Canvas 生成器 | `DeepRead/src/canvas_builder.py` | 待创建 |
| AI 总结器 | `DeepRead/src/summarizer.py` | 待创建 |
| 主脚本 | `DeepRead/src/main.py` | 待创建 |
| 配置文件 | `DeepRead/config.yaml` | 待创建 |
| CLAUDE.md | `DeepRead/CLAUDE.md` | 现有（保留） |
| .claudrules | `DeepRead/.claudrules` | 现有（待废弃/合并） |

### 输出文件示例

单篇文献处理后应生成:
```
01-Literature/Vaswani-2017-Attention-Is-All-You-Need/
├── Vaswani-2017-Attention-Is-All-You-Need.md    # 全文 Markdown
├── assets/
│   ├── _page_3_Figure_1.png
│   └── _page_5_Figure_2.png
├── Vaswani-2017-Attention-Is-All-You-Need.canvas # 单文献 Canvas
└── Summary.md                                     # AI 中文总结
```

总图谱:
```
00-KnowledgeMap/
└── MasterMap.canvas  # 自动增量更新
```

---

## 验证方案

### 端到端测试流程

1. **准备阶段**
   ```bash
   # 安装依赖
   pip install marker-pdf surya-ocr pdftext

   # 创建目录结构
   mkdir -p input-pdfs 00-KnowledgeMap 01-Literature src
   ```

2. **测试单篇文献**
   ```bash
   # 放入 PDF
   cp FULLTEXT01.pdf input-pdfs/

   # 运行处理
   python main.py --input input-pdfs/FULLTEXT01.pdf

   # 验证输出
   ls 01-Literature/
   # 检查：文件夹、.md、.canvas、Summary.md、assets/
   ```

3. **验证 Obsidian 兼容性**
   - 打开 Obsidian
   - 检查 `MasterMap.canvas` 是否正确渲染
   - 检查单文献 Canvas 是否正确渲染
   - 检查图片链接是否有效
   - 检查节点连接是否正确

4. **批量测试**
   ```bash
   # 放入多篇 PDF
   cp *.pdf input-pdfs/

   # 批量处理
   python main.py --batch

   # 验证总图谱更新
   cat 00-KnowledgeMap/MasterMap.canvas
   ```

5. **验证增量更新**
   ```bash
   # 添加新 PDF
   cp new-paper.pdf input-pdfs/

   # 增量处理（应跳过已处理的文献）
   python main.py --batch

   # 验证总图谱中新增了节点
   ```

---

## 风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| Marker 处理速度慢 | 用户体验差 | 支持后台批处理、进度显示 |
| 中文 OCR 准确率 | 总结质量下降 | 可调 LLM 辅助校正 |
| Canvas 格式变更 | 兼容性问题 | 参考 Obsidian 官方文档 |
| 论文标题提取错误 | 文件名混乱 | 提供手动重命名选项 |

---

## 下一步行动

等待用户确认本计划后，开始实现 Phase 1。
