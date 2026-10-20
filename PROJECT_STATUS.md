KG Agent Master Thesis Project Status

Last Updated: 2026-10-08

1. Project Goal

本项目旨在设计、实现并定量评估一个面向专业领域知识图谱的 Knowledge Graph Agent，重点研究 Agent 是否能够：
正确理解自然语言问题；
完成多跳知识图谱推理；
正确调用知识图谱工具并使用检索结果；
生成正确、完整且可自动评价的最终答案；
在知识图谱信息不足时合理拒答；
避免仅依靠语言模型的预训练知识或猜测作答。

项目以现有第一版 KG Agent 原型为起点，而不是从零开始。论文将分析现有原型的架构和局限，设计至少一个改进版本，并与第一版原型及适当的基线方法进行比较。与此同时，项目需要分析现有 KGQA 数据集是否能够验证 Agent 真正使用了知识图谱；必要时定义或构建更适合专业工业场景的补充评测数据。

项目未来的目标应用场景是导师团队正在设计和构建的 Circular Factory Knowledge Graph。该知识图谱预计采用 RDF/OWL，而不是 property graph，其结构将更接近 GTSQA 使用的知识图谱。由于该图谱目前尚未完成，当前论文实验将优先使用具有相关结构特征的现有数据集验证 Agent 架构和评测流程，并为未来迁移到 Circular Factory Knowledge Graph 做准备。

项目最终可能包含：
KG Agent 与 KGQA 相关文献调研；
KGQA 数据集系统分析与选择；
Agent 能力与评测框架设计；
统一结构化输出与运行日志设计；
改进版 KG Agent 架构设计与实现；
自动化 Evaluation Program；
对照实验、误差分析和消融分析；
硕士论文撰写。

2. Current Phase

当前主要阶段：
ARK_V1 适配版的基线边界梳理、GTSQA 与 GTSQA_UA 开发数据及评测流程核验、开发实验结果整理，以及面向后续 ARK_V2 的失败模式分析阶段。

项目已经完成初步课题定义、评测框架设计、少量优先候选 KGQA 数据集的深入分析，以及第一阶段 GTSQA 数据和 ARK_V1 接入工作，但尚未进入 ARK_V2 的正式实现。第三次导师会议形成了以 KQA Pro 小型 pilot 为起点的阶段性方案；导师随后根据未来 Circular Factory Knowledge Graph 的 RDF/OWL 形式和预期结构，进一步确认并调整了数据集与实施顺序。第四次导师会议进一步将近期工作聚焦到 GTSQA pilot、ARK_V1、Langfuse tracing、自定义 evaluator 和实验结果提取组成的端到端工作流。此前会议提出的 incoming relations 已实现，当前代码也已加入多样本顺序实验、实体答案精确匹配、拒答评价和图证据覆盖评价。

当前重点不是从零开始筛选或重新提取 GTSQA 样本，也不是立即开发复杂 Agent，而是核验已经建立的开发数据、适配版 Agent 和评测管线之间的一致性；明确当前基线包含的数据适配、可靠性修复与局部行为调整；整理可复查的逐题结果和汇总结果；并通过运行轨迹识别修复后仍然存在的主要失败模式。CR-LT-KGQA 深入核验仍属于后续核心工作。GTSQA_UA 已有第一版 12 对、24 项开发数据及相应适配和评价实现，后续重点转为验证记录整理、实验分析和构造边界检查，而不是从零开始构造。

当前代码实现不等于所有开发实验已经完成或结果已经核验。实验入口当前默认选择 3 道 GTSQA 问题，使用实体精确匹配和图证据覆盖 evaluator；24 项 GTSQA_UA 的样本选择配置保留在代码注释中。整批实验是否完成、评分是否完整及实际性能，应以对应的实验结果和 trace 为准，不能仅根据配置或提交记录认定。

当前阶段的具体目标：
将 Agent Capability、Test Task、Dataset Requirement、Ground Truth、Logging Requirement、Evaluation Metric 和 Implementation Method 明确区分并建立对应关系。
确定硕士论文的最小可执行评测范围，避免同时实现过多能力、指标、数据集和 Agent 版本。
继续核验与当前实验直接相关的 GTSQA、GTSQA_UA 数据和实际样本，并深入核验 CR-LT-KGQA，重点记录和判断：
Question Type(s)；
Expected Solving Strategy；
Answer Type；
Answerability；
Hop Count；
Gold Query / Logical Form / Program；
KG 可访问性；
Question Construction；
Domain / Knowledge Exposure；
Relevance to Thesis。

当前整理的六类 Reference Question Patterns 仅用于辅助对照不同数据集中的问题结构，不作为 Mandatory Classification Scheme。数据集已有的官方分类应优先保留；只有在能够自然对应时，才补充其与参考类型的对应关系。

确定哪些能力采用自动定量评价，哪些能力只进行少量案例分析。
固定统一结构化答案和最小运行日志接口，使未来可能采用的不同 Agent 架构都能够进入相同评测流程。
数据集分析与评测设计相互迭代：通过 GTSQA 和 CR-LT-KGQA 的实际问题类型、标注、图结构和 KG 可访问性验证评测方案；核验基于受控事实删除构造的 GTSQA_UA；再反向确定 ARK_V1 适配版的剩余必要需求和 ARK_V2 的具体功能需求。
区分“已实现”“已有保存的验证记录”“已完成且核验的实验”和“尚待开展的分析”，避免将代码存在或实验配置存在直接解释为性能证据。
整理原始 ARK_V1、当前适配版和后续 ARK_V2 的关系，保留可追踪的代码、Prompt 和实验配置记录。

当前实施顺序为：
1. 整理已实现的 GTSQA 适配、重试与路由修复、答案处理和评测功能，核验开发数据与 Agent 输入、Gold Data 之间的一致性；
2. 明确适配版 ARK_V1 的基线边界，评估 seed entities 直接使用、返回上限或分页、截断记录等剩余需求是否属于冻结前的必要范围；
3. 核验现有 Langfuse 多样本实验、item-level evaluator、run-level evaluator、结构化结果和结果提取流程；
4. 整理并在需要时补充 GTSQA 开发子集实验，形成逐题结果、汇总结果和真实失败模式分析；
5. 核验现有 GTSQA_UA 的 12 对、24 项开发数据、构造验证记录及回答/拒答评价流程，并分析配对实验结果；
6. 进一步核验 CR-LT-KGQA，并完成 ARK_V1 对 CR-LT-KGQA 所需的最小适配；
7. 对冻结后的适配版 ARK_V1 开展第一轮系统评测；
8. 根据真实失败案例和相关文献设计 ARK_V2，并在 GTSQA、GTSQA_UA 和 CR-LT-KGQA 的小型子集上迭代测试；
9. 运行完整实验；
10. 条件允许时，将 ARK_V2 扩展到 KQA Pro。

3. Confirmed Decisions

项目以现有第一版 KG Agent 为基线，后续将实现至少一个改进版本并进行定量比较。
第一版 Agent 是可运行的早期原型，但其推理流程、工具调用、图查询和答案生成仍需要系统分析和改进。
论文不能仅以最终答案正确作为 Agent 有效性的证明，还需要判断答案是否来自实际知识图谱检索结果。
评测数据应尽量包含语言模型预训练阶段不太可能掌握的专业知识、长尾实体或人工构造知识，以降低模型凭记忆直接作答的可能性。
评测设计需要区分 Agent Capability、Test Task、Dataset Requirement、Ground Truth / Annotation、Logging Requirement、Evaluation Metric 和 Implementation Method。数据集字段要求与逐题标准值、日志字段与实现节点、能力与指标之间不能混为一谈。

当前核心定量评价方向为：
Multi-hop Reasoning；
Final Answer；
Refusal；
Graph Grounding。

