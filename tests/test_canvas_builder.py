"""
/**
 * [IN]: json, pathlib, src.canvas_builder.CanvasBuilder
 * [OUT]: 验证 CanvasBuilder 的节点生成（附带手动 v3 布局校验）及边连接正确性
 * [POS]: 作为 src/canvas_builder.py 的单元测试
 * [PROTOCOL]: 修改 canvas_builder.py 模板布局 -> 必须同步更新本文件的验证断言
 */
"""
import json
from pathlib import Path

from src.canvas_builder import CanvasBuilder


def test_canvas_builder_v3_layout(tmp_path):
    """测试 CanvasBuilder 的固定 v3 布局生成逻辑"""
    builder = CanvasBuilder()
    
    summary_data = {
        "title": "Test Title",
        "first_author": "John Doe",
        "year": "2023",
        "citekey": "Doe2023",
        "methodology": "Test method",
        "key_findings": "Test findings"
    }

    output_file = builder.create_paper_canvas(summary_data, tmp_path, "TestPaper")
    
    assert output_file.exists()
    
    with open(output_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    assert "nodes" in data
    assert "edges" in data
    
    # 验证生成的 6 个节点
    assert len(data["nodes"]) == 6
    texts = [n["text"] for n in data["nodes"]]
    assert any("## 文献元数据" in t for t in texts)
    assert any("## 研究问题" in t for t in texts)
    assert any("## 方法论" in t for t in texts)
    assert any("## 主要发现" in t for t in texts)
    assert any("## 贡献与局限性" in t for t in texts)
    assert any("## 个人思考" in t for t in texts)
    
    # 验证新加入的 width 和 height 特性
    metadata_node = next(n for n in data["nodes"] if "## 文献元数据" in n["text"])
    assert metadata_node["width"] == 300
    assert metadata_node["height"] == 200
    
    methodology_node = next(n for n in data["nodes"] if "## 方法论" in n["text"])
    assert methodology_node["width"] == 350
    assert methodology_node["height"] == 380
    
    # 验证 edges 都包含 fromSide 和 toSide
    assert len(data["edges"]) == 8
    for edge in data["edges"]:
        assert "fromSide" in edge
        assert "toSide" in edge
