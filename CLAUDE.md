# DeepRead 项目全局配置

本文件为项目 L1（全局地图）文档，定义开发工作流、项目状态和分形文档索引规则。

---

## 一、开发工作流规则

### 1.1 编码前规范
1. **先说明思路**：在编写任何代码之前，先说明实现思路，并等待确认后再开始写代码。
2. **澄清歧义**：如果需求存在歧义，在编写任何代码之前先提出澄清问题。
3. **任务拆分**：如果一个任务需要修改超过 3 个文件，先停下来把任务拆分成更小的子任务。

### 1.2 编码后规范
4. **边界测试**：完成代码编写后，列出可能的边界情况，并建议覆盖这些情况的测试用例。
5. **缺陷修复流程**：出现缺陷时，先编写一个能稳定复现该问题的测试，然后再修复代码，直到测试通过。
6. **错误反思**：每次被纠正时，回顾哪里做错了，并制定避免再次犯同类错误的具体方案。

### 1.3 Git 提交规范（⚠️ 强制执行）

> **严禁自动 push！** 任何涉及 `git commit` 或 `git push` 的操作，必须严格遵守以下流程：

1. **功能检查停止点**：完成代码修改后，**先停下来**，向用户报告变更内容，等待用户确认功能正确。
2. **Commit Message 审批**：拟写 commit message 后，**展示给用户审批**，用户明确同意后才能执行 `git commit`。
3. **Push 审批**：`git push` 同样需要用户明确指令，不得在用户未确认时自动 push。
4. **违规后果**：跳过上述任一步骤均视为违规，必须回滚并重新走审批流程。

---

## 二、分形文档索引规则

- **业务逻辑**：详见 [`src/CLAUDE.md`](src/CLAUDE.md)
- **测试保障**：详见 [`tests/CLAUDE.md`](tests/CLAUDE.md)
- **L3 文件头**：所有 `.py` 文件头部必须包含 `[IN]/[OUT]/[POS]/[PROTOCOL]` 契约注释
- **更新同步**：每次修改测试代码，必须更新 `tests/CLAUDE.md` 和被修改测试文件的 L3 头

---

## 三、项目状态概览

### Phase 完成进度
| Phase     | 名称         | 状态                                                     |
| --------- | ------------ | -------------------------------------------------------- |
| Phase 1   | 项目初始化   | ✅ 完成                                                   |
| Phase 1.5 | 技术验证     | ✅ 完成                                                   |
| Phase 2   | 核心功能开发 | ✅ 完成（所有源代码模块已创建）                           |
| Phase 3   | 工作流整合   | ✅ 完成（真实 PDF E2E 测试通过）                          |
| Phase 4   | 测试与优化   | ✅ 完成                                                   |
| Phase 5   | 边界用例测试 | ⏳ 进行中（系统极特殊防护与 Mock 已完成，算法层真实待补） |

### 核心模块清单
```
src/
├── main.py              # CLI 入口与工作流编排
├── pdf_processor.py     # PDF → Markdown (Marker)
├── summarizer.py        # LLM 调用与摘要生成
├── canvas_builder.py    # Canvas JSON 生成器
├── state_tracker.py     # 文献处理状态追踪
├── config.py            # 配置管理
├── exceptions.py        # 自定义异常
└── utils.py             # 工具函数
```

### Canvas 布局规范 (v3)
- **布局参数**：详见 [`src/canvas_builder.py:_create_nodes()`](src/canvas_builder.py)
- **节点类型**：6 个节点（文献元数据、研究问题、方法论、主要发现、贡献与局限性、个人思考）
- **边连接**：8 条带标签的边
- **参考文件**：[`reports/canvas_schema_test_v4.canvas`](reports/canvas_schema_test_v4.canvas)

---

## 四、质量红线

- 单文件行数 ≤ 800 行
- 单函数行数 ≤ 30 行
- 嵌套深度 ≤ 3 层
- 分支逻辑 ≤ 3 个

---

## 五、环境配置与踩坑记录

### Python 环境
- **必须使用 conda 环境**：`conda activate PY_3_10`
- **依赖安装**：使用 `pip install -r requirements.txt` 而非直接使用 pip（避免环境混乱）
- **模块导入问题**：若遇到 `ModuleNotFoundError`，首先检查是否激活了正确的 conda 环境

### 编码问题
- **Windows 终端编码**：输出中文时可能遇到 `UnicodeEncodeError: 'gbk' codec can't encode character`，应使用 ASCII 安全字符（如 `[OK]` 代替 `✓`）

### 文档规范
- **L3 文件头格式**：必须严格遵循 `[IN]/[OUT]/[POS]/[PROTOCOL]` 格式，参考现有测试文件
- **Plan 文件命名**：必须遵循 `YYYYMMDD-<功能简述>.md` 格式
- **文件读取后再编辑**：必须先 Read 再 Edit，不能假设文件已缓存

### 跑坑记录（Phase 3 新增）
- **marker_single 路径**：不能依赖系统 PATH，要用 `sys.executable.parent / 'Scripts' / 'marker_single.exe'` 动态定位
- **marker_single 参数**：使用 `--output_dir` 和 `--output_format`，不是 `--output`
- **文件重命名冲突**：当使用 `--force` 重复处理时，先用 `Path.unlink()` 删除已存在的目标文件再 rename
- **API 对齐**：`StateTracker` 函数名为 `compute_hash/is_processed/update_file_state`，非 `compute_file_hash/get_file_record`
- **Canvas 调用签名**：`create_paper_canvas(summary_dict, paper_folder: Path, paper_name: str)`