Problem Understanding 暂不设置大规模独立定量指标，主要通过少量代表性执行轨迹、案例分析和错误分类进行评价。
不要求数据集为每道问题人工标注完整的标准推理链或 supporting_triples。对于 GTSQA 已提供的 Gold answer subgraph，可以直接利用其进行证据覆盖评价，不需要另行人工构造完整推理链。
Agent 不需要输出完整自然语言思维过程，但需要记录实际工具调用、查询输入、检索结果和执行状态。
数据集保存评测输入和标准信息，例如 question、gold_answer、answer_type、hop_count 和 answerable；运行日志保存 Agent 的实际执行结果，例如 predicted_answer、answer_status、execution_status 和 tool_calls。两侧通过数据集 id 与日志 sample_id 关联。

不同 Agent 架构应在自然语言回答生成前增加统一的结构化答案输出步骤，并提供：
answer_payload；
predicted_answer；
final_answer_text；
answer_status；
execution_status 等字段。

统一结构化答案流程的设计为：答案整合 → 结构化答案节点 → answer_payload → 答案规范化 → predicted_answer → final_answer_text。answer_payload 是 Agent 整合检索结果后认定的原始结构化答案；predicted_answer 是按照数据集答案类型和规范化规则转换后的评测答案。规范化只能统一表示形式，不能纠正 Agent 的错误答案。
当前实现由 Agent 生成结构化最终答案，由 Evaluation adapter 提取 answer_payload 和状态，由 evaluator 进行答案规范化与评分；上述全部字段是否统一进入独立结果记录，仍需核验与完善。
结构化答案中，null 表示无法根据 KG 确定答案；[] 表示问题可回答，但正确结果是空集合。二者必须区分，以支持 Final Answer 和 Refusal 的确定性评价。
answer_status 与 execution_status 必须分开记录，避免把查询失败误判为正确拒答。
tool_calls 的设计要求是每次实际工具调用对应一个独立对象。多跳查询、失败重试和重新规划均应新增记录，不覆盖之前的失败调用；工具调用次数不等于问题跳数。当前 Langfuse trace 与这一统一日志设计之间的完整映射仍需核验。

Graph Grounding 的最低实现主要依赖：
结构化最终答案；
Agent 实际获得的 KG 检索结果；
可访问的目标知识图谱。

当前 GTSQA 已实现的 Graph Grounding 代理指标为 graph_evidence_coverage：将 Agent 保留的、已完成且有效的推理步骤中选择的 triples 与 Gold answer subgraph 进行规范化后比较，计算匹配 Gold triples 占全部 Gold triples 的比例。
该指标不同于早期讨论的 Answer–Retrieved Result Consistency 和 Retrieved Fact Validity Rate，不能将几者混称为同一个已实现指标。
当前 used_triples 不是全部工具返回的 triples，也不等于完整的运行历史；它反映从最终保留的有效推理步骤中提取的所选证据。

统一 KG 工具封装层属于未来可选设计，不是当前最小评测框架的强制实现。
RAG 可以作为候选基线，但只有在能够保证信息输入和实验条件基本公平时才加入正式实验。
最终使用的语言模型暂不提前锁定，应在实验设计确定后根据模型能力、可获得性、Token 成本和可复现性选择。
KGQA 数据集分析不仅记录所使用的查询语言，还需要分析问题本身要求完成什么操作，即 Question Type 与 Expected Solving Strategy。Gold Query、Logical Form 或 Program 可作为辅助证据，用于判断问题实际要求的检索、组合、比较、聚合或其他操作。
当前六类 Reference Question Patterns 是数据集调研的参考框架，不是最终确定的问题类型集合，也不要求所有数据集问题强制映射到其中。

导师最新确认的数据集路线为：GTSQA 和 CR-LT-KGQA 作为当前主要评测数据集；参考 GrailQAbility 的受控删除或知识图谱不完整性构造方法，基于 GTSQA 创建 GTSQA_UA，用于不可回答问题和 Refusal 能力评测；KQA Pro 作为条件允许时的可选扩展，不属于当前核心实验范围。
未来的 Circular Factory Knowledge Graph 将采用 RDF/OWL，而不是 property graph，其结构预计更接近 GTSQA。当前以 GTSQA 为核心开展适配和实验，有助于提高所设计 Agent 向未来工业知识图谱迁移的可能性。
Circular Factory Knowledge Graph 目前仍处于设计和构建阶段，因此当前论文实施不能直接依赖该图谱完成。论文应优先通过现有数据集建立可运行的 Agent、实验管线和评测证据。

已选择 12 道 GTSQA test 问题作为初始开发候选集，覆盖 6 种四边图结构，每种结构 2 题。所选问题均为非冗余、单一 gold answer 样本，并排除了 unseen relation type，以减少关系词汇泛化对图结构推理分析的干扰。
12 道候选问题对应的完整 question-specific graphs 已成功提取，每题约包含 6,093–27,293 条边。ARK_V1 和 ARK_V2 应逐题载入对应图，完成运行后释放，不应将 12 张图合并为一个知识图谱。
ARK_V1 接入 GTSQA 的已知适配方向包括：统一 triple schema；保留同一实体对之间的多种关系；支持 incoming 和 outgoing 查询；限制或分页返回 triples；直接使用数据集提供的 seed entities；记录图规模、工具返回数量和截断状态。其中 triple adapter、MultiDiGraph 和双向查询已实现，其余需求应结合实际风险确定是否纳入基线冻结前的必要范围。

ARK_V1 首先需要进行支持 GTSQA 和 CR-LT-KGQA 所必需的适配。适配范围应优先覆盖数据转换、图访问、查询接口、答案输出和 Agent Tracing，同时尽量保持 ARK_V1 原有的核心图探索和搜索策略，以使其能够作为清晰且可解释的基线。
会议确认，为使第一版 Agent 能在 GTSQA 上进行有意义的比较，可以在适配版中加入 incoming relation 查询能力。该能力涉及图访问和 Agent 可用操作，应明确记录为基线适配的一部分。
当前适配版除数据与接口适配外，已经包含 anchor/relation 重试与路由修复、状态重置、结构化输出失败处理及部分 Prompt 调整。因此，不能将其描述为完全未经行为修改的原始 ARK_V1，也不能将所有改动统称为数据格式适配。
原始 ARK_V1 与 GTSQA 适配版应保留明确的版本和实验配置记录。关系选择 Prompt 等变化可能影响旧数据集上的结果，因此不能将适配版的结果直接视为原始版本在相同条件下的结果。可在旧数据集上运行适配版，检查这些变化的影响。
一旦 ARK_V1 能够稳定运行所选数据集和开发子集，就不应继续无限扩大旧版 Agent 的修改范围，以保证 ARK_V1 与 ARK_V2 之间比较的公平性。

当前适配版统一命名为 ARK v1.1：目录为 agent/ark_v1_1，Python 包和实验标识为 ark_v1_1，类名为 ARK_V1_1，Evaluation adapter 为 Evaluation/adapters/ark_v1_1.py。共享环境位于根目录 .venv，共享配置位于根目录 .env。历史记录中的适配版 ARK_V1 对应此版本，历史实验名称保持原样。上游原版尚待独立导入，具体冻结提交及配置仍需明确。重命名后需要重新注册 editable 包；随目录保留的旧虚拟环境不再使用，待确认后清理。
将当前版本定位为“经过数据适配与可靠性修复的增强基线”是当前的版本整理建议，不代表已经获得导师对该正式名称或贡献划分的确认。
基线边界应区分图与数据适配、实现正确性修复、输出处理增强和探索策略改进，不以是否提高准确率作为唯一分类依据。

