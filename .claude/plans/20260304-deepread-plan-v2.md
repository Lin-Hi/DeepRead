# DeepRead 项目规划 v2.0 - 实施计划

**创建日期**: 20260304
**状态**: 待用户确认
**最后更新**: 20260304
**关联计划**: 20260303-deepread-initial-plan.md

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

## 关键决策（已确认）

### 1. PDF → MD 技术方案

**选择：使用 Marker（整合 pdftext + Surya OCR）**

- 运行环境：`PY_3_10` Anaconda 环境
- GPU：NVIDIA RTX 4070 (8GB)，驱动版本 595.71
- 当前状态：marker-pdf (1.10.2)、surya-ocr (0.17.1) 已安装
- PyTorch：当前为 CPU 版本 (2.10.0+cpu)，未来可升级为 GPU 版本加速 OCR
- 升级命令（暂不执行）：
  ```bash
  conda activate PY_3_10
  pip uninstall torch torchvision torchaudio
  pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
  ```

### 2. 文件组织结构

```
DeepRead/
├── .deepread/                       # DeepRead 状态文件（隐藏目录）
│   └── state.json                   # 处理状态追踪（hash、时间戳）
│
├── .claude/                         # Claude Code 配置
│   └── plans/                       # 计划文件目录
│
├── README.md                        # 项目文档（新建）
├── CLAUDE.md                        # Claude Code 通用行为准则（现有，保留）
├── RESEARCH_CONTEXT.md              # 研究领域规则（新建，基于 Prompt V2 翻译+优化）
│
├── 00-KnowledgeMap/                 # 总图谱
│   └── MasterMap.canvas             # 所有文献的宏观知识图谱
│
├── 01-Literature/                   # 文献处理目录
│   ├── [论文标题]/                  # 每篇文献独立文件夹
│   │   ├── [论文标题].md            # 全文 Markdown
│   │   ├── assets/                  # 图片资源
│   │   │   └── _page_[页码]_Figure_[图号].png
│   │   ├── [论文标题].canvas        # 该文献的知识卡片
│   │   └── Summary.md               # AI 总结（方法论/逻辑链/研究内容）
│   │
│   └── ...
│
├── input-pdfs/                      # 待处理 PDF 输入目录
│   └── *.pdf
│
└── src/                             # 源代码目录
    ├── pdf_processor.py             # PDF 处理模块
    ├── summarizer.py                # AI 总结模块
    ├── canvas_builder.py            # Canvas 生成模块
    └── main.py                      # 主脚本
```

### 3. 标题提取与命名策略

**主策略**: 从 PDF 元数据或第一页提取论文标题

**Fallback 策略**（优先级从高到低）:
1. 尝试读取 PDF 元数据 (title 字段)
2. 失败 → 使用 LLM 解析第一页前 3000 tokens 推断标题
3. 失败 → 使用固定命名：`UNNAMED_[num]`（num 是当前目录下 UNNAMED 文件的编号）

**文件名规范化**:
- 移除非法字符：`: ? " < > | \ /`
- 长度截断至 200 字符
- 空格替换为连字符 `-`

### 4. LLM 配置

**Provider**: 阿里百炼
- **Base URL**: `https://coding.dashscope.aliyuncs.com/v1` (OpenAI 兼容协议)
- **API Key**: 用户自行填写（`.env` 文件存储）
- **模型**: `kimi-k2.5`

**请求优化策略**（套餐按请求次数计费）:
- 单篇论文总结：合并为 **1 次请求**（一次性输出所有字段）
- 文献关系推断：批量处理（一次发送多篇文献的 Summary，返回关系矩阵）

### 5. Canvas 生成规范

**单文献 Canvas 节点布局**: 使用 **dagre 自动布局算法**（美观优先）

**节点颜色**（边框颜色区分，文字统一默认黑色）:
| 节点类型 | 边框颜色 |
|---------|---------|
| 文献元数据 | 蓝色 `#3b82f6` |
| 研究问题 | 橙色 `#f97316` |
| 方法论 | 紫色 `#8b5cf6` |
| 主要发现 | 绿色 `#22c55e` |
| 贡献与局限性 | 红色 `#ef4444` |
| 个人思考 | 灰色 `#6b7280` |

