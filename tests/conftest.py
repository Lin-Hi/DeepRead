"""
/**
 * [IN]: pytest fixtures, pathlib, tempfile
 * [OUT]: 全局 pytest fixtures（如临时目录、模拟数据等）
 * [POS]: pytest 自动加载，供所有测试函数共享
 * [PROTOCOL]: 新增 fixture -> 更新本文件头部 IN 依赖列表
 */
"""
import pytest
from pathlib import Path
import tempfile
import shutil


@pytest.fixture
def temp_output_dir():
    """提供临时输出目录，测试结束后自动清理"""
    temp_dir = tempfile.mkdtemp(prefix="deepread_test_")
    yield Path(temp_dir)
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def sample_summary_data():
    """提供示例 Summary 数据用于测试"""
    return {
        "title": "Test Paper Title",
        "first_author": "John Doe",
        "year": "2023",
        "journal": "Test Journal",
        "citekey": "Doe2023Test",
        "abstract": "This is a test abstract for testing purposes.",
        "research_gap_hypothesis": "The core research gap is the lack of testing frameworks.",
        "methodology": "We used unit testing and integration testing.",
        "key_findings": "All tests passed successfully with 100% coverage.",
        "critical_analysis": "Strengths: comprehensive. Limitations: synthetic data.",
        "connections": "Related to software engineering best practices.",
        "action_items": "- [ ] Run more tests\n- [ ] Add edge cases"
    }
