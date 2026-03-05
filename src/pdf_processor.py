"""
/**
 * [IN]: config.settings, exceptions, utils, fitz(PyMuPDF), subprocess(Marker)
 * [OUT]: PDFProcessor 类 - PDF验证、转换、元数据提取
 * [POS]: 被 main.py 调用，处理 PDF → Markdown 转换流程
 * [PROTOCOL]: 修改处理逻辑 -> 更新 tests/test_pdf_processor.py
 */
"""
import shutil
import subprocess
from pathlib import Path
from typing import Optional, Tuple

import fitz  # PyMuPDF

from .config import settings
from .exceptions import PDFAccessError, MarkerProcessingError
from .utils import compute_file_hash, normalize_filename


class PDFPreprocessor:
    """PDF 预处理器 - 验证和基本信息提取"""

    @staticmethod
    def validate(pdf_path: Path) -> Tuple[bool, str, dict]:
        """
        验证 PDF 是否适合处理

        Returns:
            (是否可处理, 错误码, 文件信息字典)
        """
        info = {
            "page_count": 0,
            "encrypted": False,
            "has_text_layer": False,
            "metadata": {},
        }

        # 1. 检查文件存在性
        if not pdf_path.exists():
            return False, "ERR_PDF_NOT_FOUND", info

        # 2. 检查文件头签名
        with open(pdf_path, 'rb') as f:
            header = f.read(5)
            if not header.startswith(b'%PDF-'):
                return False, "ERR_PDF_CORRUPTED", info

        # 3. 尝试打开并提取信息
        try:
            doc = fitz.open(pdf_path)
        except Exception as e:
            return False, "ERR_PDF_OPEN_FAILED", info

        with doc:
            # 4. 检查加密状态
            if doc.is_encrypted:
                auth_result = doc.authenticate("")
                if auth_result == 0:
                    return False, "ERR_PDF_ENCRYPTED", info
                info["encrypted"] = True

            # 5. 检查页数
            page_count = len(doc)
            info["page_count"] = page_count

            if page_count == 0:
                return False, "ERR_PDF_EMPTY", info

            if page_count > 500:
                return False, "ERR_PDF_TOO_LARGE", info

            # 6. 检查文本层
            if page_count > 0:
                first_page = doc[0]
                text = first_page.get_text()
                info["has_text_layer"] = len(text.strip()) > 50

            # 7. 提取元数据
            metadata = doc.metadata
            info["metadata"] = {
                "title": metadata.get("title", ""),
                "author": metadata.get("author", ""),
                "subject": metadata.get("subject", ""),
                "keywords": metadata.get("keywords", ""),
                "creator": metadata.get("creator", ""),
                "producer": metadata.get("producer", ""),
                "creation_date": metadata.get("creationDate", ""),
                "modification_date": metadata.get("modDate", ""),
            }

        return True, "OK", info

    @staticmethod
    def extract_title_and_author(info: dict) -> Tuple[str, str]:
        """
        从元数据中提取标题和作者

        Returns:
            (标题, 作者)
        """
        metadata = info.get("metadata", {})
        title = metadata.get("title", "").strip()
        author = metadata.get("author", "").strip()

        # 清理作者字段（取第一个作者）
        if author:
            # 处理 "Author A, Author B" 格式
            author = author.split(",")[0].strip()
            # 处理 "Author A; Author B" 格式
            author = author.split(";")[0].strip()

        return title, author