**增量更新策略**: 允许重置为算法计算的位置（新增节点时全局重新布局）

**节点 ID 生成**: 使用基于标题的 hash（保证唯一性和可复现性）

### 6. 文献关系推断

**优先级策略**:
1. **DOI/标题匹配参考文献列表** → "引用"关系
2. **LLM 分析摘要中的对比描述** → "基于"、"改进"、"对比"关系
3. **关键词和方法论相似度** → "相关"关系

**置信度阈值**: 不创建边的情况 → 无法确定关系时，不创建边（保守策略）

**关系类型**:
- `cites` (引用)
- `based_on` (基于)
- `improves` (改进)
- `compares_with` (对比)

### 7. 命令行交互方式

**方案 D - 组合模式**:

| 命令 | 行为 |
|------|------|
| `python main.py` | 无参数时进入交互模式，逐个询问文件名，输入空行结束 |
| `python main.py --batch` | 自动扫描 input-pdfs，处理所有未识别文件 |
| `python main.py --file paper1.pdf paper2.pdf` | 一次性列出所有文件 |

**状态追踪**: 使用 `.deepread/state.json` 记录已处理文件的 hash

### 8. Summary.md 格式

**来源**: 基于 `Prompt- Literature Note Generator for a PhD-V2.md` 翻译 + 优化

**核心字段**:
```markdown
---
citekey: {{camelCase: FirstAuthor+FirstWordOfTitle+Year}}
status: read
dateread: {{Current Date YYYY-MM-DD}}
---

> #### Citation
> {{Full APA Style Citation}}

> #### Synthesis
> **Contribution**:: {{单句贡献描述}}
> **Related**:: {{Key Concept 1}}, {{Key Concept 2}}

> #### Metadata
> **Title**:: {{Paper Title}}
> **Year**:: {{Year}}
> **Journal**:: {{Journal Name}}
> **FirstAuthor**:: {{First Author Name}}
> **ItemType**:: journalArticle

> #### Abstract
> {{2-3 句核心贡献摘要}}

## Notes

### 🚀 Research Gap & Hypothesis
#### Problem Context
- **Core Issue**: {{根本问题}}
- **Current Knowledge Gap**: {{文献缺口}}
- **Clinical/Scientific Need**: {{紧迫性}}

#### Central Hypothesis
{{主要假设}}

### 🔬 方法论与技术选择
#### Study Characteristics
- **Type**: {{研究类型}}
- **Scope**: {{范围}}

#### Key Techniques Evaluated
- **{{Technique 1}}**: {{应用方式}}
  - **选择理由**: {{为何选择此方法而非其他}}
- **{{Technique 2}}**: {{应用方式}}
  - **选择理由**: {{为何选择此方法而非其他}}

### 📊 Key Mechanisms & Findings
#### {{Mechanism/Theme 1}}
1. **Concept**: {{描述}}
2. **Findings:**
   - {{Key Result 1}}
   - {{Key Result 2}}

### 🔗 逻辑链 (Logic Chain)
{{从研究问题到结论的推理链条}}

### 🎯 Critical Analysis
#### Strengths
1. **{{Strength 1}}**: {{描述}}
2. **{{Strength 2}}**: {{描述}}

#### Limitations
1. **{{Weakness 1}}**: {{描述}}
2. **{{Weakness 2}}**: {{描述}}

#### Open Questions
1. **{{Question 1}}?**
2. **{{Question 2}}?**

### 🔗 Connections & Integration
#### Practical Implementation
- **Protocols**: {{实施细节}}
- **Tools**: {{工具}}

#### Personal Relevance
- **Research Interests**: {{与研究领域的关联}}
- **Application**: {{潜在应用场景}}

### 📋 Action Items & Next Steps
- [ ] {{待研究问题}}
- [ ] {{待验证假设}}
- [ ] {{待填补知识缺口}}

## Summary & Conclusion
> **Key Takeaway**: {{一句话核心收获}}

#### Final Assessment
- **Innovation**: {{High/Med/Low}}
- **Evidence**: {{High/Med/Low}}
- **Clinical Potential**: {{High/Med/Low}}
```