学生的新 Agent 应作为独立的新版本 ARK_V2 设计，而不是无限延续对 ARK_V1 的增量修改。ARK_V2 的具体架构仍保持开放，应根据 ARK_V1 在 GTSQA、GTSQA_UA 和 CR-LT-KGQA 上的真实失败案例确定。
当前关于 ARK_V2 的问题与约束分析、多锚点和多路径探索仅属于初步构想。可以复用第一版中适用的图接口和工具，但是否复用以及如何组织工作流，需要结合相关文献和实验结果确定。
后续也可以复用适用的模型调用封装和 Pydantic 数据模型；ARK_V2 的区别应体现在其解决的问题、状态表示、探索决策或证据整合机制，而不是要求所有组件重新实现。
在正式设计 ARK_V2 前，应先核验 Dataset Input、Graph Access、Agent Execution、Structured Logging、Normalized Prediction、Ground Truth、Metric Calculation 和 Result Storage 的端到端工作流。
ARK_V1 的第一轮评测用于建立初始性能基准、了解 Agent 的实际表现并识别主要失败模式，不应直接被解释为最终架构评测。
ARK_V2 开发阶段应优先在 GTSQA、GTSQA_UA 和 CR-LT-KGQA 的小型代表性子集上进行迭代测试。在 ARK_V2 设计稳定并完成小型子集测试后，再开展完整实验。

KQA Pro 属于可选扩展。只有在核心路线已经完成且时间、实现成本和计算预算允许时，才将 ARK_V2 扩展到 KQA Pro。此前对 KQA Pro 的 qualifier、属性读取、数值比较和 Boolean verification 等能力的分析仍可用于未来可选扩展以及复杂答案类型设计，但不再决定当前第一阶段的实施顺序。
对 CR-LT-KGQA 的初步理解是：它为每道问题提供相关 KG triples，并要求系统结合这些证据与 commonsense knowledge 产生 Boolean 答案，因此可能更适合作为 KG-grounded commonsense reasoning 的补充评测，而不是主要的图检索评测。该理解仍需通过数据文件、论文和实际样本进一步核验。
知识图谱中缺少事实但模型可通过预训练知识或常识回答时，应区分 Graph Answerability、External Knowledge Answer、Unsupported Hallucination 和 Correct Refusal。该区分具有研究价值，但是否进入正式大规模实验仍需通过少量样本验证并控制标注成本。
数据集中的问题应作为相互独立的 Agent runs 执行。第一版评测执行器采用简单可控的顺序执行；云端调用可在成本和速率限制可控时加入有限并发。为每个问题启动 sub-agent 会引入独立的 Multi-Agent Architecture 问题，当前不属于论文主要范围。
开发和调试阶段优先使用导师提供的 OpenRouter API Key 和低成本模型。最终模型组合仍不提前锁定；导师将继续确认是否可以远程开放工作站上的 Ollama 服务。

GTSQA_UA 当前 pilot 采用 controlled fact deletion。每个原始问题对应一个 original 对照项和一个 ua-01 变体，保存原始答案、删除 triples、验证查询和验证结果，不额外持久化每个变体的完整图副本。
当前构造的不可回答操作性定义为：原始查询在原图上返回与 Gold 一致的非空答案；相同查询在删除后的图上成功执行并返回空结果。查询执行失败不能作为不可回答标签。
Gold、answerable、SPARQL query 和删除记录用于数据构造与评价，不作为 Agent 问题输入或图探索提示。
当前 UA evaluator 评价的是回答/拒答决策，不评价回答内容本身是否正确；可回答对照项上的错误答案仍可能具有正确的“回答”决策。
开发原题及由其生成的 UA 配对变体应保持相同的数据划分，不能将原题用于开发后再把其 UA 变体作为独立的无偏测试样本。

Langfuse 将作为当前实验的运行追踪和实验管理工具，用于保存 Agent trace、Token 用量、执行时间、Prompt 版本和 evaluator 结果。论文所需的规范化答案、状态字段和指标仍由项目自己的统一评测结构定义。
Langfuse 的使用减少了自行实现底层 tracing 的需要，但不能替代论文特定的答案规范化、Gold Answer 比较、执行状态判断和实验结果分析。
Langfuse 数据集中的每个数据项应至少包含 input、expected output 和 metadata。当前 GTSQA 的 input 为问题文本，expected output 包含 Gold Answer 和 Gold answer subgraph，metadata 保存 sample_id；运行时通过 sample_id 读取本地 question-specific graph。当前 GTSQA_UA 的 expected output 包含 answerable，metadata 保存样本标识与数据集类型。
Langfuse evaluator 可以在单个数据项运行完成后执行，也可以在完整数据集实验结束后计算汇总结果。当前已实现 item-level 和 run-level evaluator，后续重点是核验评分完整性、失败计数和汇总分母。
实验记录应保存 Agent 版本、数据集和样本标识、模型、温度、Prompt 版本等必要配置。当前实验 metadata 已保存 Agent 标识、Agent 配置、数据集类型、数据集名称和样本数量；精确代码版本、实际 Prompt 版本及全部运行条件的完整记录仍需核验与完善。
正式性能比较还需考虑随机种子、重复运行次数和结果波动，具体规模应结合预算确定。
Prompt Management 可用于保存和版本化实验 Prompt，使运行结果能够关联到明确的 Prompt 版本。是否将全部 Prompt 迁移到 Langfuse 仍可根据实现复杂度决定，但正式实验必须能够追踪实际使用的 Prompt 或版本标识。

4. Current Progress

4.1已完成

已完成第一次导师会议的校订转录和详细中英文总结。
已完成第二次导师会议内容整理，进一步明确当前下一步应聚焦 KGQA 数据集及其 Question Type。
已完成第三次导师会议的详细中英文对照总结，并整理了 KQA Pro、GrailQAbility 和 GTSQA 的阶段性分工、ARK v1.1 的最小适配原则以及先建立评测工作流再设计新 Agent 的执行思路。
已完成第四次导师会议的详细中英文对照总结，明确近期应围绕 GTSQA pilot、ARK_V1、Langfuse tracing、自定义 evaluator 和实验结果提取建立端到端实验流程。
已获得导师对更新后项目路线的回复，明确未来 Circular Factory Knowledge Graph 将采用 RDF/OWL、其结构更接近 GTSQA，并确认以 GTSQA、GTSQA_UA 和 CR-LT-KGQA 为核心，KQA Pro 作为可选扩展的实施顺序。
已明确课题背景、初步研究目标、预期实验方向和导师对论文的基本要求。
已复现并初步理解第一版 KG Agent 的工作流程。
已完成当前版本的 Exposé，明确论文题目、研究动机、主要目标和预期方法。
已形成硕士论文详细章节提纲，包括：
Background；
Existing Agent Analysis；
Improved Agent Design；
Experimental Design；
Results and Discussion。

已建立初步 Agent 能力评测框架，并区分核心定量评价与辅助案例分析。
已整理自建数据集和现有评测数据集所需的主要字段。
已设计统一结构化答案节点、最小运行日志字段和 tool_calls 记录方式。
已形成 Graph Grounding 的早期候选方案：Answer–Retrieved Result Consistency；
条件允许时计算 Retrieved Fact Validity Rate。
当前已进一步实现基于 GTSQA Gold answer subgraph 的 graph_evidence_coverage，早期候选方案与当前实现应分别记录。

已初步建立七个评测层次之间的关系，并分别澄清 Final Answer、Refusal、Multi-hop Reasoning 和 Graph Grounding 的数据需求、日志需求、指标及主要局限。
已明确 gold_answer、answerable 和 hop_count 属于数据集标准侧；predicted_answer、answer_status、execution_status 和 tool_calls 属于 Agent 运行侧。
已明确多跳问题的工具调用次数不等于 hop_count；当前 Multi-hop 指标设计主要反映按题目跳数分组的最终答案表现。

