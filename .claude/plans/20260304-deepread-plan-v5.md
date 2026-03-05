# DeepRead 项目规划 v5.0 - 实施计划

**创建日期**: 20260304
**状态**: 待用户确认
**最后更新**: 20260304
**关联计划**: 20260304-deepread-plan-v4.md
**改进说明**: 基于 v4 + plan-reviewer 评审意见，移除扩展功能（多 Context 支持），新增 dagre 布局验证和 PDF 预处理验证，补充 state.json 原子写入和错误汇总报告

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

**技术验证清单（Phase 1.5 执行）**:
- [ ] 选取 3-5 篇典型论文（双栏/单栏、有/无公式、有/无表格）进行基准测试
- [ ] 记录 CPU 模式下的处理耗时，设定性能阈值（如：>10 分钟则告警）
- [ ] 验证公式提取：确认输出是纯文本还是保留 LaTeX 语法
- [ ] 验证表格提取：确认是否支持 Markdown 表格或需特殊处理
- [ ] 增加 PDF 预处理检查（文件完整性、加密检测、最小页数检查）
- [ ] Marker 失败 fallback：尝试 pymupdf4llm 作为备选方案

---

### 2. 模块架构设计

```
┌─────────────────────────────────────────────────────────────┐
│                        main.py                               │
│  (命令行入口：交互模式 / --batch / --file / --force)          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     state_tracker.py                         │
│  (状态管理：hash 计算、增量更新、UNNAMED 编号)                   │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│ pdf_processor │     │ summarizer.py │     │ config.py     │
│ .py           │     │               │     │ (被所有模块    │
│               │     │ - 读取 MD      │     │  消费)        │
│ - Marker 调用  │     │ - LLM 请求     │     │               │
│ - 标题提取     │     │ - Summary 输出 │     │               │
│ - 图片保存     │     │               │     │               │
└───────────────┘     └───────────────┘     └───────────────┘
        │                     │
        │                     ▼
        │            ┌───────────────┐
        │            │ canvas_       │
        │            │ builder.py    │
        │            │ (消费：Summary│
        │            │  .md 文件)     │
        │            └───────────────┘
        │                     │
        └─────────────────────┘
                │
                ▼
        ┌───────────────┐
        │ utils.py      │
        │ (纯函数工具集) │
        └───────────────┘
                │
                ▼
        ┌───────────────┐
        │ prompts/      │
        │ summary_prompt│
        │ relation_prompt│
        └───────────────┘
```

---

### 3. 文件组织结构

```
DeepRead/
├── .deepread/                       # DeepRead 状态文件（隐藏目录）
│   ├── state.json                   # 处理状态追踪（hash、时间戳、输出列表）
│   └── cache/                       # LLM 响应缓存（可选）
│
├── .claude/                         # Claude Code 配置
│   ├── plans/                       # 计划文件目录
│   └── hooks/                       # Hook 脚本目录（可选）
│
├── logs/                            # 日志文件目录
│   ├── deepread_YYYYMMDD_HHMMSS.log # 运行日志
│   └── llm_usage.jsonl              # LLM 使用记录（Token 统计）
│
├── reports/                         # 技术验证报告目录
│   ├── marker-benchmark.md          # Marker 基准测试报告
│   ├── obsidian-canvas-schema.md    # Canvas Schema 分析
│   ├── llm-request-strategy.md      # LLM 请求策略
│   ├── state-tracker-design.md      # State 设计文档
│   ├── dagre-layout-test.md         # dagre 布局测试（新增）
│   └── pdf-preprocessing-check.md   # PDF 预处理检查（新增）
│
├── README.md                        # 项目文档（新建）
├── CLAUDE.md                        # Claude Code 通用行为准则（现有，保留）
├── RESEARCH_CONTEXT.md              # 研究领域规则（新建，基于 Prompt V2 翻译 + 优化）
│
├── 00-KnowledgeMap/                 # 总图谱
│   └── MasterMap.canvas             # 所有文献的宏观知识图谱
│
├── 01-Literature/                   # 文献处理目录
│   ├── [year]-[firstAuthor]-[titleSlug]/  # 每篇文献独立文件夹
│   │   ├── [year]-[firstAuthor]-[titleSlug].md  # 全文 Markdown
│   │   ├── assets/                  # 图片资源
│   │   │   └── _page_[页码]_Figure_[图号].png
│   │   ├── [year]-[firstAuthor]-[titleSlug].canvas  # 该文献的知识卡片
│   │   └── Summary.md               # AI 总结（方法论/逻辑链/研究内容）
│   │
│   └── ...
│
├── input-pdfs/                      # 待处理 PDF 输入目录
│   └── *.pdf
│
├── tests/                           # 测试代码目录
│   ├── test_pdf_processor.py
│   ├── test_summarizer.py
│   ├── test_canvas_builder.py
│   ├── test_state_tracker.py
│   └── conftest.py
│
└── src/                             # 源代码目录
    ├── main.py                      # 主脚本（命令行入口）
    ├── config.py                    # 配置管理（pydantic-settings）
    ├── state_tracker.py             # 状态追踪模块
    ├── pdf_processor.py             # PDF 处理模块
    ├── summarizer.py                # AI 总结模块
    ├── canvas_builder.py            # Canvas 生成模块
    ├── utils.py                     # 公共工具
    ├── exceptions.py                # 统一异常类（新增）
    └── prompts/                     # Prompt 模板
        ├── summary_prompt.py        # Summary.md 生成 Prompt
        └── relation_prompt.py       # 文献关系推断 Prompt
```

