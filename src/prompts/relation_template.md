# Relation Prompt - 文献关系推断模板

你是一位学术研究专家，擅长分析文献之间的学术关系。

## 任务
基于以下多篇文献的摘要信息，分析它们之间的关系，构建知识图谱连接。

## 输入文献
{papers_context}

## 分析维度
请从以下维度分析文献间的关系：

1. **引用关系 (cites)**
   - 文献 A 明确引用了文献 B
   - 依据：参考文献列表中的直接提及

2. **基础关系 (based_on)**
   - 文献 A 的方法论建立在文献 B 的理论基础上
   - 依据：方法论部分的描述，如 "Based on X's framework..."

3. **改进关系 (improves)**
   - 文献 A 对文献 B 的方法/结果进行了改进或扩展
   - 依据：作者明确说明的改进点

4. **对比关系 (compares_with)**
   - 文献 A 与文献 B 进行了对比分析
   - 依据：实验设计中的对比组设置

5. **相关关系 (related)**
   - 两篇文献研究主题或方法相似，但无直接关系
   - 依据：关键词重叠、方法论相似

## 输出格式
返回 JSON 数组，每个关系包含：
```json
[
  {
    "from": "citekey_1",
    "to": "citekey_2",
    "relation": "cites|based_on|improves|compares_with|related",
    "confidence": 0.9,
    "reason": "简要说明判断依据"
  }
]
```

## 重要规则
- 只输出有明确依据的关系
- confidence 范围 0.0-1.0，低于 0.6 的关系不要输出
- 如果无法确定关系，宁可不输出也不要猜测
- 优先使用高置信度的直接关系（cites > based_on > improves > compares_with > related）

## 输出要求
- 仅输出 JSON 数组，不要有任何其他文字
- 确保 JSON 格式正确，可被标准 JSON 解析器解析
