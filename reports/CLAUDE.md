# DeepRead Reports

本目录包含 DeepRead 项目的技术验证报告和文档。

## 文件结构

```
reports/
├── design/                       # 架构设计与策略推演文档
│   ├── phase1.5-summary.md
│   ├── llm-request-strategy.md
│   ├── obsidian-canvas-schema.md
│   └── state-tracker-design.md
├── testing/                      # 各模块及自动化边角测试报告
│   ├── edge_case_testing_report.md
│   ├── marker-benchmark.md
│   ├── pdf-preprocessing-check.md
│   ├── dagre-layout-test.md
│   └── canvas_schema_test*.canvas
└── templates/                    # 各类固定生成的后备排版结构
    └── dagre_fallback_template.canvas
```

## 报告分类明细

### 1. 技术设计与策略 (design)
| 报告                        | 内容                           |
| --------------------------- | ------------------------------ |
| `phase1.5-summary.md`       | Phase 1.5 原型评估整体总结     |
| `llm-request-strategy.md`   | 大模型（阿里百炼）接入策略设计 |
| `obsidian-canvas-schema.md` | Obsidian 画板 JSON Schema 分析 |
| `state-tracker-design.md`   | 原子写入与防冲突状态机设计     |

### 2. 测试验收报告 (testing)
| 报告                          | 对象                                                   |
| ----------------------------- | ------------------------------------------------------ |
| `edge_case_testing_report.md` | ✅ **Phase 5** 的文件损坏、大文件及限速阻断极限防护结果 |
| `marker-benchmark.md`         | 验证多级 PDF 引擎的耗时表现                            |
| `pdf-preprocessing-check.md`  | PyMuPDF 对于密码及空白 PDF 识别验证                    |
| `dagre-layout-test.md`        | DAG 节点重叠分离自动布局算法打磨                       |

### 3. 可视化模板库 (templates)
- `dagre_fallback_template.canvas` - 用于发生布局降级时的稳定静态备用骨架。

## 变更协议

- 新增技术验证 → 添加报告文件并更新本列表
- 更新测试数据 → 保留历史版本，注明日期
- 修改设计决策 → 在报告中记录变更原因