---

### 4. 标题提取与命名策略

**格式**: `[year]-[firstAuthorLastName]-[titleSlug]`

**字段规则**:
| 字段                | 规则                            | 最大值  | 示例                    |
| ------------------- | ------------------------------- | ------- | ----------------------- |
| year                | 4 位数字，优先元数据 → LLM 推断 | 4       | `2023`                  |
| firstAuthorLastName | 仅姓氏，移除空格和前缀          | 15 字符 | `Vaswani`               |
| titleSlug           | 标题前 5 个实词，字母数字连字符 | 80 字符 | `AttentionIsAllYouNeed` |

**完整文件名示例**:
- `2017-Vaswani-AttentionIsAllYouNeed`
- `2020-Devlin-BERTPreTrainingDeepBidirectional`
- `2021-Chen-ViTImageClassificationWithTransformers`

**Fallback 策略**（优先级从高到低）:
1. 完整格式 → 成功
2. 无标题 → `UNNAMED_[year]_[num]`（如 `UNNAMED_2023_001`）
3. 无年份 → `UNNAMED_[firstAuthor]_[num]`
4. 全部失败 → `UNNAMED_[num]`

**文件名规范化算法**:
```python
def normalize_filename(title: str, year: str, first_author: str) -> str:
    """规范化文件名并处理冲突"""
    # 1. 提取作者姓氏（取最后一个单词，处理 Western 姓名）
    author_lastname = first_author.strip().split()[-1] if first_author else ''
    author_lastname = re.sub(r'[^\w]', '', author_lastname)[:15]

    # 2. 标题 slug 化
    title_slug = re.sub(r'[^\w\s]', '', title)  # 移除标点
    title_slug = ' '.join(title_slug.split()[:5])  # 取前 5 个实词
    title_slug = re.sub(r'\s+', '', title_slug)  # 移除空格
    title_slug = title_slug[:80]

    # 3. 组合
    base_name = f"{year}-{author_lastname}-{title_slug}"

    # 4. 移除非法字符
    base_name = re.sub(r'[<>:"/\\|?*]', '', base_name)

    # 5. Unicode 规范化 (NFC)
    base_name = unicodedata.normalize('NFC', base_name)

    # 6. 截断（预留空间给扩展名和冲突后缀）
    if len(base_name) > 100:
        base_name = base_name[:100]

    return base_name
```

**路径长度检查**:
```python
MAX_PATH_LENGTH = 255  # Windows 限制

def validate_path(full_path: Path) -> bool:
    if len(str(full_path)) > MAX_PATH_LENGTH:
        # 截断 titleSlug 或使用 hash 后缀
        return False
    return True
```

---

### 5. 配置管理（pydantic-settings）

```python
# src/config.py
from pydantic_settings import BaseSettings
from pathlib import Path
from typing import Optional

class Settings(BaseSettings):
    # API 配置
    api_base_url: str = "https://coding.dashscope.aliyuncs.com/v1"
    api_key: str
    model: str = "kimi-k2.5"

    # 路径配置
    input_dir: str = "input-pdfs"
    output_dir: str = "01-Literature"
    knowledge_map_dir: str = "00-KnowledgeMap"
    state_dir: str = ".deepread"
    log_dir: str = "logs"
    reports_dir: str = "reports"

    # 处理配置
    max_retries: int = 3
    batch_size: int = 10
    timeout_seconds: int = 300

    # 日志配置
    log_level: str = "INFO"

    # Canvas 配置
    canvas_node_width: int = 300
    canvas_node_height: int = 200
    canvas_node_spacing: int = 50

    # 文件名配置
    max_filename_length: int = 100
    max_title_slug_words: int = 5

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def root_dir(self) -> Path:
        return Path(__file__).parent.parent

    @property
    def input_path(self) -> Path:
        return self.root_dir / self.input_dir

    @property
    def output_path(self) -> Path:
        return self.root_dir / self.output_dir

# 使用
settings = Settings()
```

