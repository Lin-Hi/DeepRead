#!/usr/bin/env python3
"""
/**
 * [IN]: os, json, time, pathlib, openai
 * [OUT]: 验证 OpenAI 兼容协议是否可以通过 API_KEY 成功连接阿里百炼并且生成正确的格式
 * [POS]: 测试 LLM 网络及认证的环境设置验证，测试用例不供其他模块消费
 * [PROTOCOL]: 增加对阿里百炼新的模型/参数的实验 -> 在 test_summary_generation 更新 prompt -> 更新 IN
 */
"""
import os
import json
import time
from pathlib import Path


def test_llm_connection():
    """测试 LLM API 连接"""
    print("=== LLM Connection Test ===\n")

    # 检查环境变量
    api_key = os.getenv("API_KEY")
    if not api_key:
        print("⚠️  API_KEY not found in environment variables")
        print("Please set API_KEY in .env file or environment")
        return False

    print(f"✓ API_KEY found (length: {len(api_key)})")

    try:
        from openai import OpenAI

        client = OpenAI(
            api_key=api_key,
            base_url="https://coding.dashscope.aliyuncs.com/v1"
        )

        # 简单测试请求
        test_prompt = "Hello, this is a test. Please respond with 'Test successful' only."

        print("\nSending test request...")
        start_time = time.time()

        response = client.chat.completions.create(
            model="kimi-k2.5",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": test_prompt}
            ],
            max_tokens=50
        )

        elapsed = time.time() - start_time

        print(f"✓ Response received in {elapsed:.2f}s")
        print(f"  Content: {response.choices[0].message.content}")
        print(f"  Model: {response.model}")
        print(f"  Tokens: prompt={response.usage.prompt_tokens}, completion={response.usage.completion_tokens}")

        return True

    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_summary_generation():
    """测试论文总结生成"""
    print("\n=== Summary Generation Test ===\n")

    sample_text = """
# Abstract

Over the past few decades, the field of Enterprise Architecture has attracted researchers,
and many Enterprise Architecture modeling frameworks have been proposed. However, in order
to support the different needs, the different frameworks offer many different elements types
that can be used to create an Enterprise Architecture.

## Methodology

This study performed a Systematic Literature Review that aims at finding the most commonly
used Enterprise Architecture modeling frameworks in the literature.

## Results

Our results showed that TOGAF, ArchiMate, DoDAF, and IAF are the most used modeling frameworks.
We managed to identify the common elements that are available in the different frameworks.
"""

    api_key = os.getenv("API_KEY")
    if not api_key:
        print("⚠️  Skipping (no API_KEY)")
        return False

    try:
        from openai import OpenAI

        client = OpenAI(
            api_key=api_key,
            base_url="https://coding.dashscope.aliyuncs.com/v1"
        )

        prompt = f"""Please analyze the following academic paper excerpt and extract key information.
Return your response in JSON format with these fields:
- title: paper title
- year: publication year (estimate if not clear)
- authors: list of authors
- abstract: brief summary
- hypothesis: main research hypothesis
- methodology: research methods used
- key_findings: main findings

Paper content:
{sample_text[:1500]}

Respond with valid JSON only."""

        print("Sending summary generation request...")
        start_time = time.time()

        response = client.chat.completions.create(
            model="kimi-k2.5",
            messages=[
                {"role": "system", "content": "You are an expert academic paper analyzer."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.3
        )

        elapsed = time.time() - start_time

        content = response.choices[0].message.content
        print(f"✓ Response received in {elapsed:.2f}s")
        print(f"  Raw response preview:\n{content[:500]}...")

        # Try to parse as JSON
        try:
            # Extract JSON if wrapped in markdown code block
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]

            data = json.loads(content.strip())
            print(f"\n✓ Valid JSON parsed successfully")
            print(f"  Fields: {list(data.keys())}")
            return True
        except json.JSONDecodeError as e:
            print(f"\n⚠️  JSON parsing failed: {e}")
            return False

    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def estimate_token_cost():
    """估算 Token 成本"""
    print("\n=== Token Cost Estimation ===\n")

    # 基于典型论文字数的估算
    scenarios = [
        ("Short paper (10 pages)", 5000),
        ("Medium paper (20 pages)", 10000),
        ("Long paper (40 pages)", 20000),
        ("Thesis (70 pages)", 35000),
    ]

    print("Estimated token usage per scenario:")
    print("-" * 60)
    print(f"{'Scenario':<25} {'Input Tokens':>15} {'Output Tokens':>15}")
    print("-" * 60)

    for name, word_count in scenarios:
        # Rough estimate: 1 word ≈ 1.3 tokens
        input_tokens = int(word_count * 1.3) + 1000  # + prompt
        output_tokens = 2000  # Estimated summary length
        print(f"{name:<25} {input_tokens:>15,} {output_tokens:>15,}")

    print("-" * 60)
    print("\nNote: kimi-k2.5 pricing (as of 2026-03):")
    print("  Input: ￥0.004 / 1K tokens")
    print("  Output: ￥0.008 / 1K tokens")


if __name__ == "__main__":
    # Load .env file if exists
    env_path = Path(".env")
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value

    print("="*60)
    print("DeepRead LLM Request Strategy Test")
    print("="*60)

    # Run tests
    connection_ok = test_llm_connection()

    if connection_ok:
        test_summary_generation()

    estimate_token_cost()

    print("\n" + "="*60)
    print("Test completed!")
    print("="*60)
