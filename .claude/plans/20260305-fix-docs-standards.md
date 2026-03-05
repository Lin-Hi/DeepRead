# 修复文档规范问题

**创建日期**: 2026-03-05
**状态**: 待用户确认

---

## Context（背景）

用户指出三个文档规范问题需要修复：

1. `tests/generate_test_canvas.py` 文件头不符合 L3 规范
2. `tests/CLAUDE.md` 需要更新以包含新文件
3. 项目根目录 `CLAUDE.md` 需要分类整理并添加项目结构内容

---

## 修复方案

### 1. 修复 `tests/generate_test_canvas.py` 文件头

**当前内容**:
```python
#!/usr/bin/env python3
"""
生成测试 Canvas 以验证 v3 布局效果
"""
```

**修复为**:
```python
#!/usr/bin/env python3
"""
/**
 * [IN]: json, pathlib, src.canvas_builder.CanvasBuilder
 * [OUT]: 生成测试 Canvas 文件以验证 v3 布局效果（手动运行脚本）
 * [POS]: 独立测试脚本，在 tests/ 目录中作为 Canvas 布局验证工具
 * [PROTOCOL]: 修改 canvas_builder.py 布局参数 -> 必须重新运行本脚本验证输出
 */
"""
```

### 2. 更新 `tests/CLAUDE.md`

在文件清单中添加 `generate_test_canvas.py`：

```
tests/
├── marker_benchmark.py        # [IN: PDF] [OUT: Markdown] - 验证 Marker/Surya 性能
├── test_pdf_preprocessing.py  # [IN: PDF, PyMuPDF] [OUT: PDF 属性状态] - 前置防线检测
├── test_dagre.py              # [IN: Canvas Nodes] [OUT: Layout Canvas JSON] - 测试布局算法并含 Fallback
├── test_llm.py                # [IN: Token API] [OUT: Summary JSON] - 测试阿里云百炼连接及 Token 长度限制
├── test_canvas_builder.py     # [IN: Summary Dict] [OUT: Canvas JSON 断言] - 针对 src/canvas_builder.py 的核心验证
├── generate_test_canvas.py    # [IN: CanvasBuilder] [OUT: Canvas 文件] - 手动运行验证 v3 布局效果
└── conftest.py                # [IN: pytest] [OUT: Fixtures] - pytest 全局 Fixtures 和环境模拟
```

### 3. 更新根目录 `CLAUDE.md`

按类别整理现有规则，添加项目结构信息：

**建议结构**:
```markdown
# DeepRead 项目（根目录 CLAUDE.md）

## 一、开发工作流规则
1. 在编写任何代码之前，先说明实现思路，并等待确认后再开始写代码。
2. 如果需求存在歧义，在编写任何代码之前先提出澄清问题。
...

## 二、分形文档索引规则
- 业务逻辑详见 `src/CLAUDE.md`
- 测试保障见 `tests/CLAUDE.md`
- 每次修改测试代码，必须更新 `tests/CLAUDE.md` 和被修改测试文件的 L3 头

## 三、项目结构概览
### Phase 完成状态
- Phase 1 (项目初始化): ✅ 完成
- Phase 1.5 (技术验证): ✅ 完成
- Phase 2 (核心功能开发): ✅ 完成
- Phase 3 (工作流整合): ⏳ 待开始

### Canvas 布局规范 (v3)
- 节点布局参数详见 `src/canvas_builder.py:_create_nodes()`
- 测试验证文件：`reports/canvas_schema_test_v4.canvas`

## 四、质量红线
...
```

---

## 清理任务

- [ ] 删除 `.claude/plans/20260305-phase3-integration-plan.md`（用户要求）
- [ ] 删除 `.claude/plans/modular-riding-yao.md`（命名不规范）
- [ ] 确认 `src/__pycache__/` 是否需要删除

---

## 验收标准

- [ ] `tests/generate_test_canvas.py` 文件头符合 L3 规范
- [ ] `tests/CLAUDE.md` 包含所有测试文件的清单
- [ ] 根目录 `CLAUDE.md` 分类清晰，包含项目状态信息