**语言要求**: 中英双语，关键术语保留英文，大段逻辑陈述用中文便于阅读

**Wikilinks**: 对关键概念、方法论名称、计算机科技术语使用 `[[Wikilinks]]`

### 9. 资源文件命名

**图片资源**: `_page_[页码]_Figure_[图号].png`
- 页码：PDF 页数
- 图号：从 0 开始，如果一页有多个图则递增（如 `_page_3_Figure_0.png`, `_page_3_Figure_1.png`）

### 10. 错误处理

| 场景 | 策略 |
|------|------|
| 单文件处理失败 | 重试 3 次，仍失败则跳过并记录 |
| 批量处理 | 单文件失败不阻塞后续，汇总报告失败列表 |
| 日志文件 | `logs/deepread_YYYYMMDD_HHMMSS.log` |
| 断点续传 | 基于 `.deepread/state.json` 从中断点继续 |

### 11. RESEARCH_CONTEXT.md 更新策略

- 将 Prompt V2 翻译为中文
- 补充缺失的"逻辑链"章节
- 修改"Key Techniques Evaluated"为"方法论与技术选择"，包含选择理由
- 每次生成 Summary 和 Canvas 时先读取当前 RESEARCH_CONTEXT.md 决定格式

---

## 实现计划 Checklist

### Phase 1: 项目初始化
- [ ] **1.1** 创建目录结构
  - [ ] `input-pdfs/`
  - [ ] `00-KnowledgeMap/`
  - [ ] `01-Literature/`
  - [ ] `src/`
  - [ ] `.deepread/`
- [ ] **1.2** 编写 `README.md`（项目介绍、安装指南、使用示例）
- [ ] **1.3** 编写 `RESEARCH_CONTEXT.md`（基于 Prompt V2 翻译+优化）
- [ ] **1.4** 创建 `.gitignore`
- [ ] **1.5** 创建 `.env.example`（API Key 模板）

### Phase 2: 核心功能开发

- [ ] **2.1** PDF 处理模块 (`src/pdf_processor.py`)
  - [ ] 调用 Marker 转换 PDF→MD
  - [ ] 从 PDF 提取标题，创建规范化文件夹名
  - [ ] 提取并保存图片到 `assets/`
  - [ ] 标题提取 fallback 策略（元数据 → LLM → UNNAMED_[num]）

- [ ] **2.2** AI 总结模块 (`src/summarizer.py`)
  - [ ] 读取 Markdown 全文
  - [ ] 根据 `RESEARCH_CONTEXT.md` 定义字段，生成中英双语总结
  - [ ] 合并为单次请求输出（减少 API 调用次数）
  - [ ] Wikilinks 自动生成
  - [ ] 输出：`Summary.md`

- [ ] **2.3** Canvas 生成模块 (`src/canvas_builder.py`)
  - [ ] **单文献 Canvas 生成**:
    - [ ] 从 `Summary.md` 读取对应字段
    - [ ] 生成 6 个节点（元数据、研究问题、方法论、主要发现、贡献与局限性、个人思考）
    - [ ] 使用 dagre 进行自动布局
    - [ ] 设置节点边框颜色
    - [ ] 生成 8 条边（按预定义连接关系）
    - [ ] 输出：`[论文标题].canvas`
  - [ ] **总图谱 Canvas 更新**:
    - [ ] 扫描 `01-Literature/` 目录
    - [ ] 为每篇文献添加 file 类型节点
    - [ ] 优先级关系推断（DOI/标题匹配 → LLM 分析 → 关键词相似度）
    - [ ] 无法确定关系时不创建边
    - [ ] 输出：`00-KnowledgeMap/MasterMap.canvas`

### Phase 3: 工作流整合