**.env 文件示例**:
```env
API_KEY=sk-xxxxxxxxx
MODEL=kimi-k2.5
LOG_LEVEL=DEBUG
```

**.env.example**（提交到 Git）:
```env
API_KEY=你的 API Key
MODEL=kimi-k2.5
LOG_LEVEL=INFO
```

---

### 6. LLM 配置

**Provider**: 阿里百炼
- **Base URL**: `https://coding.dashscope.aliyuncs.com/v1` (OpenAI 兼容协议)
- **API Key**: 用户自行填写（`.env` 文件存储）
- **模型**: `kimi-k2.5`

**请求优化策略**（套餐按请求次数计费）:
- 单篇论文总结：合并为 **1 次请求**（一次性输出所有字段）
- 文献关系推断：批量处理（一次发送多篇文献的 Summary，返回关系矩阵）

**Token 预估与拆分策略**:
- 输入：Markdown 全文（预估 5000-10000 tokens）+ Prompt（1000 tokens）
- 输出：Summary（预估 2000-3000 tokens）
- 如果输入超过模型限制：
  - 方案 A：分段提取（先提取标题/摘要/方法论，再提取其他字段）
  - 方案 B：使用支持长上下文的模型（如 kimi-chat）

**字段完整性验证**:
```python
def validate_summary(summary: dict) -> List[str]:
    """验证必填字段，返回缺失字段列表"""
    required_fields = ["citekey", "title", "abstract", "hypothesis", "methodology"]
    return [f for f in required_fields if not summary.get(f)]

# 如果有缺失，自动发起补充请求
```

**批量关系推断的分批策略**:
```python
# 每批最多 5 篇文献，避免 token 爆炸
for i in range(0, len(papers), 5):
    batch = papers[i:i+5]
    # 计算 batch 内的关系矩阵
```

**错误处理（指数退避）**:
```python
RETRY_DELAYS = [5, 15, 60]  # 秒

for delay in RETRY_DELAYS:
    try:
        response = call_llm()
        # 验证字段完整性
        missing = validate_summary(response)
        if missing:
            log_warning(f"缺失字段：{missing}")
            # 发起补充请求
        break
    except RateLimitError:
        time.sleep(delay)
    except AuthenticationError:
        log_error("API Key 无效")
        raise  # 不重试
    except TimeoutError:
        continue
```

---

### 7. Canvas 生成规范

**单文献 Canvas 节点布局**: 使用 **dagre 自动布局算法**（美观优先）

**Python 布局库选择**: `dagre-python`

**节点颜色**（边框颜色区分，文字统一默认黑色）:
| 节点类型     | 边框颜色       |
| ------------ | -------------- |
| 文献元数据   | 蓝色 `#3b82f6` |
| 研究问题     | 橙色 `#f97316` |
| 方法论       | 紫色 `#8b5cf6` |
| 主要发现     | 绿色 `#22c55e` |
| 贡献与局限性 | 红色 `#ef4444` |
| 个人思考     | 灰色 `#6b7280` |

**增量更新策略**: 允许重置为算法计算的位置（新增节点时全局重新布局）

**节点 ID 生成**: 使用基于标题的 hash + 时间戳（避免冲突）
```python
def generate_node_id(title: str) -> str:
    """使用 title + timestamp 组合 hash 避免冲突"""
    import hashlib
    import time
    base = hashlib.sha256(title.encode()).hexdigest()[:12]
    return f"node_{base}_{int(time.time())}"
```

**Fallback 固定模板布局**（dagre 失败时用）:
```
┌───────────────┐     ┌───────────────┐
│  元数据 (50,50)  │────▶│ 研究问题 (400,50)│
└───────────────┘     └───────────────┘
         │                      │
         ▼                      ▼
┌───────────────┐     ┌───────────────┐
│方法论 (50,300) │────▶│主要发现 (400,300)│
└───────────────┘     └───────────────┘
         │                      │
         ▼                      ▼
┌───────────────┐     ┌───────────────┐
│局限性 (50,550) │────▶│个人思考 (400,550)│
└───────────────┘     └───────────────┘
```

