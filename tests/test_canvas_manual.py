#!/usr/bin/env python3
"""
/**
 * [IN]: json, pathlib, src.canvas_builder.CanvasBuilder
 * [OUT]: 生成测试 Canvas 文件以验证 v3 布局效果（手动运行脚本）
 * [POS]: 独立测试脚本，在 tests/ 目录中作为 Canvas 布局验证工具
 * [PROTOCOL]: 修改 canvas_builder.py 布局参数 -> 必须重新运行本脚本验证输出
 */
"""
import json
from pathlib import Path
import sys

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.canvas_builder import CanvasBuilder


def main():
    # 创建测试数据
    summary_data = {
        'title': 'Test Paper for Layout Verification',
        'first_author': 'Test Author',
        'year': '2024',
        'journal': 'Test Journal',
        'citekey': 'Author2024Test',
        'research_gap_hypothesis': 'This is a test research gap description to verify the layout. ' * 5,
        'methodology': 'Test methodology with multiple steps:\n1. Step one\n2. Step two\n3. Step three\n' * 3,
        'key_findings': 'Key findings include:\n- Finding A\n- Finding B\n- Finding C\n' * 4,
        'critical_analysis': 'Strengths and limitations analysis goes here. ' * 4,
        'connections': 'Related to software engineering practices.',
        'action_items': '- [ ] Action item 1\n- [ ] Action item 2'
    }

    # 创建 CanvasBuilder 实例并生成 Canvas
    builder = CanvasBuilder()
    test_dir = Path('reports/test_canvas_v3')
    test_dir.mkdir(parents=True, exist_ok=True)

    output_file = builder.create_paper_canvas(summary_data, test_dir, 'test_layout_v3')
    print(f'✓ Test Canvas generated: {output_file}')

    # 读取并显示关键信息
    with open(output_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f'\n=== Generated Canvas Summary ===')
    print(f'Nodes: {len(data["nodes"])}')
    print(f'Edges: {len(data["edges"])}')
    print('\nNode positions and sizes:')
    for node in data['nodes']:
        text_preview = node['text'][:20].replace('\n', ' ')
        print(f'  {text_preview:25} x:{node["x"]:6} y:{node["y"]:6} w:{node["width"]:4} h:{node["height"]:4}')

    print('\nEdge connections:')
    for edge in data['edges']:
        print(f'  {edge["fromNode"][:15]:15} -> {edge["toNode"][:15]:15} ({edge.get("label", "no label")})')

    print('\n=== Node Content Preview ===')
    for node in data['nodes']:
        title = node['text'].split('\n')[0] if node['text'] else 'Empty'
        print(f'\n{title}:')
        print(f'  Color: {node.get("color", "default")}')


if __name__ == '__main__':
    main()
