# DeepRead 项目规划 v6.0 - 工作流整合与全量测试计划

**创建日期**: 20260305
**状态**: 待审查
**关联计划**: 20260304-deepread-plan-v5.md
**目标**: 推进 Phase 3（工作流整合）、Phase 4（测试与优化）及 Phase 5（边界用例测试）的全面实施。

---

## 核心任务与 Checklist

### Phase 3: 工作流整合 (Workflow Integration)

- [ ] **3.1 端到端流程测试与错误处理验证**
  - [ ] 编写并运行 `tests/test_e2e_workflow.py`：模拟从输入单篇 PDF 到生成 Markdown、请求 Summary 及创建 Canvas 的全链路。
  - [ ] 验证在关键节点（如 PDF 解析失败、LLM 返回错误 JSON、网络超时等）引发 `DeepReadError` 及子异常的过程。
  - [ ] 验证 `main.py` 的错误汇总报告（Summary Report）能够正确捕捉并输出失败情况和对应的错误码。
  - [ ] 检查并验证控制台与文件（`logs/`）双目标志输出格式及回溯信息的完整性。
- [ ] **3.2 依赖管理与环境锁定**
  - [ ] 使用 `pip freeze` 检查并更新 `requirements.txt`（明确标注核心模块版本：marker-pdf, surya-ocr, pydantic-settings, dashscope, dagre-python 等）。
  - [ ] 补充可选依赖（GPU 加速、测试工具如 pytest 等）说明至 README 环境配置文档中。

### Phase 4: 测试与优化 (Testing & Optimization)

- [ ] **4.1 单元测试完善（使用 pytest）**
  - [ ] `tests/test_pdf_processor.py`: 断言 Marker 对正常/含公式/双栏PDF文件的输出文本。
  - [ ] `tests/test_summarizer.py`: Mock API 调用，验证 `validate_summary` 函数和重试机制（指数退避）。
  - [ ] `tests/test_state_tracker.py`: 验证 `.deepread/state.json` 增量更新、原子写入以及 UNNAMED 计数器正确性。
  - [ ] `tests/test_config.py`: 验证配置项覆盖及环境变量 (.env) 的默认读取逻辑。
- [ ] **4.2 系统级优化**
  - [ ] 审查 `summarizer.py` 并确保合并API请求的批量调用策略真正落实。
  - [ ] 调整 `dagre-python` 布局参数使得图表节点不重叠且美观（若必要，微调 `canvas_builder.py` 内部布局坐标换算）。

### Phase 5: 边界用例测试 (Edge Case Testing)

- [ ] **5.1 异常 PDF 与输入边界**
  - [ ] 准备加密的 PDF 及极小/损坏 PDF 文件用于测试。
  - [ ] 验证系统正常跳过异常文件并在 state.json 标记其处理失败，记录对应日志而不会导致程序崩溃。
- [ ] **5.2 LLM 等外部依赖异常**
  - [ ] 编写测试 Mock LLM 返回缺失核心字段（如 `citekey`，`hypothesis`）的情况，测试代码的自动验证与重试行为。
- [ ] **5.3 增量更新冲突与并发处理**
  - [ ] 测试覆盖相同文献、修改现有文献（改变 hash 摘要）等行为，验证再次运行 `main.py --batch` 能进行正确的覆盖与输出追踪。

---

## 对应代码/文档调整协议 (Protocol)
- 遵循红线规定：单文件行数 ≤ 800 行，单函数行数 ≤ 30 行，逻辑/嵌套 ≤ 3。
- 测试脚本的 L3 文件头必须符合 `[IN]/[OUT]/[POS]/[PROTOCOL]` 契约约束。
- 自动化实施完毕后，更新 `tests/CLAUDE.md` 及全局 `CLAUDE.md` 的 Phase 完成进度标记。

## 下一步行动
等待用户审阅本次 Plan (5+ 轮质疑与补全循环开始)。评审通过后，我们将按照以上列表逐步实施并持久化状态。
