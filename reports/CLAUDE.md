# DeepRead Reports

本目录包含 DeepRead 项目的技术验证报告和文档。

## 文件结构

```
reports/
├── phase1.5-summary.md           # Phase 1.5 技术验证总结
├── marker-benchmark.md           # Marker PDF 转换基准测试报告
├── obsidian-canvas-schema.md     # Obsidian Canvas JSON Schema 分析
├── llm-request-strategy.md       # LLM API 请求策略设计
├── state-tracker-design.md       # state.json 状态追踪设计
├── dagre-layout-test.md          # 节点布局算法测试报告
├── pdf-preprocessing-check.md    # PDF 预处理验证报告
├── canvas_schema_test.canvas     # Canvas Schema 测试文件
├── dagre_fallback_template.canvas # Fallback 布局模板
└── marker_test_*/                # Marker 转换测试输出目录
```

## 报告分类

### 技术验证报告 (Phase 1.5)

| 报告 | 内容 | 结论 |
|------|------|------|
| `marker-benchmark.md` | Marker CPU 模式性能测试 | ✅ 85页论文10-15秒，满足需求 |
| `obsidian-canvas-schema.md` | Canvas JSON 格式分析 | ✅ Schema 已确认，支持颜色/标签 |
| `llm-request-strategy.md` | 阿里百炼 API 设计 | ⚠️ 需配置 Key 后测试 |
| `state-tracker-design.md` | state.json 结构设计 | ✅ 原子写入、增量更新 |
| `dagre-layout-test.md` | 自动布局算法验证 | ⚠️ dagre-python 不可用，改用固定模板 |
| `pdf-preprocessing-check.md` | PDF 异常检测验证 | ✅ PyMuPDF 可检测加密/损坏/空文件 |

### 项目文档

| 报告 | 用途 |
|------|------|
| `phase1.5-summary.md` | Phase 1.5 整体总结，下一步行动指南 |

### 测试输出

- `marker_test_FULLTEXT01/` - Marker 转换结果示例（Markdown + 图片）
- `canvas_schema_test.canvas` - 可在 Obsidian 中打开的测试文件
- `dagre_fallback_template.canvas` - 固定模板布局示例

## 变更协议

- 新增技术验证 → 添加报告文件并更新本列表
- 更新测试数据 → 保留历史版本，注明日期
- 修改设计决策 → 在报告中记录变更原因
