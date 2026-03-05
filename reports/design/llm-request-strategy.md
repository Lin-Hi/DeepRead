# LLM 请求策略报告

**测试日期**: 2026-03-04
**API 提供商**: 阿里百炼 (DashScope)
**Base URL**: `https://coding.dashscope.aliyuncs.com/v1`
**模型**: kimi-k2.5

---

## API 配置验证

### 认证方式

```python
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}
```

### 端点信息

| 属性 | 值 |
|------|-----|
| Base URL | `https://coding.dashscope.aliyuncs.com/v1` |
| Chat Completions | `/chat/completions` |
| 协议 | OpenAI 兼容 API |

---

## Token 用量预估

### 单篇论文总结请求

| 组件 | Token 估算 |
|------|-----------|
| System Prompt | ~500 tokens |
| Markdown 全文 | 5,000 - 15,000 tokens |
| User Prompt | ~300 tokens |
| **输入总计** | **6,000 - 16,000 tokens** |
| 输出 (Summary) | 2,000 - 4,000 tokens |

### 计费说明

阿里百炼按**请求次数**计费，不按 token 数计费。因此优化策略是：
1. **合并字段提取为单次请求**（减少 API 调用次数）
2. **批量处理关系推断**（一次发送多篇文献）

---

## 请求策略设计

### 1. 单文献总结 - 单次请求模式

```python
response = client.chat.completions.create(
    model="kimi-k2.5",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"请分析以下论文内容：\n\n{markdown_content}"}
    ],
    temperature=0.3,
    max_tokens=4000
)
```

**优点**:
- 仅 1 次 API 调用
- 上下文完整，理解更准确

**风险**:
- 长论文可能超出上下文限制
- 需要处理超时情况

### 2. 长论文分段策略（Fallback）

如果论文过长，采用分段提取：

```
第 1 次请求：提取标题、作者、摘要、关键词
第 2 次请求：提取研究问题、方法论
第 3 次请求：提取主要发现、结论
```

### 3. 批量关系推断

```python
# 每批最多 5 篇文献
batch_size = 5
for i in range(0, len(papers), batch_size):
    batch = papers[i:i+batch_size]
    # 计算批次内关系矩阵
```

---

## 错误处理策略

### 重试机制（指数退避）

```python
RETRY_DELAYS = [5, 15, 60]  # 秒

for attempt, delay in enumerate(RETRY_DELAYS):
    try:
        response = call_llm()
        break
    except RateLimitError:
        time.sleep(delay)
    except TimeoutError:
        if attempt < len(RETRY_DELAYS) - 1:
            continue
        raise
```

### 字段完整性验证

```python
def validate_summary(summary: dict) -> List[str]:
    required_fields = [
        "citekey", "title", "abstract",
        "hypothesis", "methodology"
    ]
    return [f for f in required_fields if not summary.get(f)]
```

### 错误类型与处理

| 错误类型 | 处理策略 |
|---------|---------|
| RateLimitError | 指数退避重试 |
| TimeoutError | 重试，增加 timeout |
| AuthenticationError | 立即终止，提示检查 API Key |
| InvalidJSONError | 重试，使用更严格的 prompt |

---

## Prompt 工程建议

### 1. 输出格式约束

使用 JSON 模式确保结构化输出：

```python
response_format = {"type": "json_object"}
```

### 2. 语言控制

在 system prompt 中明确指定：

```
请用中文回答，但保留关键术语的英文原文。
关键概念和方法论名称使用 [[Wikilinks]] 格式。
```

### 3. Token 优化技巧

- 移除 Markdown 中的图片标记 `![...](...)`
- 截断过长的参考文献列表
- 保留核心章节（摘要、引言、方法、结果、结论）

---

## 测试验证清单

- [ ] API Key 有效性验证
- [ ] 基础对话功能测试
- [ ] JSON 模式输出测试
- [ ] 长文本处理能力测试
- [ ] 错误重试机制测试
- [ ] Token 用量统计验证

---

## 集成代码示例

见 `tests/test_llm.py` 文件获取完整的测试代码。

---

## 下一步行动

1. **获取有效 API Key** 并完成连通性测试
2. **开发 summarizer.py** 模块，实现 LLM 调用封装
3. **实现字段验证逻辑**，处理缺失字段的补充请求
