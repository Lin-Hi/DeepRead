# Dagre 布局测试报告

**测试日期**: 2026-03-04
**测试环境**: Windows 11, Python 3.10.14 (Conda PY_3_10)

---

## 测试结果摘要

| 测试项 | 状态 | 说明 |
|--------|------|------|
| dagre-python 安装 | ❌ 失败 | 包不存在于 PyPI |
| networkx 可用性 | ✅ 通过 | 已安装 v3.4.2，可作为替代 |
| Fallback 固定模板 | ✅ 通过 | 正常生成 Canvas 文件 |

---

## 详细分析

### 1. dagre-python 不可用

**问题**: `pip install dagre-python` 返回错误：
```
ERROR: Could not find a version that satisfies the requirement dagre-python
```

**原因分析**:
- dagre-python 可能已从 PyPI 移除或从未发布
- 或者正确的包名是其他名称（如 `dagre`, `pydagre` 等）

**尝试过的包名**:
- [x] dagre-python ❌
- [ ] dagre (待测试)
- [ ] pydagre (待测试)

### 2. 替代方案：NetworkX + Graphviz

由于 dagre-python 不可用，推荐使用以下替代方案：

#### 方案 A: NetworkX 内置布局

```python
import networkx as nx

# 创建有向图
G = nx.DiGraph()
G.add_edges_from([
    ("metadata", "research_question"),
    ("metadata", "methodology"),
    ("research_question", "findings"),
    ("methodology", "findings"),
])

# 使用层次布局
pos = nx.nx_agraph.graphviz_layout(G, prog='dot')
```

**优点**:
- NetworkX 已安装，无需额外依赖
- 支持多种布局算法（dot, neato, fdp 等）

**缺点**:
- 需要单独安装 Graphviz 二进制程序

#### 方案 B: 手动层次布局算法

实现一个简单的自上而下的分层布局：

```python
def simple_hierarchical_layout(nodes, edges, level_map):
    """
    简单的层次布局算法
    level_map: {'node_id': level_number}
    """
    positions = {}
    level_width = 400
    node_height = 200
    level_height = 300

    for node_id, level in level_map.items():
        # 计算该层节点数量
        nodes_in_level = [n for n, l in level_map.items() if l == level]
        index = nodes_in_level.index(node_id)

        x = 50 + index * level_width
        y = 50 + level * level_height
        positions[node_id] = (x, y)

    return positions
```

#### 方案 C: 固定模板布局（推荐作为 Fallback）

预定义的布局位置（已在代码中实现）：

```
┌───────────────┐     ┌───────────────┐
│  文献元数据    │────▶│   研究问题    │
│   (50,50)     │     │   (400,50)    │
└───────────────┘     └───────────────┘
         │                      │
         ▼                      ▼
┌───────────────┐     ┌───────────────┐
│    方法论      │────▶│   主要发现    │
│   (50,300)    │     │   (400,300)   │
└───────────────┘     └───────────────┘
         │                      │
         ▼                      ▼
┌───────────────┐     ┌───────────────┐
│ 贡献与局限性   │────▶│   个人思考    │
│   (50,550)    │     │   (400,550)   │
└───────────────┘     └───────────────┘
```

---

## 建议的实现策略

### 阶段 1: 使用固定模板布局（当前推荐）

直接使用预定义的固定布局，确保稳定性：

```python
# src/canvas_builder.py
def generate_fixed_layout_nodes():
    positions = {
        "metadata": (50, 50),
        "research_question": (400, 50),
        "methodology": (50, 300),
        "findings": (400, 300),
        "limitations": (50, 550),
        "thoughts": (400, 550),
    }
    # ... 生成节点
```

### 阶段 2: 集成 Graphviz（可选增强）

如果需要更美观的布局，可以：

1. 安装 Graphviz 二进制：`choco install graphviz` (Windows)
2. 安装 Python 绑定：`pip install pygraphviz`
3. 使用 dot 布局算法

### 阶段 3: 自定义布局算法（未来优化）

基于力导向或层次布局原理，实现轻量级布局算法。

---

## Fallback 布局验证

✅ **已通过测试**:
- [x] 6 个节点正确放置
- [x] 8 条边正确连接
- [x] 无节点重叠
- [x] 生成的 Canvas 文件可在 Obsidian 中打开

**生成的测试文件**:
- `reports/dagre_fallback_template.canvas` - 固定模板布局示例

---

## 结论与行动计划

### 结论

1. **dagre-python 不可用**，无法使用原计划中的自动布局库
2. **固定模板布局可行**，能满足基本需求
3. **networkx + graphviz** 可作为进阶替代方案

### 行动计划

1. **立即实施**: 使用固定模板布局完成 Phase 2 开发
2. **后续优化**: 如有需要，集成 graphviz 提供更美观的布局
3. **文档更新**: 在 canvas_builder.py 中记录布局策略选择

---

## 参考

- [NetworkX Documentation](https://networkx.org/documentation/stable/)
- [Graphviz Download](https://graphviz.org/download/)
- [ELK.js](https://github.com/kieler/elkjs) - JavaScript 实现的 ELK 布局算法（Obsidian 内部可能使用）
