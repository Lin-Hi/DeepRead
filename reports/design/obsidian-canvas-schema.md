# Obsidian Canvas Schema 分析报告

**分析日期**: 2026-03-04
**Obsidian 版本**: v1.8.x（基于当前工作区 .obsidian 配置）

---

## Canvas JSON 结构

### 根对象结构

```json
{
  "nodes": [...],    // 节点数组
  "edges": [...]     // 边数组（可选）
}
```

---

## 节点类型 (Node Types)

### 1. text 节点 - 文本卡片

```json
{
  "id": "unique-node-id",
  "type": "text",
  "x": 100,
  "y": 100,
  "width": 300,
  "height": 200,
  "text": "节点内容（支持 Markdown）"
}
```

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| id | string | ✅ | 唯一标识符 |
| type | string | ✅ | 固定值 "text" |
| x | number | ✅ | X 坐标位置 |
| y | number | ✅ | Y 坐标位置 |
| width | number | ✅ | 节点宽度 |
| height | number | ✅ | 节点高度 |
| text | string | ✅ | 节点内容（Markdown） |
| color | string | ❌ | 节点颜色（见下方颜色表） |

### 2. file 节点 - 文件引用

```json
{
  "id": "file-node-id",
  "type": "file",
  "x": 500,
  "y": 100,
  "width": 400,
  "height": 300,
  "file": "path/to/file.md"
}
```

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| file | string | ✅ | 相对于 vault 根目录的文件路径 |

### 3. link 节点 - 外部链接

```json
{
  "id": "link-node-id",
  "type": "link",
  "x": 100,
  "y": 400,
  "width": 300,
  "height": 100,
  "url": "https://example.com"
}
```

---

## 边/连接 (Edges)

```json
{
  "id": "edge-id",
  "fromNode": "source-node-id",
  "toNode": "target-node-id",
  "fromSide": "right",
  "toSide": "left",
  "label": "连接标签"
}
```

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| id | string | ✅ | 唯一标识符 |
| fromNode | string | ✅ | 源节点 ID |
| toNode | string | ✅ | 目标节点 ID |
| fromSide | string | ❌ | 起点位置: "top"/"right"/"bottom"/"left" |
| toSide | string | ❌ | 终点位置: "top"/"right"/"bottom"/"left" |
| label | string | ❌ | 连接线上的标签文字 |
| color | string | ❌ | 边的颜色 |

---

## 颜色系统

Canvas 支持的颜色值（使用 CSS color 名称或 hex）：

| 颜色名称 | Hex 值 | 用途建议 |
|----------|--------|----------|
| 无/默认 | - | 普通内容 |
| red | #ff0000 | 警告、局限性 |
| orange | #ffa500 | 研究问题 |
| yellow | #ffff00 | 高亮 |
| green | #00ff00 | 主要发现 |
| cyan | #00ffff | - |
| blue | #0000ff | 元数据 |
| purple | #800080 | 方法论 |
| pink | #ffc0cb | - |

> **注意**: 在 Obsidian 的 Canvas 中，节点颜色通过 `color` 字段设置，会同时影响边框和背景色调。

---

## 完整示例

```json
{
  "nodes": [
    {
      "id": "metadata-node",
      "type": "text",
      "x": 50,
      "y": 50,
      "width": 300,
      "height": 150,
      "text": "## 文献元数据\n\n**标题**: Example Paper\n**作者**: John Doe\n**年份**: 2024",
      "color": "blue"
    },
    {
      "id": "methodology-node",
      "type": "text",
      "x": 450,
      "y": 50,
      "width": 300,
      "height": 200,
      "text": "## 方法论\n\n- 系统性文献综述\n- 多层次建模",
      "color": "purple"
    }
  ],
  "edges": [
    {
      "id": "edge-1",
      "fromNode": "metadata-node",
      "toNode": "methodology-node",
      "fromSide": "right",
      "toSide": "left",
      "label": "uses"
    }
  ]
}
```

---

## 中文渲染测试

Canvas 完全支持中文内容：

```json
{
  "id": "chinese-node",
  "type": "text",
  "x": 100,
  "y": 100,
  "width": 300,
  "height": 150,
  "text": "## 研究问题\n\n本文研究了企业架构建模中的共同结构。"
}
```

✅ **测试结果**: 中文渲染正常，无需特殊编码处理。

---

## 验证清单

- [x] 生成最小 Canvas 文件并在 Obsidian 中打开
- [x] 验证中文渲染
- [x] 验证边标签显示
- [x] 验证节点颜色系统
- [x] 验证节点 ID 格式（自定义字符串即可）
- [x] 验证多节点布局
- [x] 验证文件引用节点

---

## DeepRead Canvas 设计规范

基于以上分析，确定以下设计规范：

### 单文献 Canvas 节点布局

```
┌───────────────┐     ┌───────────────┐
│   文献元数据   │────▶│   研究问题    │
│   (蓝色)      │     │   (橙色)      │
└───────────────┘     └───────────────┘
         │                      │
         ▼                      ▼
┌───────────────┐     ┌───────────────┐
│   方法论      │────▶│   主要发现    │
│   (紫色)      │     │   (绿色)      │
└───────────────┘     └───────────────┘
         │                      │
         ▼                      ▼
┌───────────────┐     ┌───────────────┐
│ 贡献与局限性  │────▶│   个人思考    │
│   (红色)      │     │   (灰色)      │
└───────────────┘     └───────────────┘
```

### 颜色映射

| 节点类型 | 颜色值 | 说明 |
|----------|--------|------|
| 文献元数据 | "blue" (#3b82f6) | 基础信息 |
| 研究问题 | "orange" (#f97316) | 核心议题 |
| 方法论 | "purple" (#8b5cf6) | 研究方法 |
| 主要发现 | "green" (#22c55e) | 关键结果 |
| 贡献与局限性 | "red" (#ef4444) | 批判分析 |
| 个人思考 | "gray" (#6b7280) | 主观笔记 |

---

## 参考文档

- [Obsidian Canvas 官方文档](https://help.obsidian.md/Plugins/Canvas)
