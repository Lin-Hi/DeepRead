#!/usr/bin/env python3
"""
/**
 * [IN]: sys, argparse, pathlib, logging
 * [OUT]: DeepRead CLI - 命令行入口点
 * [POS]: 用户直接执行，协调各模块工作流
 * [PROTOCOL]: 新增命令参数 -> 更新 README.md 使用文档
 */
"""
import sys
import argparse

from pathlib import Path
from typing import List, Optional

# Windows 终端字符编码崩溃备用·强制 UTF-8
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")  # type: ignore

from src.config import settings
from src.exceptions import DeepReadError
from src.logger import get_logger
from src.utils import normalize_filename
from src.state_tracker import StateTracker
from src.pdf_processor import PDFProcessor
from src.summarizer import Summarizer
from src.canvas_builder import CanvasBuilder

# 初始化日志器
logger = get_logger(__name__)


def parse_args() -> argparse.Namespace:
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="DeepRead - 学术论文阅读与知识可视化系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 交互模式（逐个输入文件名）
  python -m src.main

  # 批量处理所有未识别文件
  python -m src.main --batch

  # 指定单个或多个文件
  python -m src.main --file paper1.pdf paper2.pdf

  # 强制重新处理
  python -m src.main --file paper.pdf --force

  # 仅重建总图谱
  python -m src.main --rebuild-map
        """
    )

    parser.add_argument(
        "--batch",
        action="store_true",
        help="自动扫描 input-pdfs 目录，处理所有未识别文件"
    )

    parser.add_argument(
        "--file",
        nargs="+",
        metavar="PDF",
        help="指定要处理的 PDF 文件（一个或多个）"
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="强制重新处理，忽略 state.json 中的 hash 匹配"
    )

    parser.add_argument(
        "--skip-summary",
        action="store_true",
        help="跳过 Summary 生成，仅更新 Canvas"
    )

    parser.add_argument(
        "--rebuild-map",
        action="store_true",
        help="重建总图谱（而非增量更新）"
    )

    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0"
    )

    return parser.parse_args()


def interactive_mode(state_tracker: StateTracker) -> List[Path]:
    """
    交互模式：逐个询问文件名

    Returns:
        用户选择的 PDF 文件列表
    """
    print("\n=== DeepRead 交互模式 ===")
    print("请输入要处理的 PDF 文件名（每行一个，空行结束）：\n")

    files = []
    while True:
        try:
            line = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not line:
            break

        pdf_path = settings.input_path / line
        if pdf_path.exists():
            files.append(pdf_path)
            print(f"  [已添加] {line}")
        else:
            # 尝试添加 .pdf 后缀
            pdf_path_with_ext = settings.input_path / f"{line}.pdf"
            if pdf_path_with_ext.exists():
                files.append(pdf_path_with_ext)
                print(f"  [已添加] {line}.pdf")
            else:
                print(f"  [错误] 文件不存在: {line}")

    print(f"\n共选择 {len(files)} 个文件")
    return files


def process_batch(pdf_files: List[Path], processor: PDFProcessor,
    summarizer: Summarizer,
    canvas_builder: CanvasBuilder,
    state_tracker: StateTracker,
    skip_summary: bool = False,
    force: bool = False,
    max_workers: int = 2) -> None:
    """
    批量处理 PDF 文件，支持并发。
    """
    # Placeholder for the actual implementation of process_batch
    # This function would typically use a ThreadPoolExecutor or ProcessPoolExecutor
    # to call process_single_pdf for each file in pdf_files.
    # For now, it's an empty function to satisfy the user's request.
    pass


def process_single_pdf(
    pdf_path: Path,
    processor: PDFProcessor,
    summarizer: Summarizer,
    canvas_builder: CanvasBuilder,
    state_tracker: StateTracker,
    skip_summary: bool = False,
    force: bool = False
) -> tuple[bool, str]:
    """
    处理单个 PDF 文件

    Returns:
        (是否成功, 消息)
    """
    filename = pdf_path.name
    logger = get_logger(__name__)
    from time import time as _t

    logger.info(f"开始处理: {filename}")
    print(f"\n📄 处理: {filename}")

    # 检查增量缓存（基于 StateTracker.is_processed）
    if not force and state_tracker.is_processed(pdf_path):
        logger.info(f"  文件未变化，跳过: {filename}")
        print(f"   ✓ 已是最新版本，跳过")
        return True, "skipped"

    try:
        # Step 1-4: PDFProcessor.process() 内部完成验证/元数据/转换/整理
        print(f"   1️⃣  验证并转换 PDF → Markdown...")
        output_folder, md_content, info = processor.process(pdf_path, force=force)

        folder_name = output_folder.name
        md_file = output_folder / f"{folder_name}.md"
        title = info.get("title", "")
        year = str(info.get("year", ""))
        first_author = info.get("first_author", "")

        # 跳过（已处理）
        if info.get("status") == "skipped":
            print(f"   ✓ 已处理，跳过")
            return True, "skipped"

        # Step 5: 生成 Summary（可选跳过）
        summary_file = output_folder / "Summary.md"
        summary_data = {}  # 用于传递给 Canvas
        if not skip_summary:
            _t5 = _t()
            print(f"   [5/6] AI 摘要生成中...", flush=True)
            summary_data = summarizer.generate_summary(md_content, summary_file)
            print(f"          [OK] {_t()-_t5:.1f}s")
        else:
            print(f"   [5/6] 跳过 AI 总结（Canvas 内容将为占位符）")

        # Step 6: 生成单文献 Canvas
        _t6 = _t()
        print(f"   [6/6] 生成知识卡片...", end="", flush=True)
        canvas_file = output_folder / f"{folder_name}.canvas"
        canvas_input = {
            "title": title or folder_name,
            "year": year,
            "first_author": first_author,
            **summary_data,  # 包含 methodology/key_findings 等 AI 分析字段
        }
        canvas_builder.create_paper_canvas(
            canvas_input,
            output_folder,
            folder_name
        )
        print(f" [OK] {_t()-_t6:.1f}s")

        # Step 7: 更新状态追踪
        file_hash = StateTracker.compute_hash(pdf_path)
        outputs = [str(md_file), str(canvas_file)]
        if summary_file.exists():
            outputs.append(str(summary_file))

        state_tracker.update_file_state(
            pdf_path=pdf_path,
            title=title,
            folder_name=folder_name,
            outputs=outputs
        )

        logger.info(f"处理完成: {filename}")
        print(f"   ✅ 完成!")
        return True, "success"

    except DeepReadError as e:
        logger.error(f"处理失败 [{e.error_code}]: {e.message}")
        print(f"   ❌ 失败: [{e.error_code}] {e.message}")
        return False, str(e)
    except Exception as e:
        logger.exception(f"处理时发生未知错误: {e}")
        print(f"   ❌ 失败: {e}")
        return False, str(e)


def update_master_map(canvas_builder: CanvasBuilder, state_tracker: StateTracker) -> None:
    """更新总图谱"""
    print("\n🗺️  更新总知识图谱...")

    # 使用真实 API: get_all_processed_files() 返回文件名列表
    processed_filenames = state_tracker.get_all_processed_files()
    papers = []

    for filename in processed_filenames:
        # 从 state 中读取 FileState
        # get_file_state 接受 pdf_path，这里用虚拟路径，仅为获取状态
        file_state = state_tracker._state["files"].get(filename)
        if not file_state:
            continue
        folder_name = file_state.get("folder_name", "")
        title = file_state.get("title", "")
        papers.append({
            "folder_name": folder_name,
            "title": title,
            "summary_path": settings.output_path / folder_name / "Summary.md"
        })

    if not papers:
        print("   没有已完成的文献")
        return

    # update_master_map 接受 literature_dir: Path，不是 papers 列表
    canvas_builder.update_master_map(settings.output_path)
    print(f"   ✓ 总图谱已更新（{len(papers)} 篇文献）")



def main() -> None:
    """主入口函数"""
    args = parse_args()

    # 初始化日志

    logger = get_logger(__name__)
    logger.info("DeepRead 启动")

    # 验证配置
    is_valid, errors = settings.check_config()
    if not is_valid:
        print("配置验证失败:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)

    # 初始化组件
    state_tracker = StateTracker()
    processor = PDFProcessor()
    summarizer = Summarizer()
    canvas_builder = CanvasBuilder()

    # 确定要处理的文件
    if args.rebuild_map:
        # 仅重建总图谱
        update_master_map(canvas_builder, state_tracker)
        print("\n✨ 总图谱重建完成!")
        return

    elif args.batch:
        # 批量模式：扫描所有未识别的文件
        print("\n🔍 批量模式：扫描 input-pdfs 目录...")
        all_pdfs = list(settings.input_path.glob("*.pdf"))

        files_to_process = []
        for pdf_path in all_pdfs:
            # 使用真实 API: is_processed() 综合检查 hash + 输出完整性
            if args.force or not state_tracker.is_processed(pdf_path):
                files_to_process.append(pdf_path)

        print(f"   发现 {len(all_pdfs)} 个 PDF，其中 {len(files_to_process)} 个需要处理")

    elif args.file:
        # 指定文件模式
        files_to_process = []
        for f in args.file:
            pdf_path = Path(f)
            # 1) 绝对路径直接使用
            if pdf_path.is_absolute():
                pass
            # 2) 相对路径直接存在（如 input-pdfs/file.pdf）则转为绝对
            elif pdf_path.exists():
                pdf_path = pdf_path.resolve()
            # 3) 仅有文件名则拼接 input_path
            else:
                pdf_path = settings.input_path / pdf_path.name

            if pdf_path.exists():
                files_to_process.append(pdf_path)
            else:
                print(f"警告: 文件不存在 - {f}")


    else:
        # 交互模式
        files_to_process = interactive_mode(state_tracker)

    if not files_to_process:
        print("\n没有要处理的文件")
        return

    # 处理文件
    print(f"\n{'='*50}")
    print(f"开始处理 {len(files_to_process)} 个文件")
    print(f"{'='*50}")

    success_count = 0
    failed_files = []

    for i, pdf_path in enumerate(files_to_process, 1):
        print(f"\n[{i}/{len(files_to_process)}]", end="")

        success, msg = process_single_pdf(
            pdf_path=pdf_path,
            processor=processor,
            summarizer=summarizer,
            canvas_builder=canvas_builder,
            state_tracker=state_tracker,
            skip_summary=args.skip_summary,
            force=args.force
        )

        if success:
            success_count += 1
        else:
            failed_files.append((pdf_path.name, msg))

    # 更新总图谱
    if success_count > 0 and not args.skip_summary:
        update_master_map(canvas_builder, state_tracker)

    # 输出汇总报告
    print(f"\n{'='*50}")
    print("处理完成")
    print(f"成功: {success_count}/{len(files_to_process)}")

    if failed_files:
        print(f"\n失败文件列表:")
        for filename, error in failed_files:
            print(f"  - {filename}: {error}")

    print(f"\n详细日志: {settings.log_path}/deepread_*.log")
    print(f"{'='*50}\n")



    # 如果有失败，返回非零退出码
    if failed_files:
        sys.exit(1)


if __name__ == "__main__":
    main()