已建立 KGQA 数据集候选来源清单，包括通用 KGQA、多跳推理、不可回答问题、长尾知识和工业工程领域数据资源。
已初步识别 BuildingQA、KGQA4MAT、GrailQAbility、KQA Pro 等值得进一步分析的数据集或结构参考。
已整理六类 Reference Question Patterns，用于辅助识别 Entity Lookup、Single-Hop Retrieval、Single-Anchor Branching、Multi-Anchor Combination、Relation / Path Discovery 以及 KG Retrieval + External / Operation Reasoning 等典型问题模式。
已明确 Reference Question Patterns 只作为辅助对照，不替代数据集原有的 question taxonomy。
已通过代表性样本进一步分析 KQA Pro 的 qualifier、属性读取、数值比较和 Boolean verification 要求。
已初步分析 GrailQAbility 通过删除 entity type、relation、entity 或 fact 构造受控不可回答问题的方法及其实现成本。
已初步分析 GTSQA 的线性路径、多 seed intersection、不同深度分支、projection 及 answer subgraph 字段对 Graph Grounding 的价值。
已读取和分析 GTSQA 无图 test 数据。该数据包含 1,622 道问题和 14 种 graph-isomorphism structures，并提供 id、question、seed_entities、answer_node、all_answers_wikikg2、full_answer_subgraph_wikikg2、n_hops、graph_isomorphism 和 test_type 等可用于开发与评测的字段。
已按照图结构覆盖原则初步选择 12 道 GTSQA 问题，每种关键四边结构选择 2 题，覆盖纯四跳链、双路径交集、多条件汇聚、分支约束、intersection 后继续遍历和时序关系链等结构。
已确定 12 道候选问题的 ID：13311、37715、40154、42587、4519、8865、16154、31606、33122、40487、1012 和 41371。所选问题均为非冗余、单一 gold answer 样本，排除了 unseen_relation_type，属于 unseen_graph_type，且 gold answer subgraph 包含 4 条边。
已成功从 GTSQA 带图 test 数据中提取 12 道候选问题对应的完整 question-specific graphs。12/12 道问题均成功匹配，每题约包含 6,093–27,293 条边。
已按 12 个选定 ID 生成 GTSQA Agent Input 和 Gold Evaluation Data，并通过稳定 id 建立对应关系。Agent Input 当前包含 id、question 和 question-specific graph；Gold Data 包含数据集说明、字段定义和 12 条问题级标准信息。
已实现基础 GTSQA adapter，将 GTSQA 的 [head, relation, tail] triple 转换为 ARK_V1 当前使用的内部顺序，并对输入字段和 triple 数据进行基本验证。
已将 ARK_V1 的本地图结构调整为 MultiDiGraph，从而保留同一实体对之间的多种关系。
已修正 ARK_V1 节点与关系候选索引处理，并增加与 GTSQA 图规模和实体候选相关的分析脚本。
已实现 ARK_V1 的 YES_NO 和 ENTITY_LIST 两种结构化最终答案模型。
已明确结构化 Entity List 答案中 None 表示无法根据 KG 确定答案，[] 表示问题可回答但正确结果为空集合，并已编写相应测试。

已实现 incoming 和 outgoing relation 查询，并在关系候选中保留相对于当前 anchor 的方向。关系选择使用 relation-direction pair，检索结果保持事实原有的 head、relation、tail 方向。
已加强 relation-selection Prompt：向模型提供当前 anchor 和可用 relation-direction pairs，要求模型返回准确的关系名称和方向，并解释 incoming traversal、候选有效性及空关系值请求换 anchor 的含义。
已修正第一次 retry feedback 的触发条件，以及换 anchor 时跳过提示更新的问题。
已调整 anchor/relation 路由判断顺序，使有效选择优先于尝试次数上限处理，避免最后一次成功仍被提前终止。
已在重新获取 anchor 的关系候选时重置 relation 选择状态，并在每次 relation 尝试前清除上一轮结果，避免旧状态干扰。
已区分 relation structured-output parsing failure、显式空关系值请求换 anchor、无效关系选择和有效关系选择，并提供相应重试反馈。
已加入可选的答案 QID 补全：从已完成推理步骤的 triples 提取实体名称与 QID 对应，对唯一匹配补全 QID，对无法匹配或存在歧义的答案保持原状。
已记录探索终止原因，包括 anchor、relation、reasoning 尝试上限、exploration limit、model stop 和其他停止情况，并将终止原因传递到评测输出及拒答汇总。
已修复哈希随机数相关实现，并将 FAISS 搜索限制为单线程，以处理已观察到的运行稳定性问题。

已通过 OpenRouter 和 LiteLLM 两条调用路径对 GTSQA 四跳样本 13311 进行了初步运行，两次运行均得到正确的 Entity List 答案 “Alzheimer's disease (Q11081)”。
已保存样本 13311 的两份初步运行结果，用于检查 ARK_V1 的四跳搜索过程、Prompt 行为、结构化输出和失败重试。
已初步观察到 LiteLLM 运行中可能出现 structured-output parsing failure，但 Agent 在该次运行中能够重试并继续完成问题。该现象需要在后续实验中作为 execution error 或 recoverable retry 记录。
上述样本结果属于早期探索性运行，不代表当前版本在固定配置下的整体性能。

已初步分析 ARK_V1 接入 GTSQA 的具体接口限制，包括多关系边可能被覆盖、缺少 incoming-edge 查询、triple 顺序不一致、每题重复生成 embedding、工具结果缺少分页或返回上限等问题。其中多关系边保留、双向查询和 triple adapter 已实现，其余问题仍需按必要性与成本处理。
已初步确定 ARK_V1 接入 GTSQA 的适配方向：建立明确的 GTSQA adapter 和内部 triple schema；保留同一节点对之间的多种关系；支持 incoming 和 outgoing 查询；为关系和 triple 返回增加分页或统一上限；直接使用 GTSQA 提供的 seed_entities；逐题载入并释放图；记录导入边数、节点数、工具返回数量和截断状态。该清单不表示所有项目均已实现或必须在当前阶段全部实现。
已初步分析 CR-LT-KGQA 的任务定位：其相关 KG triples 可能主要作为给定证据，Agent 仍需结合 commonsense knowledge 产生 Boolean 答案，因此它可能适合作为 KG-grounded commonsense reasoning 的补充实验。
已确定 ARK_V1 应作为第一轮实验基线，ARK_V2 应根据 ARK_V1 的真实失败案例独立设计。
此前已完成的 KQA Pro pilot、qualifier 和复杂答案类型分析仍可作为未来可选扩展和接口设计参考，但不再属于当前核心实施路线。

已为 ARK_V1 接入 Langfuse callback 和实验配置传递，并建立包含数据准备、Agent adapter、运行任务、item-level evaluator 和 run-level evaluator 的实验入口。
已支持按显式 SAMPLE_IDS 选择多个样本并顺序执行，保留逐题进度和错误信息，减少默认详细输出。
已实现 GTSQA 数据准备阶段的问题文本一致性、triple 格式、Gold answer 和 Gold evidence 格式检查，以及 Langfuse dataset item 的创建、更新和一致性核验逻辑。
已实现 Entity List 答案的 QID 规范化和精确集合匹配，并区分无答案与规范化失败。
已实现计划样本数、执行完成数、执行失败数、评分数、正确数、拒答数和评分完整性等汇总记录，以及端到端准确率和执行失败率的计算逻辑。
已实现独立的 execution_status、answer_status、error_type 和 termination_reason 记录，避免将执行错误直接计为正常拒答。
已预先登记计划执行的样本，使失败任务不会因没有正常输出而直接从实验统计中消失。

已实现 GTSQA_UA 构造脚本，并保存第一版 12 对、24 项开发 Gold 数据，包含 12 个原始对照项和 12 个事实删除变体；已保存文件中 skipped 为空。
已保存原始答案、删除 triples、SPARQL query 和 validation 结果；当前构造配置最多删除 2 条事实。
构造程序已实现原图查询答案与 Gold 一致性检查、Gold evidence 在原图中的包含关系检查、实际删除与记录一致性检查，以及修改后查询为空的验证。已保存数据包含 passed 验证记录，但本次状态整理未重新运行构造程序。
已实现 GTSQA_UA adapter，通过原始图与删除记录重建变体，并在 Agent 执行前核验原图答案、修改操作和修改后查询结果。
已将 Gold 答案、answerability 标签、验证查询和删除元数据与 Agent 输入分离。
已实现 GTSQA_UA 的回答/拒答决策 evaluator 及运行级汇总，并在实验入口保留完整 24 项样本选择配置。配置存在不等于整批实验结果已经完成核验。

