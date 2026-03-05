# DeepRead 研究领域规则

**用途**: 指导 AI 生成学术文献的 Summary.md 和 Canvas 节点内容

**语言策略**: 中英双语，关键术语保留英文，大段逻辑陈述用中文便于阅读

---

## 1. 研究背景与目标

### 用户研究领域
- **核心课题**: Azure Serverless vs 传统 SpringBoot
- **关注维度**: 安全性、高并发场景下的稳定性
- **研究类型**: 对比分析、性能评估、架构设计

### 输出目标
生成结构化的学术笔记，便于：
1. 快速回顾论文核心贡献
2. 发现文献间的关联与差异
3. 激发批判性思维与研究灵感

---

## 2. Summary.md 格式规范

### 2.1 Frontmatter（YAML）

```yaml
---
citekey: {{FirstAuthorFirstWordOfTitleYear}}  # 例如: VaswaniAttention2017
status: read
dateread: {{YYYY-MM-DD}}
---
```

### 2.2 引用块（Callout）

```markdown
> #### Citation
> {{Full APA Style Citation}}

> #### Synthesis
> **Contribution**:: {{单句贡献描述}}
> **Related**:: [[Key Concept 1]], [[Key Concept 2]]

> #### Metadata
> **Title**:: {{Paper Title}}
> **Year**:: {{Year}}
> **Journal**:: {{Journal Name}}
> **FirstAuthor**:: {{First Author Name}}
> **ItemType**:: journalArticle

> #### Abstract
> {{2-3 句核心贡献摘要}}
```

### 2.3 正文结构

#### 🚀 Research Gap & Hypothesis

##### Problem Context
- **Core Issue**: {{根本问题是什么？}}
- **Current Knowledge Gap**: {{现有文献缺口}}
- **Clinical/Scientific Need**: {{解决的紧迫性}}

##### Central Hypothesis
{{论文的主要假设或研究问题}}

---

#### 🔬 方法论与技术选择

##### Study Characteristics
- **Type**: {{研究类型（实验/仿真/理论分析/案例研究）}}
- **Scope**: {{研究范围}}

##### Key Techniques Evaluated
- **{{Technique 1}}**: {{应用方式}}
  - **选择理由**: {{为何选择此方法而非其他？是否有对比论证？}}
- **{{Technique 2}}**: {{应用方式}}
  - **选择理由**: {{方法选择的合理性}}

---

#### 📊 Key Mechanisms & Findings

##### {{Mechanism/Theme 1}}
1. **Concept**: {{核心概念描述}}
2. **Findings:**
   - {{Key Result 1}}
   - {{Key Result 2}}

##### {{Mechanism/Theme 2}}
...

---

#### 🔗 逻辑链 (Logic Chain)

{{从研究问题到结论的完整推理链条，使用步骤式描述：}}

1. **起点**: {{研究背景/问题}}
2. **假设**: {{核心假设}}
3. **方法**: {{验证方法}}
4. **结果**: {{关键发现}}
5. **结论**: {{最终贡献}}

---

#### 🎯 Critical Analysis

##### Strengths
1. **{{Strength 1}}**: {{具体描述}}
2. **{{Strength 2}}**: {{具体描述}}

##### Limitations
1. **{{Weakness 1}}**: {{具体描述}}
2. **{{Weakness 2}}**: {{具体描述}}

##### Open Questions
1. **{{Question 1}}?**
2. **{{Question 2}}?**

---

#### 🔗 Connections & Integration

##### Practical Implementation
- **Protocols**: {{实施细节}}
- **Tools**: {{使用的工具/框架}}

##### Personal Relevance
- **Research Interests**: {{与用户研究领域的关联}}
- **Application**: {{潜在应用场景}}

---

#### 📋 Action Items & Next Steps

- [ ] {{待研究问题}}
- [ ] {{待验证假设}}
- [ ] {{待填补知识缺口}}

---

### 2.4 总结部分

```markdown
## Summary & Conclusion

> **Key Takeaway**: {{一句话核心收获}}

#### Final Assessment
- **Innovation**: {{High/Med/Low}}
- **Evidence**: {{High/Med/Low}}
- **Clinical Potential**: {{High/Med/Low}}
```

---

## 3. Wikilinks 使用规范

对以下类型的术语使用 `[[Wikilinks]]`：

| 类别 | 示例 |
|------|------|
| 计算机科学概念 | [[Serverless Computing]], [[Microservices Architecture]] |
| 方法论名称 | [[Load Testing]], [[Chaos Engineering]] |
| 技术/框架 | [[Azure Functions]], [[Spring Boot]], [[Kubernetes]] |
| 性能指标 | [[Latency]], [[Throughput]], [[Availability]] |
| 安全概念 | [[Authentication]], [[Authorization]], [[Zero Trust]] |

---

## 4. Canvas 节点映射规则

Summary.md 中的内容应映射到 Canvas 的以下节点类型：

| Canvas 节点 | Summary.md 来源 | 边框颜色 |
|------------|----------------|---------|
| 文献元数据 | Metadata + Citation | 蓝色 `#3b82f6` |
| 研究问题 | Research Gap & Hypothesis | 橙色 `#f97316` |
| 方法论 | 方法论与技术选择 | 紫色 `#8b5cf6` |
| 主要发现 | Key Mechanisms & Findings | 绿色 `#22c55e` |
| 贡献与局限性 | Critical Analysis | 红色 `#ef4444` |
| 个人思考 | Connections & Integration | 灰色 `#6b7280` |

---

## 5. 提取优先级

当论文内容较长时，按以下优先级提取信息：

1. **必须提取**（最高优先级）：
   - 标题、作者、年份、期刊
   - 核心假设/研究问题
   - 主要方法论
   - 关键发现（至少 Top 3）

2. **强烈建议提取**：
   - 逻辑链（从问题到结论的推理）
   - 方法论选择理由
   - 局限性分析

3. **可选补充**：
   - 详细的实施协议
   - 与其他工作的详细对比

---

## 6. 特殊处理规则

### 6.1 对比类论文
如果论文是对比研究（如 Azure vs AWS），需额外提取：
- 对比维度（如成本、性能、易用性）
- 各方案的优缺点矩阵
- 推荐场景

### 6.2 综述类论文
如果是文献综述，调整结构为：
- 综述范围与时间跨度
- 分类框架（Taxonomy）
- 各研究方向的代表性工作
- 未来趋势预测

### 6.3 短论文/海报
对于篇幅较短的论文：
- 精简各章节内容
- 重点突出核心创新点
- 明确标注"Limited Details Available"

---

## 7. 质量检查清单

生成 Summary.md 前，确认以下内容：

- [ ] Citekey 符合规范（作者+首词+年份）
- [ ] 所有必填字段已填充
- [ ] Wikilinks 格式正确（双括号）
- [ ] 逻辑链完整且清晰
- [ ] 方法论包含选择理由
- [ ] 局限性分析客观公正
- [ ] 中英文混合自然流畅