**Obsidian Canvas Schema 验证清单（Phase 1.5 执行）**:
1. 手动创建一个 Canvas，导出 JSON 分析结构：
```json
{
  "nodes": [
    {
      "id": "node_id",
      "type": "text",
      "x": 100,
      "y": 100,
      "width": 300,
      "height": 200,
      "text": "内容"
    }
  ],
  "edges": [
    {
      "id": "edge_id",
      "fromNode": "node_a",
      "toNode": "node_b",
      "label": "cites"
    }
  ]
}
```

2. 验证清单：
- [ ] 生成最小 Canvas 文件并在 Obsidian 中打开
- [ ] 验证中文渲染
- [ ] 验证边标签显示
- [ ] 验证节点颜色（borderColor 字段是否存在）
- [ ] 验证节点 ID 格式（是否需要 UUID 还是可自定义）

---

### 8. 文献关系推断

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

---

### 9. 命令行交互方式

**方案 D - 组合模式**:

| 命令                                          | 行为                                               |
| --------------------------------------------- | -------------------------------------------------- |
| `python main.py`                              | 无参数时进入交互模式，逐个询问文件名，输入空行结束 |
| `python main.py --batch`                      | 自动扫描 input-pdfs，处理所有未识别文件            |
| `python main.py --file paper1.pdf paper2.pdf` | 一次性列出所有文件                                 |
| `python main.py --force`                      | 强制重新处理，忽略 state.json 中的 hash 匹配       |
| `python main.py --skip-summary`               | 跳过 Summary 生成，仅更新 Canvas                   |
| `python main.py --rebuild-map`                | 重建总图谱（而非增量更新）                         |

**状态追踪**: 使用 `.deepread/state.json` 记录已处理文件的 hash

---

### 10. Summary.md 格式

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

**Wikilinks**: 对关键概念、方法论名称、计算机科学术语使用 `[[Wikilinks]]`

---

### 11. 资源文件命名

**图片资源**: `_page_[页码]_Figure_[图号].png`
- 页码：PDF 页数
- 图号：从 0 开始，如果一页有多个图则递增（如 `_page_3_Figure_0.png`, `_page_3_Figure_1.png`）

**图片提取策略**: 优先使用 Marker 的默认图片提取功能

---

### 12. 错误处理

**错误码设计**:

| 错误码                     | 含义              | 处理策略                 |
| -------------------------- | ----------------- | ------------------------ |
| `ERR_PDF_DECRYPT_FAILED`   | PDF 加密无法解密  | 跳过，记录日志           |
| `ERR_PDF_CORRUPTED`        | PDF 文件损坏      | 跳过，记录日志           |
| `ERR_PDF_EMPTY`            | PDF 页数为 0      | 跳过，记录日志           |
| `ERR_MARKER_TIMEOUT`       | Marker 处理超时   | 重试 3 次，失败跳过      |
| `ERR_TITLE_EXTRACT_FAILED` | 标题提取失败      | 使用 UNNAMED_[num]       |
| `ERR_LLM_TIMEOUT`          | LLM 请求超时      | 指数退避重试             |
| `ERR_LLM_INVALID_JSON`     | LLM 返回无效 JSON | 重试，使用 fallback 解析 |
| `ERR_CANVAS_LAYOUT_FAILED` | dagre 布局失败    | 使用固定模板布局         |
| `ERR_CONFIG_INVALID`       | 配置验证失败      | 终止程序，提示用户       |

**处理策略**:
| 场景           | 策略                                     |
| -------------- | ---------------------------------------- |
| 单文件处理失败 | 重试 3 次，仍失败则跳过并记录            |
| 批量处理       | 单文件失败不阻塞后续，汇总报告失败列表   |
| 日志文件       | `logs/deepread_YYYYMMDD_HHMMSS.log`      |
| 断点续传       | 基于 `.deepread/state.json` 从中断点继续 |

**state.json 原子写入**（防止崩溃损坏）:
```python
import tempfile
import shutil

def save_state_atomic(state_path: Path, data: dict):
    """原子写入，避免崩溃导致损坏"""
    temp_path = state_path.with_suffix('.tmp')
    with open(temp_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    shutil.move(str(temp_path), str(state_path))
```

**错误汇总报告**（批量处理结束输出）:
```
==================================================
处理完成
成功：8/10

失败文件列表:
  - paper1.pdf: ERR_MARKER_TIMEOUT
  - paper2.pdf: ERR_TITLE_EXTRACT_FAILED

详细日志：logs/deepread_20260304_143022.log
==================================================
```

---

### 13. RESEARCH_CONTEXT.md 使用策略