已实现 GTSQA graph_evidence_coverage，并从最终保留的、已完成且有效的推理步骤中提取 used_triples。
已实现 triples 的 QID/PID 规范化、与 Gold answer subgraph 的集合比较、逐题覆盖率及运行级汇总。
证据提取失败会记录 used_triples_error，不直接将已经完成的 Agent 执行或实体答案评价改判为失败；图证据评分的可用性需单独检查。

根据此前会议报告，已在约 6 道 GTSQA 问题上进行探索性试跑，其中约 1 道得到正确答案。会议当时将缺少 incoming relation 查询识别为重要限制。该结果尚未构成固定配置下的正式准确率，也不能据此单独归因所有失败；incoming 查询现已实现，应结合后续结果重新分析。
已形成 ARK_V2 的初步构想，包括先分析问题与约束，再探索多个 anchor 和路径；尚未确定最终架构。

4.2正在进行

核验已经生成的 12 条 GTSQA Agent Input、Gold Evaluation Data 和 question-specific graph 之间的 id、question、seed、gold answer 和 gold answer subgraph 一致性，并整理已有程序检查覆盖的范围。
检查每道题必要的图规模、关系类型数量、seed 邻居规模和潜在工具返回风险信息，并根据一致性和接口风险最终冻结 12 道开发问题。
将已发现的 ARK_V1 图接口问题收敛为正式的 Compatibility and Adaptation Contract，明确已完成项、剩余必要适配以及不属于 ARK_V1 基线范围的功能。
评估 seed entities 的直接使用、triple 返回上限或分页、工具返回数量和截断状态记录是否属于基线冻结前的必要需求，避免继续无边界扩展适配版。
整理当前版本已经包含的数据适配、可靠性修复、输出处理增强和局部 Prompt/流程调整，明确原始 ARK_V1 与适配版之间的差异。
核验当前实验入口中 Dataset Input、Graph Access、Agent Execution、Agent Tracing、Normalized Prediction、Ground Truth、Metric Calculation 和 Result Storage 之间的接口。
核验 Langfuse callback 实际保存的 Agent trace、节点或步骤状态、Token 用量和执行时间。
核验 GTSQA 与 GTSQA_UA 在 Langfuse 中的 input、expected output 和 metadata 映射，以及实际实验结果与本地样本选择的对应关系。
核验已实现的实体精确匹配、回答/拒答决策和图证据覆盖 evaluator，检查逐题评分、失败计数、评分完整性和汇总分母。
整理现有 GTSQA 与 GTSQA_UA 的实验结果；区分已完成运行、失败运行、仅配置未运行和运行后尚未核验的情况。
研究通过 Langfuse API 提取 observations、traces、experiment results、evaluator scores、Token 用量和执行时间的方法。
确定 Prompt 在代码和 Langfuse Prompt Management 之间的管理方式，并保证正式实验可以追踪实际使用的 Prompt 或 Prompt 版本。
明确原始 ARK_V1 与 GTSQA 适配版的版本及配置记录方式，并评估 Prompt 调整对旧数据集结果的影响。
深入核验 CR-LT-KGQA 的准确数据版本、两个子集、实际样本字段、KG triples 来源、Boolean ground truth、commonsense reasoning 设置和本地可用性。
核验 GTSQA_UA 当前事实删除方案的操作性定义、原始样本与变体关联、查询验证和数据污染控制，并判断是否需要扩展缺失类型或样本规模。
结合实际 pilot 样本，继续收敛最终需要保留的 Agent 能力和测试任务。
继续确定最终静态数据集 schema、answer_type 枚举和答案规范化规则。
结合实际数据字段和 Langfuse trace，研究 ARK_V1 的 retrieved entities、retrieved facts、used_triples、查询状态、失败状态和 recoverable retry 的记录方式。
明确开发样本与正式评测样本之间的隔离原则，避免在正式实验中将已经用于架构开发的题目解释为无偏测试结果；UA 配对变体应与原题保持相同划分。
控制论文范围，区分：必须完成的核心贡献；
条件允许时加入的扩展实验；
适合作为未来工作的设计。

4.3尚未开始或尚未形成完成证据

在已有分散检查基础上，形成覆盖全部 12 道开发题的统一、可复查的一致性与接口风险检查报告。
根据图完整性和 ARK_V1 接口风险最终冻结 12 题；如确需替换，应记录明确理由，避免根据 Agent 表现选择样本。
落实 12 道开发问题及其 UA 配对变体与正式 held-out evaluation questions 的隔离方案。
形成正式的 GTSQA/CR-LT-KGQA–ARK_V1 Compatibility and Adaptation Contract。
冻结适配版 ARK_V1 的具体代码提交、Prompt 和实验配置。
深入读取和核验 CR-LT-KGQA 的实际问题样本和数据文件。
确定 CR-LT-KGQA 应采用 given-evidence 输入，还是需要额外的图检索接口。
实现 CR-LT-KGQA 数据适配层。
实现 ARK_V1 对 CR-LT-KGQA 的最小适配。
形成配置明确、结果可复查的完整 GTSQA 12 题及 GTSQA_UA 24 项开发实验汇总；如已有对应运行，应优先核验并整理，避免不必要地重复执行。
在小型开发子集上完成适配版 ARK_V1 第一轮系统评测及错误分类。
确定最终正式实验数据组合和测试样本规模。
对第一版 Agent 开展系统化代码分析和错误分类，并区分实现缺陷、数据或输出问题与探索策略局限。
结合相关文献和 ARK_V1 的失败案例确定 ARK_V2 的最终架构。
实现 ARK_V2。
在 GTSQA、GTSQA_UA 和 CR-LT-KGQA 的小型子集上迭代测试 ARK_V2。
完善面向正式实验的 Evaluation Program，包括结果导出、版本追踪、重复运行和必要的汇总分析。
开展正式实验、重复运行和统计分析。
开展 Agent 版本之间的消融实验。
条件允许时，实现 ARK_V2 对 KQA Pro 的扩展支持。
正式撰写论文主体章节。

5. Open Questions

5.1尚未确定的问题

论文的主要贡献在 Agent 架构改进、可执行评测框架、KGQA 数据分析和小规模受控评测数据之间如何分配比重。
CR-LT-KGQA 的准确数据版本、两个子集、知识图谱结构、许可条件和本地可用性是什么。
CR-LT-KGQA 是否提供完整知识图谱、question-specific candidate graph，还是仅提供人工选择的相关 KG triples。
CR-LT-KGQA 是否应采用 given-evidence 输入，还是需要为其建立额外的图检索设置。
GTSQA 和 CR-LT-KGQA 是否能够进入同一个 Graph Access 接口，还是需要使用不同的数据适配层但共享相同日志和评价接口。
ARK_V1 当前依赖 property graph 的哪些具体功能，适配到未来 RDF/OWL 图还需要修改哪些组件。
当前 Agent 图访问继续使用数据集适配层和本地 MultiDiGraph；未来是否需要引入 RDF library/SPARQL 作为实际检索后端，以及该变化是否属于论文必要范围。
ARK v1.1 的论文名称如何与当前 ark_v1 代码标识对应，是否需要独立版本标识，以及哪个提交和配置构成正式基线。
如何在论文中分别呈现必要适配、可靠性修复、早期局部优化和 ARK_V2 的方法改进，避免将其混为同一类贡献。
哪些剩余接口需求必须在基线冻结前完成，哪些可以保留为已知局限或未来工作。
GTSQA_UA 当前采用 fact deletion；是否有必要扩展到 entity、relation 或 entity type 删除，以及新增类型是否服务于论文研究问题。
当前基于 Gold SPARQL 的 UA 验证是否充分覆盖所选自然语言问题的语义，是否需要少量人工复核或补充检查。
GTSQA_UA 已保存原始答案、删除事实和验证查询，并可关联原始 Gold evidence；后续是否需要额外的独立构造审计记录。
GTSQA_UA 应实现到什么规模，以及是否需要为不同缺失类型保持平衡。
正式评测应从 GTSQA 的哪些 split 或 test categories 中选择样本，以及如何与 12 道开发题保持隔离。
当前选择的 12 题来自 GTSQA test split。如果这些题用于反复开发 ARK_V2，如何避免正式实验中的 test leakage，并为最终评测保留独立的 held-out questions。
所选 12 题属于 unseen_graph_type。如果 Agent 架构开发直接针对这些结构进行调整，最终是否还能将其结果解释为 unseen graph structure generalization。
当前 graph_evidence_coverage 是否已足以支持核心实验，是否还需要 Answer–Retrieved Result Consistency 或移除、替换 KG 信息等干预实验。
是否需要实现统一 KG 工具封装层，还是只统一各 Agent 的日志输出。
是否加入 RAG 基线，以及如何保证 KG Agent 和 RAG 获得等价信息。
最终使用哪些模型、运行多少次、使用多少测试样本，以及如何控制调用成本。

