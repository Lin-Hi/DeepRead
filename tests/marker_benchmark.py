#!/usr/bin/env python3
"""
/**
 * [IN]: time, subprocess, json, pathlib, datetime
 * [OUT]: 运行 Marker 并验证 PDF 转 Markdown 的效果（生成测试报告）
 * [POS]: 仅用于 Phase 1.5 技术验证，不作为核心库被读取
 * [PROTOCOL]: 增加新的基准测试项 -> 更新 reports/marker-benchmark-result.json 字段定义 -> 检查本文件头的 IN 依赖
 */
"""
import time
import subprocess
import json
from pathlib import Path
from datetime import datetime


def run_marker_benchmark(pdf_file: str, output_dir: str) -> dict:
    """运行 Marker 基准测试"""
    result_data = {
        "test_file": pdf_file,
        "output_dir": output_dir,
        "timestamp": datetime.now().isoformat(),
        "success": False,
        "processing_time_seconds": 0,
        "return_code": -1,
        "stdout": "",
        "stderr": "",
        "output_files": []
    }

    print(f"=== Marker Benchmark Test ===")
    print(f"Testing file: {pdf_file}")
    print(f"Output directory: {output_dir}")
    print()

    # 确保输出目录存在
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # 运行 marker - 使用正确的参数格式
    start_time = time.time()
    try:
        result = subprocess.run(
            ['marker_single', pdf_file, '--output_dir', output_dir],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        elapsed = time.time() - start_time

        result_data["processing_time_seconds"] = round(elapsed, 2)
        result_data["return_code"] = result.returncode
        result_data["stdout"] = result.stdout
        result_data["stderr"] = result.stderr
        result_data["success"] = (result.returncode == 0)

        print(f"Processing time: {elapsed:.2f} seconds")
        print(f"Return code: {result.returncode}")
        print()

        if result.returncode == 0:
            # 检查输出文件
            output_path = Path(output_dir)
            result_data["output_files"] = [str(f) for f in output_path.rglob('*') if f.is_file()]
            print(f"Output files generated: {len(result_data['output_files'])}")
            for f in result_data["output_files"]:
                print(f"  - {f}")
        else:
            print("STDERR:")
            print(result.stderr[-2000:] if len(result.stderr) > 2000 else result.stderr)

    except Exception as e:
        result_data["stderr"] = str(e)
        print(f"Error running marker: {e}")

    return result_data


def analyze_output(output_dir: str) -> dict:
    """分析 Marker 输出结果"""
    analysis = {
        "markdown_found": False,
        "images_found": [],
        "metadata_found": False,
        "markdown_preview": ""
    }

    output_path = Path(output_dir)

    # 查找 Markdown 文件
    md_files = list(output_path.rglob('*.md'))
    if md_files:
        analysis["markdown_found"] = True
        md_file = md_files[0]
        content = md_file.read_text(encoding='utf-8')
        analysis["markdown_preview"] = content[:2000]  # 前2000字符预览

        # 检查是否包含公式、表格等
        analysis["has_latex"] = '$' in content or '\\(' in content or '\\[' in content
        analysis["has_tables"] = '|' in content and '\n|' in content

    # 查找图片
    img_exts = ['.png', '.jpg', '.jpeg', '.gif']
    for ext in img_exts:
        analysis["images_found"].extend([str(f) for f in output_path.rglob(f'*{ext}')])

    # 查找元数据
    metadata_files = list(output_path.rglob('metadata.json'))
    analysis["metadata_found"] = len(metadata_files) > 0

    return analysis


if __name__ == "__main__":
    # 测试配置
    test_files = [
        "FULLTEXT01.pdf",
        "FULLTEXT01 (1).pdf"
    ]

    all_results = []

    for pdf_file in test_files:
        if not Path(pdf_file).exists():
            print(f"File not found: {pdf_file}, skipping...")
            continue

        output_dir = f"reports/marker_test_{Path(pdf_file).stem.replace(' ', '_')}"

        # 运行测试
        result = run_marker_benchmark(pdf_file, output_dir)

        # 分析输出
        if result["success"]:
            analysis = analyze_output(output_dir)
            result["analysis"] = analysis

            print("\n=== Output Analysis ===")
            print(f"Markdown found: {analysis['markdown_found']}")
            print(f"Images found: {len(analysis['images_found'])}")
            print(f"Metadata found: {analysis['metadata_found']}")
            print(f"Has LaTeX formulas: {analysis.get('has_latex', False)}")
            print(f"Has tables: {analysis.get('has_tables', False)}")
            print("\n=== Markdown Preview (first 1000 chars) ===")
            print(analysis['markdown_preview'][:1000])

        all_results.append(result)
        print("\n" + "="*50 + "\n")

    # 保存测试结果
    report_file = "reports/marker-benchmark-result.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)

    print(f"Benchmark results saved to: {report_file}")