- 将 Prompt V2 翻译为中文
- 补充缺失的"逻辑链"章节
- 修改"Key Techniques Evaluated"为"方法论与技术选择"，包含选择理由
- 每次生成 Summary 和 Canvas 时先读取当前 RESEARCH_CONTEXT.md 决定格式

**加载机制**:
- 程序启动时读取 RESEARCH_CONTEXT.md
- 解析为结构化配置（YAML frontmatter + 正文）
- 作为 system prompt 的一部分发送给 LLM

**Fallback**:
```python
if not research_context.exists():
    log_warning("RESEARCH_CONTEXT.md 不存在，使用默认模板")
    use_default_summary_format()
```

---

### 14. state.json 详细设计

```json
{
  "version": "1.0",
  "last_updated": "2026-03-04T14:30:00Z",
  "files": {
    "FULLTEXT01.pdf": {
      "hash": "sha256:abc123...",
      "processed_at": "2026-03-04T14:30:00Z",
      "title": "Attention Is All You Need",
      "folder_name": "2017-Vaswani-AttentionIsAllYouNeed",
      "outputs": [
        "01-Literature/2017-Vaswani-AttentionIsAllYouNeed/2017-Vaswani-AttentionIsAllYouNeed.md",
        "01-Literature/2017-Vaswani-AttentionIsAllYouNeed/Summary.md",
        "01-Literature/2017-Vaswani-AttentionIsAllYouNeed/2017-Vaswani-AttentionIsAllYouNeed.canvas"
      ],
      "status": "completed"
    }
  },
  "unnamed_counter": 3
}
```

**增量更新逻辑**:
1. 扫描 `input-pdfs/` 目录
2. 计算每个 PDF 的 hash（SHA256）
3. 对比 state.json：
   - hash 匹配 → 跳过
   - hash 不匹配 → 重新处理
   - 无记录 → 新文件，处理
4. 更新 state.json（原子写入）

**UNNAMED 编号管理**:
- `unnamed_counter` 全局递增
- 删除文件不回收编号（避免冲突）
- 格式：`UNNAMED_[year]_[num]` 或 `UNNAMED_[num]`

**文件存在性检查**:
```python
def validate_outputs(outputs: List[str]) -> List[str]:
    """检查输出文件是否存在，返回缺失文件列表"""
    return [f for f in outputs if not Path(f).exists()]

# 在增量更新前检查
missing = validate_outputs(record["outputs"])
if missing:
    log_warning(f"输出文件缺失：{missing}，将重新处理")
    return False  # 标记为需要重新处理
```

---

## 实现计划 Checklist

### Phase 1: 项目初始化
- [x] **1.1** 创建目录结构
  - [x] `input-pdfs/`
  - [x] `00-KnowledgeMap/`
  - [x] `01-Literature/`
  - [x] `src/`
  - [x] `.deepread/`
  - [x] `logs/`
  - [x] `reports/`
  - [x] `tests/`
- [x] **1.2** 编写 `README.md`（项目介绍、安装指南、使用示例）
- [x] **1.3** 编写 `RESEARCH_CONTEXT.md`（基于 Prompt V2 翻译 + 优化）
- [x] **1.4** 创建 `.gitignore`
- [x] **1.5** 创建 `.env.example`（API Key 模板）

---

### Phase 1.5: 技术验证（v5 更新）

- [x] **1.5.1** Marker 基准测试
  - [x] 选取 3-5 篇典型论文（双栏/单栏、有/无公式、有/无表格）
  - [x] 记录 CPU 模式下的处理耗时
  - [x] 验证公式提取（LaTeX 保留情况）
  - [x] 验证表格提取（Markdown 兼容性）
  - [x] 输出：`reports/marker-benchmark.md`

- [x] **1.5.2** Obsidian Canvas Schema 验证
  - [x] 手动创建示例 Canvas 并导出 JSON
  - [x] 分析节点/边结构、ID 格式、颜色字段
  - [x] 验证中文渲染、边标签显示
  - [x] 输出：`reports/obsidian-canvas-schema.md`

- [x] **1.5.3** LLM 请求测试
  - [x] Token 用量预估（输入/输出）
  - [x] 字段完整性验证逻辑
  - [x] 错误处理（超时、无效 JSON、缺失字段）
  - [x] 输出：`reports/llm-request-strategy.md`

- [x] **1.5.4** state.json 设计评审
  - [x] 确定完整结构（hash、时间戳、输出列表、UNNAMED 计数器）
  - [x] 确定增量更新逻辑
  - [x] 确定冲突处理策略
  - [x] 输出：`reports/state-tracker-design.md`