class PDFProcessor:
    """PDF 处理器 - 协调预处理、转换和后处理"""

    def __init__(self) -> None:
        self.preprocessor = PDFPreprocessor()

    def process(
        self,
        pdf_path: Path,
        force: bool = False
    ) -> Tuple[Path, str, dict]:
        """
        处理单个 PDF 文件

        Args:
            pdf_path: PDF 文件路径
            force: 是否强制重新处理

        Returns:
            (输出文件夹路径, 生成的Markdown内容, 处理信息)
        """
        # 1. 验证 PDF
        is_valid, error_code, info = self.preprocessor.validate(pdf_path)
        if not is_valid:
            raise PDFAccessError(f"PDF validation failed: {error_code}", error_code)

        # 2. 提取标题和作者
        title, author = self.preprocessor.extract_title_and_author(info)

        # 3. 生成规范化文件夹名
        year = self._extract_year(info)
        folder_name = normalize_filename(title or "Untitled", author or "Unknown", year)
        output_folder = settings.output_path / folder_name

        # 4. 创建输出目录
        output_folder.mkdir(parents=True, exist_ok=True)
        assets_folder = output_folder / "assets"
        assets_folder.mkdir(exist_ok=True)

        # 5. 使用 Marker 转换 PDF
        markdown_content = self._convert_with_marker(pdf_path, output_folder, folder_name)

        # 6. 整理图片资源
        self._organize_assets(output_folder, folder_name)

        # 返回带元数据的处理结果（状态追踪交由 main.py 统一管理）
        return output_folder, markdown_content, {
            "status": "success",
            "folder_name": folder_name,
            "page_count": info["page_count"],
            "has_text_layer": info["has_text_layer"],
            "title": title or "",
            "year": year,
            "first_author": author or "",
        }

    def _extract_year(self, info: dict) -> str:
        """从元数据中提取年份"""
        metadata = info.get("metadata", {})

        # 尝试从 creation_date 提取
        creation_date = metadata.get("creation_date", "")
        if creation_date and len(creation_date) >= 4:
            # PDF 日期格式: D:20220202120000
            if creation_date.startswith("D:"):
                year_str = creation_date[2:6]
                if year_str.isdigit():
                    return str(year_str)

        # 尝试从 modification_date 提取
        mod_date = metadata.get("modification_date", "")
        if mod_date and len(mod_date) >= 4:
            if mod_date.startswith("D:"):
                year_str = mod_date[2:6]
                if year_str.isdigit():
                    return str(year_str)

        return "0000"

    def _convert_with_marker(
        self,
        pdf_path: Path,
        output_folder: Path,
        folder_name: str
    ) -> str:
        """使用 Marker 将 PDF 转换为 Markdown"""
        # Marker 输出目录（Marker 会创建子目录）
        marker_output_dir = output_folder / "_marker_temp"

        try:
            # 动态定位 marker_single（与 python.exe 同级的 Scripts 目录）
            import sys as _sys
            _py_dir = Path(_sys.executable).parent  # e.g. C:\...\PY_3_10\
            # 先尝试 Scripts 子目录（Windows conda 标准安装位置）
            marker_exe = _py_dir / "Scripts" / "marker_single.exe"
            if not marker_exe.exists():
                # 尝试直接在同级目录
                marker_exe = _py_dir / "marker_single.exe"
            if not marker_exe.exists():
                marker_exe = _py_dir / "marker_single"
            if not marker_exe.exists():
                raise MarkerProcessingError(
                    f"marker_single not found, searched in: {_py_dir}/Scripts and {_py_dir}"
                )

            # 构建 Marker 命令
            cmd = [
                str(marker_exe),
                str(pdf_path),
                "--output_dir", str(marker_output_dir),
                "--output_format", "markdown",
            ]

            # 执行转换
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600,  # 10 分钟超时
                encoding='utf-8',
                errors='ignore'
            )

            if result.returncode != 0:
                raise MarkerProcessingError(
                    f"Marker conversion failed: {result.stderr}",
                    details={"stdout": result.stdout, "stderr": result.stderr}
                )

            # 查找生成的 Markdown 文件
            md_files = list(marker_output_dir.rglob("*.md"))
            if not md_files:
                raise MarkerProcessingError("No markdown file generated by Marker")

            # 读取内容并重命名文件
            md_content = md_files[0].read_text(encoding='utf-8')
            target_md_path = output_folder / f"{folder_name}.md"
            # 如果目标已存在（如 --force 重复执行），先删除再移动
            if target_md_path.exists():
                target_md_path.unlink()
            md_files[0].rename(target_md_path)

            # 移动图片资源
            for img_file in marker_output_dir.rglob("*"):
                if img_file.is_file() and img_file.suffix.lower() in ['.png', '.jpg', '.jpeg', '.gif']:
                    target_img = output_folder / "assets" / img_file.name
                    shutil.move(str(img_file), str(target_img))

            return md_content

        except subprocess.TimeoutExpired:
            raise MarkerProcessingError("Marker conversion timeout (>10 minutes)")
        except Exception as e:
            if isinstance(e, MarkerProcessingError):
                raise
            raise MarkerProcessingError(f"Marker conversion error: {e}")

        finally:
            # 清理临时目录
            if marker_output_dir.exists():
                shutil.rmtree(marker_output_dir, ignore_errors=True)

    def _organize_assets(self, output_folder: Path, folder_name: str) -> None:
        """整理图片资源，更新 Markdown 中的图片链接"""
        md_file = output_folder / f"{folder_name}.md"
        if not md_file.exists():
            return

        content = md_file.read_text(encoding='utf-8')
        assets_folder = output_folder / "assets"

        # 更新图片链接路径
        # Marker 默认使用相对路径如 "_page_1_Figure_1.jpeg"
        # 需要改为 "assets/_page_1_Figure_1.jpeg"
        if assets_folder.exists():
            for img_file in assets_folder.iterdir():
                if img_file.is_file():
                    old_pattern = f"]({img_file.name})"
                    new_pattern = f"](assets/{img_file.name})"
                    content = content.replace(old_pattern, new_pattern)

        md_file.write_text(content, encoding='utf-8')


# 全局处理器实例
pdf_processor = PDFProcessor()