Langfuse trace 中哪些字段可以直接作为运行证据，哪些字段需要转换为论文定义的统一日志结构。
Prompt 是否全部迁移到 Langfuse Prompt Management，还是继续在代码中保留默认版本并在实验记录中保存版本标识。
Langfuse 中的 evaluator 结果是否作为主要实验结果存储，还是同时导出到独立的本地结构化结果文件。
适配版 ARK_V1 在旧数据集上的表现是否受到 Prompt 和接口调整影响，以及如何在正式比较中区分版本变化与数据集差异。
正式实验需要多少随机种子和重复运行，才能在调用预算内合理描述性能波动。
如何统一各版本的 QID 补全、答案规范化、调用预算、重试预算和图访问条件，避免公共处理差异干扰版本比较。

5.2需要导师确认的问题

KIT 工作站的 Ollama Endpoint 是否能够远程使用。

Circular Factory Knowledge Graph 预计何时可以提供初步 schema、ontology 或最小样例。
是否可以在完整 Circular Factory Knowledge Graph 完成前提供不包含敏感内容的小型 RDF/OWL 示例，用于验证 Agent 接口兼容性。
未来 Circular Factory Knowledge Graph 与 GTSQA 在结构上的相似性具体体现在哪些方面，以及论文中应如何界定这种迁移关系。
CR-LT-KGQA 的推荐版本、两个子集的区别、获取方式和预期实验角色。
GTSQA、GTSQA_UA 和 CR-LT-KGQA 的小型开发子集是否需要由导师进一步确认。
是否必须加入 RAG 或其他额外基线。
正式实验可使用的 OpenRouter 额度、模型范围、预算和允许的调用规模。
当前包含必要适配、可靠性修复和局部优化的 ARK v1.1 应如何作为论文主基线呈现，以及早期改动需要提供何种程度的单独验证。

5.3需要文献或实验验证的问题

哪些指标能够可靠区分“答案正确”和“答案确实来自知识图谱”。
不要求标准推理路径时，是否仍能对多跳能力进行有效评价。
hop_count 能否从 Gold SPARQL、Logical Form 或查询结构中稳定推导。
不同 Agent 架构在统一日志接口下是否能够公平比较。
answer_type 的最终取值应包括哪些类型。
当前 Agent 已通过结构化最终答案生成 answer_payload；后续不同架构应如何保持相同的输出语义和可比较性。
后续版本的结构化答案节点采用确定性程序、LLM Structured Output，还是混合实现。
当前已实现实体 QID 规范化；URI、别名、日期、数值及其他集合答案如何进一步规范化。
hop_count 如何在不同数据集中统一定义。
当前 used_triples 提取是否足以支持证据分析，以及是否需要另行提取全部 retrieved_facts。
大规模实验中完整 result 是内嵌保存，还是通过 result_ref 单独保存。
数值、布尔、日期、聚合和比较答案如何评价 Graph Grounding。
Answer–Retrieved Result Consistency 是作为核心指标，还是只作为辅助诊断指标。
哪些指标因数据缺失需要设置降级方案。
GTSQA 的 answer subgraph 在多大程度上可以作为 Graph Grounding 的参考证据，而不会被错误解释为 Agent 必须遵循的唯一推理路径。
受控删除生成的 GTSQA_UA 是否会产生问题语义异常、替代解释仍然成立或答案泄漏等构造偏差。
ARK_V1 在 property graph 与 RDF/OWL 图上的性能差异有多少来自 Agent 架构，又有多少来自数据适配和查询接口。
CR-LT-KGQA 的最终表现应如何区分 KG evidence 使用、commonsense reasoning、模型参数知识和猜测。

ARK_V1 在更多 GTSQA 样本上能否稳定完成多跳搜索，而不是只在样本 13311 上成功。
不同模型或调用路径产生的 structured-output parsing failure、关系选择失败和重试行为应如何分类和量化。
Langfuse callback 是否能够完整观察 ARK_V1 的 LangGraph 节点、工具调用、Token 用量、执行时间和状态变化。
补充 incoming relations 并修复重试路由后，早期错误有多少得到解决，还有哪些错误来自搜索策略、约束处理、证据整合或提前终止。
重试修复与局部 Prompt 调整是否带来可测量的执行成功率、调用成本或答案准确率变化。
QID 补全减少了多少表示层面的评分失败，是否存在错误或歧义映射，以及比较不同 Agent 时应如何保持一致。
多锚点、多路径探索是否相对于 ARK_V1 的顺序式搜索带来可测量的准确率或效率收益，具体应参考哪些相关研究。
GTSQA_UA 上的拒答有多少来自有效识别知识不足，有多少与搜索失败、预算耗尽或模型提前停止有关。

5.4当前评测边界与已知局限

Answer Accuracy by Hop 测量的是按题目跳数分组的最终答案表现，不能证明 Agent 实际执行了标注数量的图跳数或正确的多跳推理路径。
Answer–Retrieved Result Consistency 只能检查最终答案是否与记录的检索实体一致，不能证明 Agent 在因果上依赖了这些实体，也不能证明相关关系充分支持答案。
Retrieved Fact Validity Rate 只能验证日志中规范化后的事实是否存在于目标 KG，不能验证这些事实是否与问题相关、是否足以推出答案，或 Agent 是否实际使用了这些事实。
当前不要求逐题人工标注 supporting_triples 或完整推理路径，因此 Graph Grounding 和 Multi-hop Reasoning 主要采用轻量代理指标，并辅以少量案例分析。GTSQA 已有的 Gold answer subgraph 可直接用于当前证据覆盖指标。
实体答案的 Grounding 比较相对容易；数值、布尔、日期、聚合和比较问题的 Grounding 规则尚未确定。

graph_evidence_coverage 测量当前所选证据对 Gold answer subgraph 的覆盖程度，不能单独证明答案由这些证据推导而来，也不能证明推理过程正确。
该指标以 Gold triples 为分母，不直接惩罚额外、无关的 triples；覆盖率高不等于证据选择精确或探索高效。
如果存在不同于 Gold answer subgraph 的有效证据路径，较低覆盖率不必然表示 Agent 没有充分证据。
当前 used_triples 来自最终保留的、已完成且有效的推理步骤，不覆盖所有检索结果、失败尝试或被重置的步骤。因此，该指标不能代替完整工具调用和探索历史分析。
图证据提取或评分缺失需与真实零覆盖区分；运行级指标必须结合评分完整性和执行状态解释。