- [x] **1.5.5 dagre 布局验证**（v5 新增）
  - [x] 安装 dagre-python 验证兼容性
  - [x] 测试 6 节点 8 边单文献布局效果
  - [x] 验证节点重叠问题
  - [x] 设计 fallback 固定模板（dagre 失败时用）
  - [x] 输出：`reports/dagre-layout-test.md`

- [x] **1.5.6 PDF 预处理验证**（v5 新增）
  - [x] 使用 pymupdf 检测加密 PDF
  - [x] 检测损坏 PDF（文件头校验）
  - [x] 检测空 PDF（页数=0）
  - [x] 输出：`reports/pdf-preprocessing-check.md`

---

### Phase 2: 核心功能开发

- [x] **2.0** 配置模块 (`src/config.py`)
  - [x] 定义 Settings 类（pydantic-settings）
  - [x] 定义所有配置项（API、路径、处理、日志、Canvas、文件名）
  - [x] 创建 `.env.example`

- [x] **2.1** 工具模块 (`src/utils.py`)
  - [x] 日志配置函数
  - [x] 文件操作函数（路径清理、目录创建）
  - [x] 文件名规范化函数（year-author-titleSlug 格式）

- [x] **2.2** 异常模块 (`src/exceptions.py`)（v5 新增）
  - [x] 定义 DeepReadError 基类
  - [x] 定义 PDFAccessError、MarkerProcessingError、LLMRequestError、CanvasLayoutError

- [x] **2.3** 状态追踪模块 (`src/state_tracker.py`)
  - [x] 读取/写入 `.deepread/state.json`
  - [x] 文件 hash 计算（SHA256）
  - [x] UNNAMED_[num] 编号管理
  - [x] 增量更新逻辑
  - [x] 原子写入实现

- [x] **2.4** Prompt 模板 (`src/prompts/`)
  - [x] `summary_prompt.py` - Summary.md 生成 Prompt
  - [x] `relation_prompt.py` - 文献关系推断 Prompt

- [x] **2.5** PDF 处理模块 (`src/pdf_processor.py`)
  - [x] 调用 Marker 转换 PDF→MD
  - [x] 从 PDF 提取标题，创建规范化文件夹名（year-author-titleSlug 格式）
  - [x] 提取并保存图片到 `assets/`
  - [x] 标题提取 fallback 策略（元数据 → LLM → UNNAMED）
  - [x] PDF 预处理检查（完整性、加密、页数）

- [x] **2.6** AI 总结模块 (`src/summarizer.py`)
  - [x] 读取 Markdown 全文
  - [x] 根据 `RESEARCH_CONTEXT.md` 定义字段，生成中英双语总结
  - [x] 合并为单次请求输出（减少 API 调用次数）
  - [x] Wikilinks 自动生成
  - [x] 字段完整性验证
  - [x] 输出：`Summary.md`

- [x] **2.7** Canvas 生成模块 (`src/canvas_builder.py`)
  - [x] **单文献 Canvas 生成**:
    - [x] 从 `Summary.md` 读取对应字段
    - [x] 生成 6 个节点（元数据、研究问题、方法论、主要发现、贡献与局限性、个人思考）
    - [x] 设置节点边框颜色
    - [x] 生成 8 条边（带标签）
    - [x] fallback 固定模板布局（dagre 失败时）
    - [x] 基于测试进行 v3 手动布局优化及中文标题调整
    - [x] 输出：`[year]-[firstAuthor]-[titleSlug].canvas`
  - [ ] **总图谱 Canvas 更新**:
    - [ ] 扫描 `01-Literature/` 目录
    - [ ] 为每篇文献添加 file 类型节点
    - [ ] 优先级关系推断（DOI/标题匹配 → LLM 分析 → 关键词相似度）
    - [ ] 无法确定关系时不创建边
    - [ ] 输出：`00-KnowledgeMap/MasterMap.canvas`

- [x] **2.8** 主脚本 (`src/main.py`)
  - [x] 无参数时进入交互模式
  - [x] `--batch` 参数自动处理全部未识别文件
  - [x] `--file` 参数指定单个或多个文件
  - [x] `--force` 强制重新处理
  - [x] `--skip-summary` 跳过 Summary 生成
  - [x] `--rebuild-map` 重建总图谱
  - [x] 增量更新（基于 `.deepread/state.json` 跳过已处理文献）
  - [x] 进度显示
  - [x] 日志输出
  - [x] 错误汇总报告

---

### Phase 3: 工作流整合（正在进行）

