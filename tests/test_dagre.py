#!/usr/bin/env python3
"""
/**
 * [IN]: json, pathlib, dagre (可选)
 * [OUT]: 测试 dagre-python 的算法重叠处理以及 fallback 模板是否能生成 Canvas JSON
 * [POS]: 技术验证脚本（Phase 1.5），用于保证引入新布局策略前的安全验证
 * [PROTOCOL]: 若改变 node_ids 或 canvas layout params -> 更新被测试模拟的 graph
 */
"""
import json
from pathlib import Path


def test_dagre_layout():
    """测试 dagre 布局算法"""
    print("=== Dagre Layout Test ===\n")

    try:
        # 尝试导入 dagre
        import dagre
        print("[OK] dagre-python imported successfully")
    except ImportError:
        print("[FAIL] dagre-python not installed")
        print("Install: pip install dagre-python")
        return False

    # 创建测试图（模拟单文献 Canvas 的 6 节点 8 边）
    graph = {
        "id": "root",
        "layoutOptions": {
            "elk.algorithm": "layered",
            "elk.direction": "DOWN",
            "elk.spacing.nodeNode": "50",
            "elk.layered.spacing.nodeNodeBetweenLayers": "80",
        },
        "children": [
            {"id": "metadata", "width": 300, "height": 150, "labels": [{"text": "文献元数据"}]},
            {"id": "research_question", "width": 300, "height": 150, "labels": [{"text": "研究问题"}]},
            {"id": "methodology", "width": 300, "height": 200, "labels": [{"text": "方法论"}]},
            {"id": "findings", "width": 300, "height": 200, "labels": [{"text": "主要发现"}]},
            {"id": "limitations", "width": 300, "height": 150, "labels": [{"text": "贡献与局限性"}]},
            {"id": "thoughts", "width": 300, "height": 150, "labels": [{"text": "个人思考"}]},
        ],
        "edges": [
            {"id": "e1", "sources": ["metadata"], "targets": ["research_question"]},
            {"id": "e2", "sources": ["metadata"], "targets": ["methodology"]},
            {"id": "e3", "sources": ["research_question"], "targets": ["findings"]},
            {"id": "e4", "sources": ["methodology"], "targets": ["findings"]},
            {"id": "e5", "sources": ["findings"], "targets": ["limitations"]},
            {"id": "e6", "sources": ["findings"], "targets": ["thoughts"]},
            {"id": "e7", "sources": ["limitations"], "targets": ["thoughts"]},
            {"id": "e8", "sources": ["research_question"], "targets": ["methodology"]},
        ]
    }

    print(f"测试图配置:")
    print(f"  - 节点数: {len(graph['children'])}")
    print(f"  - 边数: {len(graph['edges'])}")
    print(f"  - 布局方向: DOWN (自上而下)")
    print()

    try:
        # 执行布局
        layout_result = dagre.layout(graph)
        print("[OK] 布局计算成功\n")

        # 提取节点位置
        print("节点布局结果:")
        for node in layout_result["children"]:
            x = node.get("x", 0)
            y = node.get("y", 0)
            width = node.get("width", 0)
            height = node.get("height", 0)
            label = node["labels"][0]["text"] if node.get("labels") else node["id"]
            print(f"  {label:15} -> x: {x:6.1f}, y: {y:6.1f}, w: {width}, h: {height}")

        # 检查节点重叠
        print("\n重叠检测:")
        nodes = layout_result["children"]
        overlaps = []
        for i, n1 in enumerate(nodes):
            for n2 in nodes[i+1:]:
                x1, y1, w1, h1 = n1["x"], n1["y"], n1["width"], n1["height"]
                x2, y2, w2, h2 = n2["x"], n2["y"], n2["width"], n2["height"]

                # 检查矩形重叠
                if (abs(x1 - x2) * 2 < (w1 + w2)) and (abs(y1 - y2) * 2 < (h1 + h2)):
                    overlaps.append((n1["id"], n2["id"]))

        if overlaps:
            print(f"  [WARN]  发现 {len(overlaps)} 处重叠:")
            for o in overlaps:
                print(f"     - {o[0]} vs {o[1]}")
        else:
            print("  [OK] 无节点重叠")

        # 转换为 Obsidian Canvas 格式
        canvas_nodes = []
        for node in layout_result["children"]:
            canvas_nodes.append({
                "id": node["id"],
                "type": "text",
                "x": node["x"] - node["width"] / 2,  # dagre 中心坐标转左上角
                "y": node["y"] - node["height"] / 2,
                "width": node["width"],
                "height": node["height"],
                "text": node["labels"][0]["text"] if node.get("labels") else ""
            })

        canvas_edges = []
        for edge in layout_result.get("edges", []):
            canvas_edges.append({
                "id": edge["id"],
                "fromNode": edge["sources"][0],
                "toNode": edge["targets"][0]
            })

        canvas_data = {
            "nodes": canvas_nodes,
            "edges": canvas_edges
        }

        # 保存测试输出
        output_file = Path("reports/dagre_test_output.canvas")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(canvas_data, f, indent=2, ensure_ascii=False)

        print(f"\n[OK] Canvas 文件已生成: {output_file}")
        print(f"   节点数: {len(canvas_nodes)}, 边数: {len(canvas_edges)}")

        return True

    except Exception as e:
        print(f"[FAIL] 布局计算失败: {e}")
        return False


