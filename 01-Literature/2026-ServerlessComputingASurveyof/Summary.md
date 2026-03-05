---
citekey: ShafieiServerlessComputingSurvey2022
status: read
dateread: 2024-01-15
---

> #### Citation
>
> Shafiei, H., Khonsari, A., & Mousavi, P. (2022). Serverless computing: A survey of opportunities, challenges, and applications. *ACM Computing Surveys*, *54*(11s), Article 239. https://doi.org/10.1145/3510611

> #### Synthesis
>
> **Contribution**:: This survey provides the first comprehensive taxonomy-driven analysis of serverless computing across eight application domains, identifying nine critical challenge categories and mapping existing solutions to domain-specific requirements, thereby establishing a structured research agenda for the field.
> **Related**:: [[Function-as-a-Service]], [[Cloud Computing]], [[Auto-scaling]], [[Cold Start Problem]], [[Microservices Architecture]], [[Edge Computing]], [[IoT]], [[Workflow Orchestration]]

> #### Metadata
>
> **Title**:: Serverless Computing: A Survey of Opportunities, Challenges, and Applications
> **Year**:: 2022
> **Journal**:: ACM Computing Surveys
> **FirstAuthor**:: Hossein Shafiei
> **ItemType**:: journalArticle

> #### Abstract
>
> This survey presents a comprehensive overview of serverless computing, categorizing applications into eight domains (real-time collaboration, urban/industrial systems, scientific computing, AI/ML, video processing, security, IoT, and e-commerce/finance) and analyzing their migration objectives and viability. The authors systematically classify challenges into nine topics—developer tools, pricing, scheduling, networking, workflows, packing, caching, provider management, and security—surveying proposed solutions and identifying open research problems.

## Notes

### 🚀 研究缺口与假设

#### 问题背景

- **核心问题**：[[Cloud Computing]] 的演进需要进一步降低运维复杂度，但现有 [[IaaS]] 和 [[PaaS]] 模型仍要求用户管理虚拟资源、配置运行时环境，且采用预置资源的计费模式导致资源利用率低下。
- **当前知识缺口**：缺乏对 [[Serverless Computing]] 跨领域适用性的系统性评估；现有文献多聚焦技术挑战本身，而非从应用域视角分析挑战的异质性；[[Function-as-a-Service]] 的性能优化与成本建模之间存在张力，尚无统一框架协调二者。
- **科学/实践需求**：云原生应用爆发式增长需要更细粒度的弹性伸缩能力；边缘计算与 [[IoT]] 场景催生超低延迟需求；企业需要可预测的成本模型以进行财务规划。

#### 核心假设

论文隐含的核心命题是：[[Serverless Computing]] 的"无服务器"抽象（隐藏基础设施、按用量计费、自动扩缩容）在特定应用域具有显著优势，但其实现受限于 [[Cold Start]] 延迟、状态管理困难、函数间通信开销等结构性挑战，这些挑战的解决方案需因域制宜。

### 🔬 方法论与证据基础

#### 研究特征

- **类型**：系统性综述（Systematic Survey），非实验性研究
- **研究范围**：2016–2021年间发表的学术论文与工业实践，覆盖8个应用域、9类技术挑战

#### 核心技术/方法

- **分类学构建（Taxonomy Construction）**：基于文献分析建立双层分类框架——应用域维度（8类）与技术挑战维度（9类），形成矩阵式分析结构
- **多源证据综合**：整合工业平台文档（AWS Lambda, Azure Functions, Google Cloud Functions, OpenWhisk）、学术研究原型、以及定量性能评估数据
- **批判性评估（Critical Assessment）**：对每个应用域，从迁移动机（Migration Objectives）、范式适配性（Paradigm Aptness）、报告挑战（Reported Challenges）三维度进行评估

### 📊 核心机制与发现

#### 应用域差异化分析

1. **概念**：[[Serverless Computing]] 的适用性高度依赖应用特征——状态依赖性、通信模式、延迟敏感度、计算强度构成四维评估空间

2. **发现：**
   - **高适配域**：[[Real-time Collaboration]]、[[IoT]]、[[Security Applications]] 因事件驱动、突发流量、弹性需求与无状态特性高度契合，评估为"Promising"
   - **条件适配域**：[[Scientific Computing]]、[[Machine Learning]]、[[Video Processing]] 受限于 [[Fine-grained Communication]] 需求或 [[Memory-intensive]] 特性，仅当任务可分解为粗粒度、低通信子任务时可行
   - **经济敏感域**：[[Urban Management Systems]] 在预算约束场景（发展中国家公共部门）因 [[Pay-as-you-go]] 模型展现独特价值

#### 挑战-解决方案映射