- [ ] **3.1** 集成测试与验证
  - [x] 验证各模块协同工作 (单元测试已启动)
  - [ ] 端到端流程测试（PDF → Markdown → Summary → Canvas）
  - [ ] 错误处理验证
  - [ ] 日志输出检查

- [ ] **3.2** 依赖安装脚本完善
  - [ ] 创建 `requirements.txt`
  - [ ] 验证所有依赖可正常安装
  - [ ] 添加可选依赖说明

---

### Phase 4: 测试与优化

- [ ] **4.1** 单元测试（pytest）
  - [ ] PDF 处理器测试（有/无文本层 PDF）
  - [ ] 总结器测试（字段完整性验证）
  - [ ] Canvas 生成器测试（Obsidian 兼容性）
  - [ ] 状态追踪测试（增量更新逻辑）
  - [ ] 配置模块测试（环境变量加载）

- [ ] **4.2** 端到端测试
  - [ ] 单篇 PDF 处理测试
  - [ ] 批量处理测试
  - [ ] 增量更新测试
  - [ ] Obsidian 显示验证

- [ ] **4.3** 优化
  - [ ] 减少 API 请求次数
  - [ ] 处理速度优化
  - [ ] dagre 布局参数调整

---

### Phase 5: 边界用例测试

- [ ] **5.1** 边界用例测试
  - [ ] 0 页 PDF（异常处理）
  - [ ] >100 页 PDF（性能与超时）
  - [ ] 加密 PDF（密码保护）
  - [ ] 损坏 PDF（无法解析）
  - [ ] 纯图片 PDF（无文本层，完全依赖 OCR）
  - [ ] 双栏排版 PDF（布局识别）
  - [ ] 含大量公式的 PDF（LaTeX 提取）

- [ ] **5.2** LLM 异常测试
  - [ ] Mock LLM 返回空响应
  - [ ] Mock LLM 返回无效 JSON
  - [ ] Mock LLM 超时
  - [ ] Mock LLM 返回缺失字段

- [ ] **5.3** 状态追踪测试
  - [ ] 同一文件连续处理两次（第二次应跳过）
  - [ ] 文件内容变化后处理（应重新处理）
  - [ ] state.json 损坏后的恢复
  - [ ] UNNAMED 编号连续性

- [ ] **5.4** 性能测试
  - [ ] 10 篇文献批量处理耗时
  - [ ] 内存占用峰值
  - [ ] 磁盘 I/O 统计

---

## 关键文件路径

| 文件                | 路径                             | 状态              |
| ------------------- | -------------------------------- | ----------------- |
| README.md           | `DeepRead/README.md`             | 待创建            |
| RESEARCH_CONTEXT.md | `DeepRead/RESEARCH_CONTEXT.md`   | 待创建            |
| 配置模块            | `DeepRead/src/config.py`         | 待创建            |
| 工具模块            | `DeepRead/src/utils.py`          | 待创建            |
| 异常模块            | `DeepRead/src/exceptions.py`     | 待创建（v5 新增） |
| 状态追踪器          | `DeepRead/src/state_tracker.py`  | 待创建            |
| Prompt 模板         | `DeepRead/src/prompts/`          | 待创建            |
| PDF 处理器          | `DeepRead/src/pdf_processor.py`  | 待创建            |
| Canvas 生成器       | `DeepRead/src/canvas_builder.py` | 待创建            |
| AI 总结器           | `DeepRead/src/summarizer.py`     | 待创建            |
| 主脚本              | `DeepRead/src/main.py`           | 待创建            |
| 依赖列表            | `DeepRead/requirements.txt`      | 待创建            |
| CLAUDE.md           | `DeepRead/CLAUDE.md`             | 现有（保留）      |

---

## 输出文件示例

单篇文献处理后应生成:
```
01-Literature/2017-Vaswani-AttentionIsAllYouNeed/
├── 2017-Vaswani-AttentionIsAllYouNeed.md    # 全文 Markdown
├── assets/
│   ├── _page_3_Figure_0.png
│   └── _page_5_Figure_1.png
├── 2017-Vaswani-AttentionIsAllYouNeed.canvas # 单文献 Canvas
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

日志文件:
```
logs/
└── deepread_20260304_143022.log  # 运行日志
```

技术报告:
```
reports/
├── marker-benchmark.md          # Marker 基准测试
├── obsidian-canvas-schema.md    # Canvas Schema 分析
├── llm-request-strategy.md      # LLM 请求策略
├── state-tracker-design.md      # State 设计文档
├── dagre-layout-test.md         # dagre 布局测试（v5 新增）
└── pdf-preprocessing-check.md   # PDF 预处理检查（v5 新增）
```

---

## 验证方案

### 端到端测试流程

1. **准备阶段**
   ```bash
   # 激活环境
   conda activate PY_3_10

   # 安装依赖
   pip install -r requirements.txt

   # 创建目录结构
   mkdir -p input-pdfs 00-KnowledgeMap 01-Literature src logs reports tests
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

