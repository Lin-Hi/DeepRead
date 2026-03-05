"""
/**
 * [IN]: config.settings, utils, pathlib, json
 * [OUT]: CanvasBuilder 类 - 生成 Obsidian Canvas JSON 文件
 * [POS]: 被 main.py 调用，生成单文献知识卡片和总图谱 MasterMap
 * [PROTOCOL]: 修改节点布局 -> 更新 tests/test_canvas_builder.py
 */
"""
import json
from pathlib import Path
from typing import Optional

from src.config import settings
from src.utils import generate_node_id


class CanvasBuilder:
    """Canvas 生成器：创建 Obsidian Canvas 格式的知识图谱"""

    # 节点类型与边框颜色映射
    NODE_COLORS = {
        "metadata": "#3b82f6",      # 蓝色 - 文献元数据
        "research_question": "#f97316",  # 橙色 - 研究问题
        "methodology": "#8b5cf6",   # 紫色 - 方法论
        "findings": "#22c55e",      # 绿色 - 主要发现
        "limitations": "#ef4444",   # 红色 - 贡献与局限性
        "thoughts": "#6b7280",      # 灰色 - 个人思考
    }

    def __init__(self):
        self.node_width = settings.canvas_node_width
        self.node_height = settings.canvas_node_height
        # 增加间距以避免密集
        self.spacing_x = settings.canvas_node_spacing_x + 100  # 450
        self.spacing_y = settings.canvas_node_spacing_y + 150  # 400

    def create_paper_canvas(
        self,
        summary_data: dict,
        paper_folder: Path,
        paper_name: str
    ) -> Path:
        """
        为单篇文献创建知识卡片 Canvas

        Args:
            summary_data: AI 生成的 Summary 字典
            paper_folder: 文献文件夹路径
            paper_name: 文献名称（用于文件名）

        Returns:
            生成的 .canvas 文件路径
        """
        nodes, node_ids = self._create_nodes(summary_data)
        edges = self._create_edges(node_ids)

        canvas_data = {"nodes": nodes, "edges": edges}

        output_file = paper_folder / f"{paper_name}.canvas"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(canvas_data, f, indent=2, ensure_ascii=False)

        return output_file

    def _create_nodes(self, summary: dict) -> tuple[list, dict]:
        """创建固定模板布局的节点（基于手动优化的 v3 布局）"""
        # 参考 v3 手动调整：位置预定义 (x, y)
        positions = {
            "metadata": (0, 20),
            "methodology": (-25, 420),
            "research_question": (720, -55),
            "thoughts": (720, 940),
            "limitations": (0, 940),
            "findings": (720, 420),
        }

        # 根据 v3 调整的高度
        heights = {
            "metadata": 200,
            "methodology": 380,
            "research_question": 350,
            "thoughts": 320,
            "limitations": 320,
            "findings": 380,
        }
        
        # 根据 v3 调整的宽度
        widths = {
            "metadata": 300,
            "methodology": 350,
            "research_question": 350,
            "thoughts": 350,
            "limitations": 350,
            "findings": 350,
        }

        nodes = []
        node_ids = {}
        for node_type, (x, y) in positions.items():
            text = self._format_node_text(node_type, summary)
            height = heights.get(node_type, self.node_height)
            width = widths.get(node_type, self.node_width)
            
            node_id = generate_node_id(f"{node_type}_{summary.get('title', '')}")
            node_ids[node_type] = node_id

            nodes.append({
                "id": node_id,
                "type": "text",
                "x": x,
                "y": y,
                "width": width,
                "height": height,
                "text": text,
                "color": self.NODE_COLORS.get(node_type, "#6b7280")
            })

        return nodes, node_ids

    def _format_node_text(self, node_type: str, summary: dict) -> str:
        """格式化节点文本内容（中文标题）"""
        formatters = {
            "metadata": lambda s: (
                f"## 文献元数据\n\n"
                f"**{s.get('title', 'Untitled')}**\n\n"
                f"作者: {s.get('first_author', 'N/A')}\n"
                f"年份: {s.get('year', 'N/A')}\n"
                f"期刊: {s.get('journal', 'N/A')}\n\n"
                f"引用键: `{s.get('citekey', '')}`"
            ),
            "research_question": lambda s: (
                "## 研究问题\n\n"
                f"{s.get('research_gap_hypothesis', '无可用数据')[:800]}"
            ),
            "methodology": lambda s: (
                "## 方法论\n\n"
                f"{s.get('methodology', '无可用数据')[:1200]}"
            ),
            "findings": lambda s: (
                "## 主要发现\n\n"
                f"{s.get('key_findings', '无可用数据')[:1200]}"
            ),
            "limitations": lambda s: (
                "## 贡献与局限性\n\n"
                f"{s.get('critical_analysis', '无可用数据')[:600]}"
            ),
            "thoughts": lambda s: (
                "## 个人思考\n\n"
                f"{s.get('connections', '')[:400]}\n\n"
                f"**行动项:**\n{s.get('action_items', '')}"
            ),
        }

        formatter = formatters.get(node_type, lambda s: "No content")
        return formatter(summary)

    def _create_edges(self, node_ids: dict) -> list:
        """创建节点间的连接边（带标签和连接边位置）"""
        # 边定义：(from_node, from_side, to_node, to_side, label)
        edge_defs = [
            ("metadata", "right", "research_question", "left", "提出问题"),
            ("metadata", "bottom", "methodology", "top", "背景支撑"),
            ("research_question", "bottom", "findings", "top", "直接回答"),
            ("methodology", "right", "findings", "left", "得出发现"),
            ("findings", "left", "limitations", "top", "讨论局限"),
            ("findings", "bottom", "thoughts", "top", "启发思考"),
            ("limitations", "right", "thoughts", "left", "批判分析"),
            ("research_question", "left", "methodology", "right", "采用方法"),
        ]

        edges = []
        for i, (from_type, from_side, to_type, to_side, label) in enumerate(edge_defs):
            if from_type in node_ids and to_type in node_ids:
                edges.append({
                    "id": f"edge_{i}",
                    "fromNode": node_ids[from_type],
                    "fromSide": from_side,
                    "toNode": node_ids[to_type],
                    "toSide": to_side,
                    "label": label
                })

        return edges

    def update_master_map(
        self,
        literature_dir: Path,
        master_map_path: Optional[Path] = None
    ) -> Path:
        """
        更新总图谱 MasterMap.canvas

        Args:
            literature_dir: 01-Literature/ 目录路径
            master_map_path: 可选的自定义输出路径

        Returns:
            生成的 MasterMap.canvas 路径
        """
        if master_map_path is None:
            master_map_path = settings.knowledge_map_path / "MasterMap.canvas"

        # 扫描所有文献文件夹
        papers = self._scan_literature_folders(literature_dir)

        # 构建总图谱节点
        nodes = self._create_master_nodes(papers)
        edges = self._create_master_edges(papers)

        canvas_data = {"nodes": nodes, "edges": edges}

        with open(master_map_path, 'w', encoding='utf-8') as f:
            json.dump(canvas_data, f, indent=2, ensure_ascii=False)

        return master_map_path

    def _scan_literature_folders(self, literature_dir: Path) -> list:
        """扫描文献目录，获取所有已处理的论文"""
        papers = []

        if not literature_dir.exists():
            return papers

        for folder in literature_dir.iterdir():
            if folder.is_dir():
                summary_file = folder / "Summary.md"
                canvas_file = folder / f"{folder.name}.canvas"

                if summary_file.exists():
                    papers.append({
                        "folder": folder.name,
                        "path": folder,
                        "has_summary": True,
                        "has_canvas": canvas_file.exists()
                    })

        return papers

    def _create_master_nodes(self, papers: list) -> list:
        """为总图谱创建节点"""
        nodes = []

        for i, paper in enumerate(papers):
            # 网格布局：每行 3 个
            row = i // 3
            col = i % 3

            x = 50 + col * 400
            y = 50 + row * 250

            nodes.append({
                "id": f"paper_{i}",
                "type": "file",
                "file": str((paper["path"] / f"{paper['folder']}.canvas").relative_to(settings.root_dir)).replace("\\", "/"),
                "x": x,
                "y": y,
                "width": 350,
                "height": 200
            })

        return nodes

    def _create_master_edges(self, papers: list) -> list:
        """为总图谱创建关系边（预留接口）"""
        # TODO: 实现基于关键词相似度的自动连线
        return []
