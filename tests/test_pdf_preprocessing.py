#!/usr/bin/env python3
"""
/**
 * [IN]: sys, pathlib, fitz (PyMuPDF)
 * [OUT]: 检查给定 PDF 的属性，如完整性、加/解密、页数、文本层是否存在
 * [POS]: 先于 pdf_processor 调用前的独立逻辑验证，避免传递故障 PDF 给 Marker
 * [PROTOCOL]: 扩展新文件支持（如 .epub 转 PDF） -> 添加边界用例到 test_files 数组
 */
"""
import sys
from pathlib import Path

def check_pdf_basic_info(pdf_path: str) -> dict:
    """使用 PyMuPDF 检查 PDF 基本信息"""
    result = {
        "file": pdf_path,
        "exists": False,
        "readable": False,
        "is_pdf": False,
        "page_count": 0,
        "encrypted": False,
        "needs_password": False,
        "metadata": {},
        "error": None
    }

    try:
        import fitz  # PyMuPDF
    except ImportError:
        result["error"] = "PyMuPDF not installed. Install with: pip install pymupdf"
        return result

    path = Path(pdf_path)
    if not path.exists():
        result["error"] = f"File not found: {pdf_path}"
        return result

    result["exists"] = True
    result["file_size_mb"] = round(path.stat().st_size / (1024 * 1024), 2)

    # 检查文件头（PDF 签名）
    with open(pdf_path, 'rb') as f:
        header = f.read(5)
        if header.startswith(b'%PDF-'):
            result["is_pdf"] = True
            result["pdf_version"] = header.decode('latin-1').replace('%PDF-', '')
        else:
            result["error"] = "Invalid PDF header signature"
            return result

    # 使用 PyMuPDF 打开
    try:
        doc = fitz.open(pdf_path)
        result["readable"] = True
        result["page_count"] = len(doc)
        result["encrypted"] = doc.is_encrypted

        if doc.is_encrypted:
            # 尝试空密码解密
            auth_result = doc.authenticate("")
            if auth_result == 0:
                result["needs_password"] = True
                result["error"] = "PDF is password protected"
            else:
                result["needs_password"] = False

        # 提取元数据
        metadata = doc.metadata
        result["metadata"] = {
            "title": metadata.get("title", ""),
            "author": metadata.get("author", ""),
            "subject": metadata.get("subject", ""),
            "creator": metadata.get("creator", ""),
            "producer": metadata.get("producer", ""),
            "creation_date": metadata.get("creationDate", ""),
            "modification_date": metadata.get("modDate", ""),
        }

        # 检查第一页是否有文本层
        if len(doc) > 0:
            first_page = doc[0]
            text = first_page.get_text()
            result["has_text_layer"] = len(text.strip()) > 50  # 假设有50字符以上为文本层

        doc.close()

    except Exception as e:
        result["error"] = f"Error opening PDF: {str(e)}"

    return result


def validate_pdf_for_processing(pdf_path: str) -> tuple[bool, str]:
    """
    验证 PDF 是否适合处理
    返回: (是否可处理, 错误信息)
    """
    info = check_pdf_basic_info(pdf_path)

    if not info["exists"]:
        return False, f"ERR_PDF_NOT_FOUND: {info['error']}"

    if not info["is_pdf"]:
        return False, f"ERR_PDF_CORRUPTED: {info['error']}"

    if info["needs_password"]:
        return False, "ERR_PDF_ENCRYPTED: PDF requires password"

    if info["page_count"] == 0:
        return False, "ERR_PDF_EMPTY: PDF has no pages"

    if info["page_count"] > 500:
        return False, f"ERR_PDF_TOO_LARGE: PDF has {info['page_count']} pages (max 500)"

    return True, "OK"


if __name__ == "__main__":
    test_files = [
        "FULLTEXT01.pdf",
        "FULLTEXT01 (1).pdf",
        "nonexistent.pdf",  # 测试不存在的文件
    ]

    print("=== PDF Preprocessing Validation ===\n")

    for pdf_file in test_files:
        print(f"Testing: {pdf_file}")
        print("-" * 40)

        info = check_pdf_basic_info(pdf_file)

        if not info["exists"]:
            print(f"  Status: FILE NOT FOUND")
            print(f"  Error: {info['error']}")
        elif info.get("error"):
            print(f"  Status: ERROR")
            print(f"  Error: {info['error']}")
        else:
            print(f"  Status: OK")
            print(f"  File size: {info.get('file_size_mb', 0)} MB")
            print(f"  PDF version: {info.get('pdf_version', 'unknown')}")
            print(f"  Pages: {info['page_count']}")
            print(f"  Encrypted: {info['encrypted']}")
            print(f"  Has text layer: {info.get('has_text_layer', False)}")

            if info['metadata'].get('title'):
                print(f"  Title: {info['metadata']['title']}")
            if info['metadata'].get('author'):
                print(f"  Author: {info['metadata']['author']}")

        # 验证是否可处理
        can_process, msg = validate_pdf_for_processing(pdf_file)
        print(f"  Can process: {can_process} ({msg})")

        print()