GTSQA_UA 的正确性不仅取决于删除了某个目标事实，还取决于修改后图中相应查询不再产生答案。当前构造和加载验证会执行原始查询，检查原图答案与修改后空结果，而不只是检查某条 Gold edge 被删除。
上述验证依赖 Gold query 对自然语言问题的表达正确性，不能自动排除所有语义解释或标注偏差，仍可通过少量人工复核检查构造质量。
当前 UA 设置将受控证据删除造成的查询空结果标为不可回答。这是该数据构造的操作性定义，不意味着所有任务中的空集合答案都应被解释为无法回答。
refusal_decision_correct 只评价回答/拒答选择，不评价回答内容是否正确；可回答题上的错误答案可能具有正确的回答决策。
None 计为 abstained，字符串列表包括 [] 计为 answered；执行失败不应当作正常拒答。
termination_reason 可以辅助区分拒答的产生背景，但不能单独证明 Agent 正确识别了知识不足。

QID 补全依赖已保留证据中的名称匹配，只处理唯一匹配，不读取 Gold 来纠正答案；其效果属于输出处理的一部分，正式版本比较需保持规则一致。
适配版已包含双向查询、重试修复和 Prompt 调整，因此其结果不能直接标为未经修改的原始 ARK_V1 结果。
当前仍需评估 seed entities 直接使用、工具返回上限及截断记录等接口需求；未实现的需求应明确记录，不能隐含假定所有版本具有相同的输入与资源条件。

Circular Factory Knowledge Graph 尚未完成，因此论文当前最多能够验证架构和接口面向相似 RDF/OWL 图结构的可迁移性，不能直接证明 Agent 已经适用于最终 Circular Factory Knowledge Graph。
当前 12 道 GTSQA 候选题来自 test split。如果这些题用于 Agent 接口开发、失败分析和架构迭代，其结果只能作为 development/pilot evidence，不能直接作为无偏正式测试结果。
所选问题属于 unseen_graph_type，但如果其具体结构已经用于 ARK_V2 开发，就不能再将同一批问题上的表现解释为严格的 unseen graph structure generalization。
基于这 12 道题构造的 GTSQA_UA 变体同样属于开发数据；原始题与变体不是相互独立的全新测试问题。

早期在 GTSQA 样本 13311 上获得两次成功结果；此前会议还报告了约 6 题的探索性试跑，其中约 1 题答对。这些运行的设置与评测流程尚未统一，不能合并为正式准确率，也不能据此推断当前适配版在全部 12 道开发题或整个 GTSQA 上的表现。
当前已有多样本实验、实体答案评价、拒答评价和图证据覆盖评价实现，但整批实验的执行情况、评分完整性、配置追踪和结果提取仍需通过实际记录核验。
当前默认实验配置选择 3 道 GTSQA 题；24 项 UA 配置保留在注释中。配置存在或提交标题提到某一实验，不构成该实验已完成的证据。
Langfuse 可以保存运行 trace，但 trace 完整并不自动证明 Graph Grounding，也不能替代论文定义的规范化日志字段和评价指标。

6. Current Main Bottleneck

6.1当前最重要的卡点：

当前最重要的卡点已经不再是缺少 GTSQA Agent Input、Gold Evaluation Data、incoming relation 查询或基本实验入口，而是需要将现有适配、修复和评测实现收敛为边界明确、配置可追踪、结果可复查的基线，并基于实际实验识别修复后仍然存在的主要失败模式。

目前 ARK_V1 已能够载入 GTSQA question-specific graph，支持 incoming/outgoing 关系选择与检索，并已接入多样本 Langfuse 实验、实体精确匹配、拒答决策和图证据覆盖评价。当前应重点核验逐题运行、评分完整性、失败统计、trace、结果导出和版本记录，而不是继续将这些功能列为尚未实现。

GTSQA_UA 已保存第一版 12 对、24 项开发数据，并实现事实删除、查询验证、图重建和拒答评价。仍需整理构造与实验验证证据，明确其语义边界，并避免在缺少结果分析的情况下扩大数据规模或缺失类型。

GTSQA adapter、MultiDiGraph、双向查询和结构化 Entity List 答案已经实现，但 seed entities 直接使用、triple 返回上限或分页、截断状态记录等需求尚需评估。已有数据准备和 UA 构造程序覆盖部分一致性检查，仍需整理覆盖全部开发样本的检查结果及尚未覆盖的 seed、结构标注和接口风险。

当前版本已经包含必要适配以外的可靠性修复和局部行为调整。需要明确哪些改动属于建立有效基线，哪些属于早期优化，以及后续 ARK_V2 将针对哪些剩余机制性问题改进。

6.2为什么它会影响后续工作：

如果没有整理数据一致性检查的覆盖范围和结果，后续失败仍可能来自数据准备错误，而不是 Agent 本身。
如果没有固定 Agent 版本、Prompt、模型配置和资源预算，就难以区分不同运行结果来自代码变化、模型波动还是方法改进。
如果没有把 sample_id、Agent Input、Gold Data、运行输出和 evaluator 结果稳定关联，就无法保证 ARK_V1、ARK_V2 和 Evaluation Program 使用相同条件。
如果没有核验 answer_payload、predicted_answer、answer_status、execution_status 和 termination_reason 的实际含义，就可能混淆错误答案、正确拒答、搜索耗尽、解析失败和执行错误。
如果没有检查计划样本、执行完成样本和成功评分样本之间的差异，汇总结果可能遗漏失败或评分缺失。
如果不核验 Langfuse trace 的完整性及其结果提取方式，Token 用量、执行时间、Prompt 版本、Agent 节点状态和工具调用记录仍可能无法稳定进入实验分析。
如果不评估 triple 返回限制和截断记录，大型 question-specific graph 可能产生过长工具输出，影响成本、稳定性和不同 Agent 之间的比较公平性。
如果没有明确原始 ARK_V1 与适配版的版本和 Prompt 差异，就无法判断不同数据集或不同 Agent 版本之间的结果是否可直接比较。
如果没有冻结 ARK_V1 的适配与修复边界，持续针对开发题调整旧版会使基线不断变化，并模糊后续 ARK_V2 的比较对象。
如果把 graph_evidence_coverage 解释为完整推理正确性，或把 refusal decision 解释为答案正确性，会导致论文结论超出指标能够支持的范围。
如果不提前区分开发题和正式测试题，使用 test split 中的 12 题及其 UA 变体开发 ARK_V2 可能造成 test leakage，并削弱正式实验的可信度。
在整理现有端到端开发实验和失败模式前直接扩大 GTSQA_UA、CR-LT-KGQA 或 ARK_V2，会使多个尚未充分核验的接口同时变化，并增加重复实现风险。

6.3已经解决的卡点：