1. **概念**：技术挑战存在显著的域间异质性，需区分通用挑战（如安全、调度）与域特定挑战（如科学计算的 [[Checkpointing]]、视频处理的 [[GPU Acceleration]]）

2. **发现：**
   - **[[Cold Start]] 缓解**：预热容器池（ENSURE, Fifer）与概率性函数链预测（Xanadu）代表两种范式——前者牺牲资源效率换取延迟保证，后者依赖执行历史的学习
   - **[[Data Locality]] 优化**："函数向数据移动"（Shredder）与"数据向函数移动"（Kayak 的自适应选择）形成设计权衡空间
   - **[[Cost Prediction]]**：蒙特卡洛模拟（Eismann et al.）与贪婪启发式（PRCP）在准确率（96–98%）与计算开销间取舍

### 🎯 批判性分析

#### 优势

1. **分类学的系统性与完备性**：首次建立应用域-技术挑战的双维矩阵，突破了以往综述单维度罗列的局限，为后续研究提供可扩展的分析框架

2. **工业-学术桥梁作用**：紧密跟踪主流云平台演进（如 AWS Step Functions、Firecracker、Greengrass），同时挖掘学术研究原型（Catalyzer, Cloudburst, InfiniCache），揭示技术转移的时间差与障碍

3. **前瞻性研究议程**：明确识别12个开放问题，包括 [[Probabilistic DAG Scheduling]]、[[Next-basket Recommendation for Package Prediction]]、[[Lightweight Security Protocols for IoT]] 等具体方向

#### 局限性

1. **量化比较不足**：虽引用性能数据，但未建立标准化的基准比较框架；不同研究的实验设置（负载特征、平台配置、度量指标）差异显著，难以进行元分析

2. **动态演化追踪有限**：Serverless 领域技术迭代极快（如2021年后 [[Kubernetes-native Serverless]]（Knative）、[[WebAssembly]] 运行时兴起），部分结论可能已过时

3. **多目标优化张力未充分展开**：成本、延迟、吞吐量、能源效率的帕累托前沿分析缺失，现有解决方案多为单目标优化

#### 开放问题

1. **如何在 [[Multi-cloud Serverless]] 环境中实现最优函数放置与动态定价的联合优化？**

2. **[[Serverless Machine Learning]] 的训练-推理协同调度：如何平衡检查点开销与抢占风险？**

### 🔗 关联与整合

#### 实践层面

- **具体做法**：
  - 工作流定义：优先采用平台无关语言（AFCL）或标准编程语言（Azure Durable Functions）而非专有JSON格式（ASL）
  - 缓存策略：结合 [[Packing]] 决策——若函数已打包至数据附近，优先采用本地缓存；否则启用分布式缓存（DHT-based）
  - 监控部署：采用采样追踪（AWS X-Ray 模式）应对大规模场景下的观测开销

- **工具**：OpenWhisk（开源参考实现）、vHive（实验框架）、FaaSdom（成本估算）、DeathStarBench（微服务基准）

#### 与个人研究的关联

- **研究兴趣**：与 [[Edge Intelligence]]、[[Federated Learning]] 的系统支撑高度相关——Serverless 可作为边缘节点的轻量级执行抽象，但需解决 [[Heterogeneous Edge Resources]] 下的调度问题

- **应用场景**：探索 [[Serverless Video Analytics]] 中的 [[Query Optimization]]——利用论文所述的 [[Workflow-aware Scheduling]] 与 [[Dataflow-aware Scheduling]] 组合，实现多摄像头流的自适应处理管道

### 📋 行动项与后续步骤

- [ ] 深入调研 [[Firecracker]] 与 [[gVisor]] 的安全隔离机制对比，评估其在 [[Confidential Computing]] 场景的可扩展性

- [ ] 验证 [[COSE]]（贝叶斯优化配置选择）在真实 ML 推理工作负载上的有效性，对比其与 [[AWS Lambda Power Tuning]] 工具

- [ ] 填补 [[Serverless Scientific Computing]] 中 [[Fault Tolerance]] 机制的知识缺口——现有方案多假设独立任务，缺乏对 [[MPI-like Collective Operations]] 的支持分析


## 总结与结论

> **核心要点**：Serverless computing 的价值主张具有条件依赖性——其"DNA"（无状态、事件驱动、细粒度计费）决定了在突发负载、低状态依赖场景中表现优异，但在需要精细通信控制或持久状态的场景仍需架构层面的补偿机制。

#### 最终评估

- **创新性**：高（首个应用域驱动的系统性综述，建立可扩展的分类框架）
- **证据质量**：中（依赖二手文献综合，缺乏原始实验；但引用覆盖面广，工业洞察深入）
- **实践潜力**：高（直接指导技术选型与迁移决策，开放问题清单具明确的研究-产业转化路径）