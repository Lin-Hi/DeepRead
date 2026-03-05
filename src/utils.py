"""
/**
 * [IN]: pathlib, hashlib, re, unicodedata, logging
 * [OUT]: 工具函数集 - 文件操作、日志配置、文件名规范化、节点ID生成等
 * [POS]: 被 pdf_processor, summarizer, canvas_builder 等模块调用
 * [PROTOCOL]: 新增工具函数 -> 添加单元测试 -> 更新本文档
 */
"""
import hashlib

import re
import shutil
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Optional

from .config import settings





def compute_file_hash(file_path: Path) -> str:
    """
    计算文件的 SHA256 hash

    Args:
        file_path: 文件路径

    Returns:
        SHA256 hash 字符串（前16位）
    """
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()[:16]  # 取前16位足够用于去重


def normalize_filename(title: str, year: str, first_author: str) -> str:
    """
    规范化文件名，格式: [year]-[firstAuthorLastName]-[titleSlug]

    Args:
        title: 论文标题
        year: 发表年份
        first_author: 第一作者全名

    Returns:
        规范化的文件名（不含扩展名）
    """
    # 1. 提取作者姓氏（取最后一个单词，处理 Western 姓名）
    author_lastname = ""
    if first_author:
        author_lastname = first_author.strip().split()[-1]
        author_lastname = re.sub(r'[^\w]', '', author_lastname)[:15]

    # 2. 标题 slug 化
    title_slug = ""
    if title:
        # 移除标点，保留字母数字和空格
        title_slug = re.sub(r'[^\w\s]', '', title)
        # 取前 N 个词
        words = title_slug.split()[:settings.max_title_slug_words]
        title_slug = ''.join(words)
        title_slug = title_slug[:80]

    # 3. 组合
    parts = []
    if year and year.isdigit():
        parts.append(year)
    if author_lastname:
        parts.append(author_lastname)
    if title_slug:
        parts.append(title_slug)

    if not parts:
        return ""

    base_name = '-'.join(parts)

    # 4. 移除非法字符
    base_name = re.sub(r'[<>:"/\\|?*]', '', base_name)

    # 5. Unicode 规范化 (NFC)
    base_name = unicodedata.normalize('NFC', base_name)

    # 6. 截断（预留空间给冲突后缀）
    if len(base_name) > settings.max_filename_length:
        base_name = base_name[:settings.max_filename_length]

    return base_name


def get_unique_folder_name(base_name: str, output_dir: Path) -> str:
    """
    获取唯一的文件夹名，处理命名冲突

    Args:
        base_name: 基础名称
        output_dir: 输出目录

    Returns:
        唯一的文件夹名
    """
    folder_name = base_name
    counter = 1

    while (output_dir / folder_name).exists():
        # 添加数字后缀
        suffix = f"_{counter:03d}"
        max_base_len = settings.max_filename_length - len(suffix)
        folder_name = base_name[:max_base_len] + suffix
        counter += 1

    return folder_name


def sanitize_path_component(name: str) -> str:
    """
    清理路径组件，移除非法字符

    Args:
        name: 原始名称

    Returns:
        清理后的名称
    """
    # Windows 非法字符: < > : " / \ | ? *
    name = re.sub(r'[<>:"/\\|?*]', '_', name)
    # 移除控制字符
    name = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', name)
    # 去除首尾空格和点
    name = name.strip('. ')
    # 限制长度
    if len(name) > 100:
        name = name[:100]
    return name


def atomic_write_json(data: dict, file_path: Path) -> None:
    """
    原子写入 JSON 文件，防止崩溃导致数据损坏

    Args:
        data: 要写入的数据
        file_path: 目标文件路径
    """
    temp_path = file_path.with_suffix('.tmp')
    try:
        import json
        with open(temp_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        shutil.move(str(temp_path), str(file_path))
    except Exception:
        # 清理临时文件
        if temp_path.exists():
            temp_path.unlink()
        raise


def format_citekey(first_author: str, title: str, year: str) -> str:
    """
    生成引用键 (citekey)，格式: FirstAuthorFirstWordOfTitleYear

    Args:
        first_author: 第一作者
        title: 标题
        year: 年份

    Returns:
        CamelCase 格式的 citekey
    """
    parts = []

    # 作者姓氏
    if first_author:
        lastname = first_author.strip().split()[-1]
        parts.append(lastname.capitalize())

    # 标题第一个实词
    if title:
        first_word = re.sub(r'[^\w]', '', title.split()[0])
        if first_word:
            parts.append(first_word.capitalize())

    # 年份
    if year and year.isdigit():
        parts.append(year)

    return ''.join(parts) if parts else "Unknown"


def truncate_text(text: str, max_chars: int, suffix: str = "...") -> str:
    """
    截断文本到指定长度

    Args:
        text: 原始文本
        max_chars: 最大字符数
        suffix: 截断后缀

    Returns:
        截断后的文本
    """
    if len(text) <= max_chars:
        return text
    return text[:max_chars - len(suffix)] + suffix


def estimate_token_count(text: str) -> int:
    """
    估算文本的 token 数量（粗略估计）

    Args:
        text: 输入文本

    Returns:
        估算的 token 数
    """
    # 中文字符：每个字约 1-2 tokens
    # 英文单词：每个词约 1 token
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    english_words = len(re.findall(r'[a-zA-Z]+', text))

    return chinese_chars * 2 + english_words


def generate_node_id(title: str) -> str:
    """
    使用 title + timestamp 组合 hash 避免冲突生成节点 ID。
    
    Args:
        title: 节点相关的标题或标识文本
        
    Returns:
        生成的节点 ID 字符串
    """
    import time
    base = hashlib.sha256(title.encode('utf-8')).hexdigest()[:12]
    return f"node_{base}_{int(time.time())}"