def test_fallback_layout():
    """测试 fallback 固定模板布局"""
    print("\n=== Fallback 固定模板布局测试 ===\n")

    # 预定义位置（当 dagre 失败时使用）
    positions = {
        "metadata": (50, 50),
        "research_question": (400, 50),
        "methodology": (50, 300),
        "findings": (400, 300),
        "limitations": (50, 550),
        "thoughts": (400, 550),
    }

    sizes = {
        "metadata": (300, 150),
        "research_question": (300, 150),
        "methodology": (300, 200),
        "findings": (300, 200),
        "limitations": (300, 150),
        "thoughts": (300, 150),
    }

    labels = {
        "metadata": "文献元数据",
        "research_question": "研究问题",
        "methodology": "方法论",
        "findings": "主要发现",
        "limitations": "贡献与局限性",
        "thoughts": "个人思考",
    }

    edges = [
        ("metadata", "research_question"),
        ("metadata", "methodology"),
        ("research_question", "findings"),
        ("methodology", "findings"),
        ("findings", "limitations"),
        ("findings", "thoughts"),
        ("limitations", "thoughts"),
        ("research_question", "methodology"),
    ]

    print("固定布局位置:")
    for node_id, (x, y) in positions.items():
        w, h = sizes[node_id]
        print(f"  {labels[node_id]:15} -> x: {x:4}, y: {y:4}, w: {w}, h: {h}")

    # 生成 Canvas 文件
    canvas_nodes = []
    for node_id, (x, y) in positions.items():
        w, h = sizes[node_id]
        canvas_nodes.append({
            "id": node_id,
            "type": "text",
            "x": x,
            "y": y,
            "width": w,
            "height": h,
            "text": labels[node_id]
        })

    canvas_edges = []
    for i, (from_node, to_node) in enumerate(edges):
        canvas_edges.append({
            "id": f"edge_{i}",
            "fromNode": from_node,
            "toNode": to_node
        })

    canvas_data = {
        "nodes": canvas_nodes,
        "edges": canvas_edges
    }

    output_file = Path("reports/templates/dagre_fallback_template.canvas")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(canvas_data, f, indent=2, ensure_ascii=False)

    print(f"\n[OK] Fallback Canvas 文件已生成: {output_file}")


if __name__ == "__main__":
    success = test_dagre_layout()
    test_fallback_layout()

    print("\n" + "="*50)
    if success:
        print("结论: dagre-python 可用，推荐使用自动布局")
    else:
        print("结论: dagre-python 不可用，将使用固定模板布局作为 fallback")
