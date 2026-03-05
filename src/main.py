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
import logging
from pathlib import Path
from typing import List, Optional

# 将 src 目录添加到路径
sys.path.insert(0, str(Path(__file__).parent))

from config import settings
from exceptions import DeepReadError
from utils import setup_logging, normalize_filename
from state_tracker import StateTracker
from pdf_processor import PDFProcessor
from summarizer import Summarizer
from canvas_builder import CanvasBuilder


def parse_args() -> argparse.Namespace:
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="DeepRead - 学术论文阅读与知识可视化系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 交互模式（逐个输入文件名）
  python main.py

  # 批量处理所有未识别文件
  python main.py --batch

  # 指定单个或多个文件
  python main.py --file paper1.pdf paper2.pdf

  # 强制重新处理
  python main.py --file paper.pdf --force

  # 仅重建总图谱
  python main.py --rebuild-map
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
    logger = logging.getLogger(__name__)

    logger.info(f"开始处理: {filename}")
    print(f"\n📄 处理: {filename}")

    # 检查是否需要处理（增量更新）
    current_hash = state_tracker.compute_file_hash(pdf_path)
    existing_record = state_tracker.get_file_record(filename)

    if not force and existing_record:
        if existing_record.get("hash") == current_hash:
            logger.info(f"  文件未变化，跳过: {filename}")
            print(f"   ✓ 已是最新版本，跳过")
            return True, "skipped"
        else:
            logger.info(f"  文件有变化，重新处理: {filename}")
            print(f"   📝 文件有变化，重新处理")

    try:
        # Step 1: 预处理验证
        print(f"   1️⃣  验证 PDF...", end=" ")
        is_valid, error_msg = processor.validate_pdf(str(pdf_path))
        if not is_valid:
            logger.error(f"PDF 验证失败: {error_msg}")
            print(f"失败\n      错误: {error_msg}")
            return False, error_msg
        print("✓")

        # Step 2: 提取元数据
        print(f"   2️⃣  提取元数据...", end=" ")
        metadata = processor.extract_metadata(str(pdf_path))
        title = metadata.get("title", "")
        year = str(metadata.get("year", ""))
        first_author = metadata.get("first_author", "")
        print(f"✓ ({title[:30]}...)")

        # Step 3: 创建文件夹
        folder_name = normalize_filename(title or filename, year, first_author)
        output_folder = settings.output_path / folder_name
        output_folder.mkdir(parents=True, exist_ok=True)
        print(f"   3️⃣  输出目录: {output_folder.name}")

        # Step 4: 转换 PDF → Markdown
        print(f"   4️⃣  转换 PDF → Markdown...", end=" ")
        md_content = processor.convert_to_markdown(str(pdf_path), str(output_folder))
        md_file = output_folder / f"{folder_name}.md"
        md_file.write_text(md_content, encoding="utf-8")
        print("✓")

        # Step 5: 生成 Summary（可选跳过）
        summary_file = output_folder / "Summary.md"
        if not skip_summary:
            print(f"   5️⃣  生成 AI 总结...", end=" ")
            summary = summarizer.generate_summary(md_content, metadata)
            summary_file.write_text(summary, encoding="utf-8")
            print("✓")
        else:
            print(f"   5️⃣  跳过 AI 总结")

        # Step 6: 生成单文献 Canvas
        print(f"   6️⃣  生成知识卡片...", end=" ")
        canvas_file = output_folder / f"{folder_name}.canvas"
        canvas_builder.create_paper_canvas(
            str(summary_file) if summary_file.exists() else None,
            str(canvas_file),
            metadata
        )
        print("✓")

        # Step 7: 更新状态追踪
        outputs = [
            str(md_file.relative_to(settings.root_dir)),
            str(summary_file.relative_to(settings.root_dir)) if summary_file.exists() else None,
            str(canvas_file.relative_to(settings.root_dir)),
        ]
        outputs = [o for o in outputs if o]

        state_tracker.update_file_record(
            filename=filename,
            file_hash=current_hash,
            folder_name=folder_name,
            outputs=outputs,
            title=title
        )

        logger.info(f"处理完成: {filename}")
        print(f"   ✅ 完成!")
        return True, "success"

    except DeepReadError as e:
        logger.error(f"处理失败 [{e.code}]: {e.message}")
        print(f"   ❌ 失败: [{e.code}] {e.message}")
        return False, str(e)
    except Exception as e:
        logger.exception(f"处理时发生未知错误: {e}")
        print(f"   ❌ 失败: {e}")
        return False, str(e)


def update_master_map(canvas_builder: CanvasBuilder, state_tracker: StateTracker):
    """更新总图谱"""
    print("\n🗺️  更新总知识图谱...")

    records = state_tracker.get_all_records()
    papers = []

    for filename, record in records.items():
        if record.get("status") == "completed":
            papers.append({
                "folder_name": record.get("folder_name", ""),
                "title": record.get("title", ""),
                "summary_path": settings.output_path / record.get("folder_name", "") / "Summary.md"
            })

    if not papers:
        print("   没有已完成的文献")
        return

    canvas_builder.update_master_map(papers)
    print(f"   ✓ 总图谱已更新（{len(papers)} 篇文献）")


def main():
    """主入口函数"""
    args = parse_args()

    # 初始化日志
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("DeepRead 启动")

    # 验证配置
    is_valid, errors = settings.validate()
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
            filename = pdf_path.name
            current_hash = state_tracker.compute_file_hash(pdf_path)
            existing = state_tracker.get_file_record(filename)

            if not existing or existing.get("hash") != current_hash or args.force:
                files_to_process.append(pdf_path)

        print(f"   发现 {len(all_pdfs)} 个 PDF，其中 {len(files_to_process)} 个需要处理")

    elif args.file:
        # 指定文件模式
        files_to_process = []
        for f in args.file:
            pdf_path = Path(f)
            if not pdf_path.is_absolute():
                pdf_path = settings.input_path / pdf_path
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

    logger.info(f"处理完成: 成功 {success_count}/{len(files_to_process)}")

    # 如果有失败，返回非零退出码
    if failed_files:
        sys.exit(1)


if __name__ == "__main__":
    main()