已经区分 Agent Capability、Test Task、Dataset Requirement、Ground Truth / Annotation、Logging Requirement、Evaluation Metric 和 Implementation Method，避免将不同评测层次混为一体。
已经区分数据集静态标准侧与 Agent 动态运行侧，并明确通过 id 与 sample_id 连接。
已经设计统一结构化答案接口，并在 ARK_V1 的 Entity List 输出及 evaluator 中实现自动比较所需的主要处理。
已经明确 answer_payload、predicted_answer 和 final_answer_text 的设计关系，以及 null 与空集合的语义差异。
已经通过最小运行日志设计建立不同 Agent 架构的共同评测输入要求，实际字段映射仍需核验。
已经明确每次工具调用独立记录、失败重试不覆盖旧记录，并且工具调用次数不能作为 hop_count。
已经明确不需要逐题人工标注完整推理链和 supporting_triples，显著降低数据构建工作量。
已经明确结构化答案本身不能证明 Graph Grounding，必须结合实际 KG 检索日志。
已经明确 Answer Accuracy by Hop、Answer–Retrieved Result Consistency 和 Retrieved Fact Validity Rate 的解释边界，避免将轻量代理指标解释为完整推理或因果证据。
已经实现基于现有 Gold answer subgraph 的 graph_evidence_coverage，为 GTSQA 证据分析提供可执行代理指标。
已经将统一 KG 工具封装层降为可选扩展，避免在当前阶段增加不必要的实现范围。
已经将 Problem Understanding 定位为少量案例分析，而不是增加一套高成本逐题人工标注。
已经形成候选 KGQA 数据集清单，不再从完全未知的数据源开始调研。
已经明确 GTSQA 和 CR-LT-KGQA 是当前核心数据集，GTSQA_UA 用于不可回答问题评测，KQA Pro 属于条件允许时的扩展，不再要求单一数据集覆盖全部能力。
已经从 GTSQA test 中初步选择 12 道覆盖 6 类四边图结构的问题。
已经成功提取 12 道候选问题对应的完整 question-specific graphs。
已经生成 12 道候选问题对应的 Agent Input 和 Gold Evaluation Data。
已经确认逐题加载和释放最多约 30,000 条边的图，比同时载入所有图更适合当前设备和执行流程。
已经实现基础 GTSQA triple adapter，并使用 MultiDiGraph 保留同一实体对之间的多种关系。
已经实现 ARK_V1 的 Entity List 结构化答案，并区分 None 与空集合。
已经实现 incoming/outgoing 查询、方向感知关系选择和保持原始事实方向的 triple 返回。
已经修正部分节点和关系候选索引问题，并加强 relation-selection Prompt。
已经修复部分 anchor/relation 重试、路由顺序和旧状态残留问题，并记录主要探索终止原因。
已经实现可选 QID 补全与确定性的 QID 答案规范化。
已经在样本 13311 上通过 OpenRouter 和 LiteLLM 两条调用路径获得正确的四跳 Entity List 答案，证明当前 GTSQA 接入能够支持至少一个完整开发案例。
已经接入 Langfuse callback、多样本顺序运行、数据准备、item-level evaluator 和 run-level evaluator。
已经实现执行失败与正常拒答的状态区分，以及计划样本和评分完整性统计。
已经构造并保存 GTSQA_UA 第一版 12 对、24 项开发数据，加入查询验证、图重建和回答/拒答决策评价。
已经明确 ARK_V1 的必要适配和公平比较原则，不再把持续改进旧版 Agent 作为新 Agent 的主要目标。
已经明确应先核验实验、日志和结果存储工作流，分析适配版 ARK_V1 的真实失败案例，再确定 ARK_V2。
已经明确 ARK_V2 应首先在 GTSQA、GTSQA_UA 和 CR-LT-KGQA 的小型子集上迭代测试，然后再运行完整实验。
已经将每题启动 sub-agent 的并行方案排除出当前论文主要范围。

7. Next Direction

下一步主要方向：
优先整理当前适配版 ARK_V1 的修改范围、版本边界和实验配置，核验已有 GTSQA 与 GTSQA_UA 数据及评测流程，形成可复查的逐题结果、汇总结果和失败分析。随后继续深入核验 CR-LT-KGQA，并结合真实失败案例和相关文献确定 ARK_V2 的功能与架构需求。当前重点是核验和分析已有实现，而不是重新实现 incoming 查询、基本 evaluator 或从零构造 GTSQA_UA。

建议按照以下顺序推进：
整理原始 ARK_V1 到当前适配版的主要改动，区分数据与图接口适配、可靠性修复、输出处理增强和探索行为调整。
明确论文中的 ARK v1.1 与代码 ark_v1 标识的对应关系，保存各版本实际使用的 Prompt 和实验配置。
核验 12 道 GTSQA 问题的 ID、问题文本、seed_entities、图结构标注和 Gold Answer。
通过稳定 id 检查 Agent Input、question-specific graph 和 Gold Evaluation Data 的对应关系。
整理已有数据准备、UA 构造与加载验证覆盖的检查项目，补充尚未覆盖的必要检查，避免重复建立已有验证逻辑。
检查每道题的 seed、gold answer 和 gold answer subgraph 是否存在于对应 candidate graph 中。
统计每道题的节点数、边数、关系类型数量、seed 邻居规模和潜在工具返回风险。
根据一致性检查和接口风险最终冻结 12 道开发问题；如需要替换，应记录数据或接口层面的理由，不能以提高 Agent 成绩为目的。
明确 12 道开发问题及其 GTSQA_UA 变体不得直接作为无偏正式 test results，并为最终实验保留独立的 held-out questions。
评估 seed entities 直接使用、triple 返回上限或分页、工具返回数量和截断状态记录的必要性，限定适配版冻结前的剩余修改范围。
明确适配版的代码提交、Prompt、模型配置、重试与探索预算、QID 补全和答案规范化规则。
必要时让适配版运行旧数据集，检查 Prompt 和接口调整的影响；是否开展及规模应由论文需要和预算决定。
核验 GTSQA 与 GTSQA_UA 的 Langfuse dataset item、input、expected output、metadata 和本地图加载关系。
核验 Langfuse callback 保存的 trace、节点状态、工具调用、Token 用量和执行时间。
核验实体精确匹配、拒答决策和图证据覆盖的逐题评分及汇总逻辑，明确执行失败、评分缺失和真实零分的区别。
整理包含 sample_id、answer_payload、predicted_answer、gold_answer 或 answerable、evaluator score、answer_status、execution_status、termination_reason、模型配置、版本标识、运行时间和 trace reference 的可复查结果；不同数据集保留其适用字段。
优先整理已有实验结果，仅对缺失或不可比较的部分补充运行，形成 GTSQA 12 题开发结果及汇总分析。
核验 GTSQA_UA 12 对、24 项的构造验证记录和配对关系，并整理或补充回答/拒答实验结果。
通过 Langfuse API 或本地结果接口提取实验输出、evaluator score、Token 用量、执行时间和关键 trace 数据。
记录多样本运行中的主要失败案例、循环、接口限制、关系选择错误、structured-output parsing failure、错误答案、错误拒答、预算耗尽和缺失日志字段。
区分修复前的实现问题与修复后仍然存在的探索、约束处理和证据整合问题，避免仅依据低准确率直接断言某个架构缺乏全部复杂图推理能力。
为后续正式实验规划随机种子、重复运行、模型配置和成本控制；将单次探索性结果与正式重复实验结果明确区分。
根据真实运行结果收敛 GTSQA/CR-LT-KGQA–ARK_V1 Compatibility and Adaptation Contract，明确哪些组件必须修改、哪些核心策略保持不变，以及哪些需求不属于基线适配范围。
深入读取 CR-LT-KGQA 的论文、仓库、两个子集和实际问题样本，确认其 KG triples、Boolean labels、commonsense reasoning 设置及预期 Agent 输入方式。
确定 CR-LT-KGQA 使用 given-evidence 输入还是需要额外图检索接口，并明确其与 GTSQA 主实验之间的角色差异。
实现并验证 ARK_V1 对 CR-LT-KGQA 的最小适配。
根据现有 GTSQA_UA 结果判断是否需要扩大规模或增加缺失类型，避免在当前 pilot 尚未分析清楚时直接扩展构造范围。
在小型开发子集上完成适配版 ARK_V1 第一轮系统评测，形成初始性能基准和错误分类。
检索并分析与 GTSQA、多锚点图探索和 KG Agent 工作流有关的研究，再将 ARK_V1 的真实局限转换为 ARK_V2 的功能与架构需求。
优先选择少数有明确失败证据、能够实验验证的问题作为 ARK_V2 的改进重点，避免以增加节点数量或重写全部组件代替方法设计。
在 GTSQA、GTSQA_UA 和 CR-LT-KGQA 的小型开发子集上迭代测试 ARK_V2，并避免在开发过程中直接依赖正式 held-out evaluation questions 反复调参。
ARK_V2 和实验管线稳定后，冻结正式实验配置并使用独立样本运行完整实验。
核心实验完成且时间、计算预算和实现成本允许时，再将 ARK_V2 扩展到 KQA Pro。
当前阶段不宜立即投入缺少失败分析支撑的大规模 ARK_V2 开发，也不应重新从零开始筛选或提取 GTSQA 数据。
当前最优先的交付物应是边界明确的适配版基线、可追踪的实验配置、经过核验的 GTSQA/GTSQA_UA 开发结果，以及能够支持 ARK_V2 设计的主要失败模式分析。