- [ ] **3.1** 创建主脚本 (`src/main.py`)
  - [ ] 无参数时进入交互模式
  - [ ] `--batch` 参数自动处理全部未识别文件
  - [ ] `--file` 参数指定单个或多个文件
  - [ ] 增量更新（基于 `.deepread/state.json` 跳过已处理文献）
  - [ ] 进度显示

- [ ] **3.2** 状态追踪模块 (`src/state_tracker.py`)
  - [ ] 读取/写入 `.deepread/state.json`
  - [ ] 文件 hash 计算
  - [ ] UNNAMED_[num] 编号管理

### Phase 4: 测试与优化

- [ ] **4.1** 单元测试
  - [ ] PDF 处理器测试（有/无文本层 PDF）
  - [ ] 总结器测试（字段完整性验证）
  - [ ] Canvas 生成器测试（Obsidian 兼容性）
  - [ ] 状态追踪测试（增量更新逻辑）

- [ ] **4.2** 端到端测试
  - [ ] 单篇 PDF 处理测试
  - [ ] 批量处理测试
  - [ ] 增量更新测试
  - [ ] Obsidian 显示验证

- [ ] **4.3** 优化
  - [ ] 减少 API 请求次数
  - [ ] 处理速度优化

---

## 关键文件路径

| 文件 | 路径 | 状态 |
|------|------|------|
| README.md | `DeepRead/README.md` | 待创建 |
| RESEARCH_CONTEXT.md | `DeepRead/RESEARCH_CONTEXT.md` | 待创建 |
| 状态追踪器 | `DeepRead/src/state_tracker.py` | 待创建 |
| PDF 处理器 | `DeepRead/src/pdf_processor.py` | 待创建 |
| Canvas 生成器 | `DeepRead/src/canvas_builder.py` | 待创建 |
| AI 总结器 | `DeepRead/src/summarizer.py` | 待创建 |
| 主脚本 | `DeepRead/src/main.py` | 待创建 |
| 配置文件 | `DeepRead/config.yaml` | 待创建 |
| CLAUDE.md | `DeepRead/CLAUDE.md` | 现有（保留） |

---

## 输出文件示例

单篇文献处理后应生成:
```
01-Literature/Vaswani-2017-Attention-Is-All-You-Need/
├── Vaswani-2017-Attention-Is-All-You-Need.md    # 全文 Markdown
├── assets/
│   ├── _page_3_Figure_0.png
│   └── _page_5_Figure_1.png
├── Vaswani-2017-Attention-Is-All-You-Need.canvas # 单文献 Canvas
└── Summary.md                                     # AI 中英双语总结
```

总图谱:
```
00-KnowledgeMap/
└── MasterMap.canvas  # 自动增量更新
```

状态文件:
```
.deepread/
└── state.json  # 处理状态追踪
```

---

## 验证方案

### 端到端测试流程

1. **准备阶段**
   ```bash
   # 激活环境
   conda activate PY_3_10

   # 创建目录结构
   mkdir -p input-pdfs 00-KnowledgeMap 01-Literature src
   ```

2. **测试单篇文献**
   ```bash
   # 放入 PDF
   cp FULLTEXT01.pdf input-pdfs/

   # 运行处理（交互模式）
   python main.py
   # 输入文件名：FULLTEXT01.pdf
   # 输入空行结束

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
| Marker 处理速度慢（CPU 模式） | 用户体验差 | 可升级 GPU 版 PyTorch 加速 OCR |
| 中文 OCR 准确率 | 总结质量下降 | Marker 已支持 90+ 语言，fallback 到 LLM 校正 |
| Canvas 格式变更 | 兼容性问题 | 参考 Obsidian 官方文档，测试后发布 |
| 论文标题提取错误 | 文件名混乱 | fallback 策略 + UNNAMED_[num] 兜底 |
| API 请求次数超预算 | 成本增加 | 合并请求策略 + 批量关系推断 |
| dagre 布局节点重叠 | 可视化效果差 | 调整节点尺寸和间距参数 |

---

## 下一步行动

等待用户确认本计划后，开始实现 Phase 1。
