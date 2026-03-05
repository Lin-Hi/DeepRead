# tests/ 模块（测试与验证平台）

本目录包含 DeepRead 项目的所有测试代码，作为系统稳定性和质量的主观断点屏障。

## 模块职责 (Responsibilities)
1. **自动化验收**：对各核心模块进行单元测试、集成测试、端到端测试。
2. **技术储备验证**：承载 Phase 1.5 中的库兼容性、API 限流、第三方算法边界验证脚本。
3. **缺陷溯源靶场**：任何 Bug 修复前，必须先在此处建立稳定复现该问题的测试用例。

## 文件与接口清单 (Interfaces)

```
tests/
├── marker_benchmark.py        # [IN: PDF] [OUT: Markdown] - 验证 Marker/Surya 性能
├── test_pdf_preprocessing.py  # [IN: PDF, PyMuPDF] [OUT: PDF 属性状态] - 前置防线检测
├── test_dagre.py              # [IN: Canvas Nodes] [OUT: Layout Canvas JSON] - 测试布局算法并含 Fallback
├── test_llm.py                # [IN: Token API] [OUT: Summary JSON] - 测试阿里云百炼连接及 Token 长度限制
├── test_canvas_builder.py     # [IN: Summary Dict] [OUT: Canvas JSON 断言] - 针对 src/canvas_builder.py 的核心验证
├── test_e2e_workflow.py       # [IN: Mock PDF+LLM] [OUT: 全链路断言] - 模拟测试全部通过 (process_single_pdf)
├── generate_test_canvas.py    # [IN: CanvasBuilder] [OUT: Canvas 文件] - 手动运行验证 v3 布局效果
└── conftest.py                # [IN: pytest] [OUT: Fixtures] - pytest 全局 Fixtures 和环境模拟
```

## 被谁消费 (Consumers)
1. **开发者 / Claude Agent**：在每次功能迭代（修改 `src/`）前后强制运行。
2. **CI/CD Pipeline**（未来）：自动化回归测试。

## 测试运行协议 (Execution Protocol)

### 验证全量/集成分支
```bash
# 激活环境
conda activate PY_3_10

# 运行全量测试
python -m pytest tests/ -v
```

### 质量红线约束 (Quality Red Lines)
1. 任何 `test_*.py` 中的测试函数嵌套层次不得超过 3 层。
2. 若新增业务逻辑功能而未补充相关测试代码，将在 CLAUDE.md 的代码审查环节被直接阻断。
3. 此目录下创建的所有 `.py` 文件，头部仍然必须遵守全局 L3 `[IN]/[OUT]/[POS]/[PROTOCOL]` 契约约束。

## 测试数据边界 (Fixtures Setup)
- **真实 PDF 测试**：`input-pdfs/` 目录下包含多种论文样本（单栏/双栏/公式/KTH 确相）
- **E2E Mock 测试**：`test_e2e_workflow.py` 中使用 `MagicMock` 隔离外部依赖，全部 3 个测试用例通过
- 若未来扩展外部数据（如图片），请建立 `tests/fixtures/` 目录统一管理