6. **单元测试**
   ```bash
   # 运行 pytest
   pytest tests/ -v
   ```

---

## 风险与缓解

| 风险                           | 影响             | 缓解措施                                                                  |
| ------------------------------ | ---------------- | ------------------------------------------------------------------------- |
| Marker 处理速度慢（CPU 模式）  | 用户体验差       | 可升级 GPU 版 PyTorch 加速 OCR；Phase 1.5 基准测试确认耗时                |
| 中文 OCR 准确率                | 总结质量下降     | Marker 已支持 90+ 语言，fallback 到 LLM 校正                              |
| Canvas 格式变更                | 兼容性问题       | Phase 1.5 手动验证 Schema，参考 Obsidian 官方文档                         |
| 论文标题提取错误               | 文件名混乱       | fallback 策略 + UNNAMED_[num] 兜底；新格式 year-author-titleSlug 降低冲突 |
| API 请求次数超预算             | 成本增加         | 合并请求策略 + 批量关系推断                                               |
| dagre 布局节点重叠             | 可视化效果差     | 调整节点尺寸和间距参数；fallback 到固定模板（v5 已设计）                  |
| pydantic-settings 配置验证失败 | 程序无法启动     | 提供清晰的错误提示和 `.env.example`                                       |
| dagre-python 安装失败          | 布局功能无法使用 | fallback 到固定模板布局                                                   |
| 路径长度超限                   | 文件写入失败     | 文件名截断至 100 字符；路径长度检查函数                                   |
| state.json 损坏                | 增量更新失效     | 原子写入机制（v5 新增）；损坏后重建                                       |

---

## 下一步行动

**当前状态**: 计划 v5 已创建，等待用户确认后开始实现 Phase 1。

**待办事项**:
1. 用户确认本计划
2. 开始实现 Phase 1（项目初始化）
3. 执行 Phase 1.5 技术验证

---

## 版本历史

| 版本 | 日期     | 改进说明                                                                                                                                                            |
| ---- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| v1   | 20260303 | 初始版本                                                                                                                                                            |
| v2   | 20260304 | 补充模块架构                                                                                                                                                        |
| v3   | 20260304 | 补充配置管理、Prompts 目录、测试框架                                                                                                                                |
| v4   | 20260304 | 基于 plan-reviewer 评审意见：新增 Phase 1.5 技术验证、补全 state.json 设计、错误码、边界用例、文件名格式改为 year-author-titleSlug                                  |
| v5   | 20260304 | 基于 plan-reviewer 深度评审：移除扩展功能（多 Context 支持），新增 dagre 布局验证和 PDF 预处理验证，补充 state.json 原子写入和错误汇总报告，新增 exceptions.py 模块 |
| v5.1 | 20260305 | Phase 3 完成：修复全链路 8 个 Bug，真实 PDF E2E 测试通过（RTX 4070 GPU + Marker）；新增 Phase 6 收尾计划                                                            |

---

## Phase 6: 项目收尾展示（待所有流程确认无误后执行）

> **触发条件**：Phase 4 + Phase 5 全部通过，工具流稳定可靠后再执行。

### 目标
在 GitHub 仓库中提供一个完整的运行示例，帮助读者/评审者快速理解工具效果。

### 待办清单

- [ ] **加入示例 PDF**：将 `input-pdfs/3510611.pdf`（来源：https://dl.acm.org/doi/10.1145/3510611，ACM 论文《Serverless Computing: A Survey of Opportunities, Challenges, and Applications》）从 `.gitignore` 中单独排除并加入 git 跟踪
- [ ] **加入示例输出**：将对应的 `01-Literature/2026-ServerlessComputingASurveyof/` 目录（含 `.md`、`Summary.md`、`.canvas`）加入 git 跟踪
- [ ] **编写 README 示例章节**：包含运行命令、预期输出截图（Obsidian Canvas 展示图）
- [ ] **最终 commit & push**

### `.gitignore` 修改方式（届时执行）

```gitignore
# 排除整个目录...
input-pdfs/
01-Literature/

# ...但保留示例文件（使用 ! 取反）
!input-pdfs/3510611.pdf
!01-Literature/2026-ServerlessComputingASurveyof/
```
