KG Agent Master Thesis Project Status

Last Updated: 2026-09-13

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
GTSQA 开发数据核验、ARK_V1 最小适配收敛、Langfuse 实验追踪接入、最小 evaluator 实现和端到端 pilot 验证阶段。
项目已经完成初步课题定义、评测框架设计、少量优先候选 KGQA 数据集的深入分析，以及第一阶段 GTSQA 数据和 ARK_V1 接入工作，但尚未进入改进版 Agent 的正式实现。第三次导师会议形成了以 KQA Pro 小型 pilot 为起点的阶段性方案；导师随后根据未来 Circular Factory Knowledge Graph 的 RDF/OWL 形式和预期结构，进一步确认并调整了数据集与实施顺序。第四次导师会议进一步将近期工作聚焦到 GTSQA pilot、ARK_V1、Langfuse tracing、自定义 evaluator 和实验结果提取组成的端到端工作流。
当前重点不是从零开始筛选或重新提取 GTSQA 样本，也不是立即开发复杂 Agent，而是核验已经生成的 12 道 GTSQA Agent Input、Gold Evaluation Data 和 question-specific graphs 之间的一致性；完成 ARK_V1 运行 GTSQA 所需的剩余最小适配；将 Langfuse 接入当前实验流程；实现最小答案规范化和自动 evaluator；并在小型开发子集上验证可复现的端到端实验管线。CR-LT-KGQA 深入核验和 GTSQA_UA 构造仍属于后续核心工作，但不应阻塞当前 GTSQA pilot。
当前阶段的具体目标：
将 Agent Capability、Test Task、Dataset Requirement、Ground Truth、Logging Requirement、Evaluation Metric 和 Implementation Method 明确区分并建立对应关系。
确定硕士论文的最小可执行评测范围，避免同时实现过多能力、指标、数据集和 Agent 版本。
继续核验与当前实验直接相关的 GTSQA 数据和实际样本，并深入核验 CR-LT-KGQA，重点记录和判断：
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
数据集分析与评测设计相互迭代：通过 GTSQA 和 CR-LT-KGQA 的实际问题类型、标注、图结构和 KG 可访问性验证评测方案；参考 GrailQAbility 的受控不完整性构造方法设计 GTSQA_UA；再反向确定 ARK_V1 的剩余最小适配需求和 ARK_V2 的具体功能需求。
当前实施顺序为：
1. 核验 GTSQA 12 题开发数据，并收敛 ARK_V1 对 GTSQA 的最小适配；
2. 建立 Langfuse Agent Tracing、最小 evaluator、结构化结果和结果提取流程；
3. 在小型 GTSQA 开发子集上运行 ARK_V1 pilot，识别真实失败模式和缺失字段；
4. 进一步核验 CR-LT-KGQA，并完成 ARK_V1 对 CR-LT-KGQA 所需的最小适配；
5. 参考 GrailQAbility，通过构造知识图谱不完整性创建 GTSQA_UA，其中 UA 表示 Unanswerable；
6. 对 ARK_V1 开展第一轮系统评测；
7. 根据 ARK_V1 的真实失败案例设计 ARK_V2，并在 GTSQA、GTSQA_UA 和 CR-LT-KGQA 的小型子集上迭代测试；
8. 运行完整实验；
9. 条件允许时，将 ARK_V2 扩展到 KQA Pro。

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
不要求数据集为每道问题人工标注完整的标准推理链或 supporting_triples。
Agent 不需要输出完整自然语言思维过程，但需要记录实际工具调用、查询输入、检索结果和执行状态。
数据集保存评测输入和标准信息，例如 question、gold_answer、answer_type、hop_count 和 answerable；运行日志保存 Agent 的实际执行结果，例如 predicted_answer、answer_status、execution_status 和 tool_calls。两侧通过数据集 id 与日志 sample_id 关联。
不同 Agent 架构应在自然语言回答生成前增加统一的结构化答案输出步骤，并提供：
answer_payload；
predicted_answer；
final_answer_text；
answer_status；
execution_status等指标。

统一结构化答案流程为：答案整合 → 结构化答案节点 → answer_payload → 答案规范化 → predicted_answer → final_answer_text。answer_payload 是 Agent 整合检索结果后认定的原始结构化答案；predicted_answer 是按照数据集答案类型和规范化规则转换后的评测答案。规范化只能统一表示形式，不能纠正 Agent 的错误答案。
结构化答案中，null 表示无法根据 KG 确定答案；[] 表示问题可回答，但正确结果是空集合。二者必须区分，以支持 Final Answer 和 Refusal 的确定性评价。
answer_status 与 execution_status 必须分开记录，避免把查询失败误判为正确拒答。
tool_calls 是调用记录列表，每次实际工具调用对应一个独立对象。多跳查询、失败重试和重新规划均新增记录，不覆盖之前的失败调用；工具调用次数不等于问题跳数。
Graph Grounding 的最低实现主要依赖：结构化最终答案；
Agent 实际获得的 KG 检索结果；
可访问的目标知识图谱。

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
ARK_V1 接入 GTSQA 的已知最小适配方向包括：统一 triple schema；保留同一实体对之间的多种关系；支持 incoming 和 outgoing 查询；限制或分页返回 triples；直接使用数据集提供的 seed entities；记录图规模、工具返回数量和截断状态。
ARK_V1 首先需要进行支持 GTSQA 和 CR-LT-KGQA 所必需的适配。适配范围应优先覆盖数据转换、图访问、查询接口、答案输出和 Agent Tracing，同时尽量保持 ARK_V1 原有的核心图探索和搜索策略，以使其能够作为清晰且可解释的基线。
一旦 ARK_V1 能够稳定运行所选数据集和开发子集，就不应继续无限扩大旧版 Agent 的修改范围，以保证 ARK_V1 与 ARK_V2 之间比较的公平性。
学生的新 Agent 应作为独立的新版本 ARK_V2 设计，而不是无限延续对 ARK_V1 的增量修改。ARK_V2 的具体架构仍保持开放，应根据 ARK_V1 在 GTSQA、GTSQA_UA 和 CR-LT-KGQA 上的真实失败案例确定。
在正式设计 ARK_V2 前，应先建立 Dataset Input、Graph Access、Agent Execution、Structured Logging、Normalized Prediction、Ground Truth、Metric Calculation 和 Result Storage 的端到端工作流。
ARK_V1 的第一轮评测用于建立初始性能基准、了解 Agent 的实际表现并识别主要失败模式，不应直接被解释为最终架构评测。
ARK_V2 开发阶段应优先在 GTSQA、GTSQA_UA 和 CR-LT-KGQA 的小型代表性子集上进行迭代测试。在 ARK_V2 设计稳定并完成小型子集测试后，再开展完整实验。
KQA Pro 属于可选扩展。只有在核心路线已经完成且时间、实现成本和计算预算允许时，才将 ARK_V2 扩展到 KQA Pro。此前对 KQA Pro 的 qualifier、属性读取、数值比较和 Boolean verification 等能力的分析仍可用于未来可选扩展以及复杂答案类型设计，但不再决定当前第一阶段的实施顺序。
对 CR-LT-KGQA 的初步理解是：它为每道问题提供相关 KG triples，并要求系统结合这些证据与 commonsense knowledge 产生 Boolean 答案，因此可能更适合作为 KG-grounded commonsense reasoning 的补充评测，而不是主要的图检索评测。该理解仍需通过数据文件、论文和实际样本进一步核验。
知识图谱中缺少事实但模型可通过预训练知识或常识回答时，应区分 Graph Answerability、External Knowledge Answer、Unsupported Hallucination 和 Correct Refusal。该区分具有研究价值，但是否进入正式大规模实验仍需通过少量样本验证并控制标注成本。
数据集中的问题应作为相互独立的 Agent runs 执行。第一版评测执行器优先采用简单可控的顺序执行；云端调用可在成本和速率限制可控时加入有限并发。为每个问题启动 sub-agent 会引入独立的 Multi-Agent Architecture 问题，当前不属于论文主要范围。
开发和调试阶段优先使用导师提供的 OpenRouter API Key 和低成本模型。最终模型组合仍不提前锁定；导师将继续确认是否可以远程开放工作站上的 Ollama 服务。

Langfuse 将作为当前实验的运行追踪和实验管理工具，用于保存 Agent trace、Token 用量、执行时间、Prompt 版本和 evaluator 结果。论文所需的规范化答案、状态字段和指标仍由项目自己的统一评测结构定义。
Langfuse 的使用减少了自行实现底层 tracing 的需要，但不能替代论文特定的答案规范化、Gold Answer 比较、执行状态判断和实验结果分析。
Langfuse 数据集中的每个数据项应至少包含 input、expected output 和 metadata。当前 GTSQA pilot 中，input 对应自然语言问题，expected output 对应 Gold Answer，question-specific graph 及相关标识可以作为 metadata 或通过稳定引用关联。
Langfuse evaluator 可以在单个数据项运行完成后执行，也可以在完整数据集实验结束后计算汇总结果。第一阶段应优先实现简单、可解释的 item-level evaluator，再扩展到总体指标。
Prompt Management 可用于保存和版本化实验 Prompt，使运行结果能够关联到明确的 Prompt 版本。是否将全部 Prompt 迁移到 Langfuse 仍可根据实现复杂度决定，但正式实验必须能够追踪实际使用的 Prompt 或版本标识。

4. Current Progress
4.1已完成
已完成第一次导师会议的校订转录和详细中英文总结。
已完成第二次导师会议内容整理，进一步明确当前下一步应聚焦 KGQA 数据集及其 Question Type。
已完成第三次导师会议的详细中英文对照总结，并整理了 KQA Pro、GrailQAbility 和 GTSQA 的阶段性分工、ARK v1.1 的最小适配原则以及先建立评测工作流再设计新 Agent 的执行思路。
已完成第四次导师会议的详细中英文对照总结，明确近期应围绕 GTSQA pilot、ARK_V1、Langfuse tracing、自定义 evaluator 和结果提取建立端到端实验流程。
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
已形成 Graph Grounding 的初步可执行方案：Answer–Retrieved Result Consistency；
条件允许时计算 Retrieved Fact Validity Rate。

已初步建立七个评测层次之间的关系，并分别澄清 Final Answer、Refusal、Multi-hop Reasoning 和 Graph Grounding 的数据需求、日志需求、指标及主要局限。
已明确 gold_answer、answerable 和 hop_count 属于数据集标准侧；predicted_answer、answer_status、execution_status 和 tool_calls 属于 Agent 运行侧。
已明确多跳问题的工具调用次数不等于 hop_count；当前 Multi-hop 指标主要反映按题目跳数分组的最终答案表现。

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
已加强 relation-selection Prompt：向模型提供当前 anchor 和可用 outgoing relations，要求模型返回一个准确的关系名称，并修正第一次 retry feedback 的触发条件。
已通过 OpenRouter 和 LiteLLM 两条调用路径对 GTSQA 四跳样本 13311 进行了初步运行，两次运行均得到正确的 Entity List 答案 “Alzheimer's disease (Q11081)”。
已保存样本 13311 的两份初步运行结果，用于检查 ARK_V1 的四跳搜索过程、Prompt 行为、结构化输出和失败重试。
已初步观察到 LiteLLM 运行中可能出现 structured-output parsing failure，但 Agent 在该次运行中能够重试并继续完成问题。该现象需要在后续实验中作为 execution error 或 recoverable retry 记录。
已初步分析 ARK_V1 接入 GTSQA 的具体接口限制，包括多关系边可能被覆盖、缺少 incoming-edge 查询、triple 顺序不一致、每题重复生成 embedding、工具结果缺少分页或返回上限等问题。
已初步确定 ARK_V1 接入 GTSQA 的最小适配方向：建立明确的 GTSQA adapter 和内部 triple schema；保留同一节点对之间的多种关系；支持 incoming 和 outgoing 查询；为关系和 triple 返回增加分页或统一上限；直接使用 GTSQA 提供的 seed_entities；逐题载入并释放图；记录导入边数、节点数、工具返回数量和截断状态。
已初步分析 CR-LT-KGQA 的任务定位：其相关 KG triples 可能主要作为给定证据，Agent 仍需结合 commonsense knowledge 产生 Boolean 答案，因此它可能适合作为 KG-grounded commonsense reasoning 的补充实验。
已确定 ARK_V1 应作为第一轮实验基线，ARK_V2 应根据 ARK_V1 的真实失败案例独立设计。
此前已完成的 KQA Pro pilot、qualifier 和复杂答案类型分析仍可作为未来可选扩展和接口设计参考，但不再属于当前核心实施路线。

4.2正在进行
核验已经生成的 12 条 GTSQA Agent Input、Gold Evaluation Data 和 question-specific graph 之间的 id、question、seed、gold answer 和 gold answer subgraph 一致性。
检查每道题必要的图规模、关系类型数量、seed 邻居规模和潜在工具返回风险信息，并根据一致性和接口风险最终冻结 12 道开发问题。
将已发现的 ARK_V1 图接口问题收敛为正式的 Compatibility and Adaptation Contract，明确已完成项、剩余必要适配以及不属于 ARK_V1 基线范围的功能。
完成 ARK_V1 对 GTSQA 的剩余最小适配，包括 incoming 查询、seed entities 的直接使用、triple 返回上限或分页，以及工具返回数量和截断状态记录。
将当前单题运行脚本整理为统一实验入口，并建立 Dataset Input、Graph Access、Agent Execution、Agent Tracing、Normalized Prediction、Ground Truth、Metric Calculation 和 Result Storage 之间的接口。
将 Langfuse callback 接入 ARK_V1，使每次实验能够保存完整 Agent trace、节点或步骤状态、Token 用量和执行时间。
将当前 GTSQA pilot 转换为 Langfuse 数据集结构，明确 input、expected output 和 metadata 的映射关系。
实现第一版 item-level evaluator，对结构化 Agent 输出执行答案规范化，并根据 answer_type 与 Gold Answer 比较。
研究通过 Langfuse API 提取 observations、traces、experiment results、evaluator scores、Token 用量和执行时间的方法。
确定 Prompt 在代码和 Langfuse Prompt Management 之间的管理方式，并保证正式实验可以追踪实际使用的 Prompt 或 Prompt 版本。
深入核验 CR-LT-KGQA 的准确数据版本、两个子集、实际样本字段、KG triples 来源、Boolean ground truth、commonsense reasoning 设置和本地可用性。
设计 GTSQA_UA 的构造原则，包括可删除的知识元素、不可回答标签、原始样本与修改样本的关联、答案验证以及数据污染控制。
结合实际 pilot 样本，继续收敛最终需要保留的 Agent 能力和测试任务。
继续确定最终静态数据集 schema、answer_type 枚举和答案规范化规则。
结合实际数据字段和 Langfuse trace，研究 ARK_V1 的 retrieved entities、retrieved facts、查询状态、失败状态和 recoverable retry 的记录方式。
明确开发样本与正式评测样本之间的隔离原则，避免在正式实验中将已经用于架构开发的题目解释为无偏测试结果。
控制论文范围，区分：必须完成的核心贡献；
条件允许时加入的扩展实验；
适合作为未来工作的设计。

4.3尚未开始
建立覆盖全部 12 道开发题的自动一致性检查，并输出可复查的检查结果。
根据图完整性和 ARK_V1 接口风险最终冻结 12 题，或使用预先定义的替补题替换不合适样本。
明确 12 道开发问题与正式 held-out evaluation questions 的隔离规则。
形成正式的 GTSQA/CR-LT-KGQA–ARK_V1 Compatibility and Adaptation Contract。
深入读取和核验 CR-LT-KGQA 的实际问题样本和数据文件。
确定 CR-LT-KGQA 应采用 given-evidence 输入，还是需要额外的图检索接口。
实现 CR-LT-KGQA 数据适配层。
实现 ARK_V1 对 CR-LT-KGQA 的最小适配。
完成包含 Langfuse Agent Tracing、答案规范化、必要指标和结构化结果存储的第一版端到端 Evaluation Program。
在多个 GTSQA 开发样本上运行 ARK_V1 第一轮 pilot，并自动生成逐题 evaluator 结果和汇总结果。
构造第一版小规模 GTSQA_UA，并验证修改后问题相对于修改后知识图谱确实不可回答。
在小型开发子集上运行 ARK_V1 第一轮系统评测。
确定最终正式实验数据组合和测试样本规模。
对第一版 Agent 开展系统化代码分析和错误分类。
确定 ARK_V2 的最终架构。
实现 ARK_V2。
在 GTSQA、GTSQA_UA 和 CR-LT-KGQA 的小型子集上迭代测试 ARK_V2。
实现正式全量 Evaluation Program。
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
ARK_V1 当前依赖 property graph 的哪些具体功能，适配到 GTSQA 和未来 RDF/OWL 图需要修改哪些组件。
当前实验中的 Graph Access 应直接采用 RDF library/SPARQL，还是继续使用经过语义保持的数据集适配层和本地图结构。
ARK_V1 的适配版本是否仍命名为 ARK v1.1，还是保留 ARK_V1 名称并将数据适配层独立版本化。
GTSQA_UA 应删除 entity、relation、entity type、fact，还是采用多种受控不完整性操作。
如何自动或半自动验证 GTSQA_UA 中的问题相对于修改后的知识图谱确实不可回答。
GTSQA_UA 是否应保留原 answer subgraph 和被删除的关键证据，以支持构造验证、Refusal 评价和后续分析。
GTSQA_UA 应实现到什么规模，以及是否需要为不同缺失类型保持平衡。
正式评测应从 GTSQA 的哪些 split 或 test categories 中选择样本，以及如何与 12 道开发题保持隔离。
当前选择的 12 题来自 GTSQA test split。如果这些题用于反复开发 ARK_V2，如何避免正式实验中的 test leakage，并为最终评测保留独立的 held-out questions。
所选 12 题属于 unseen_graph_type。如果 Agent 架构开发直接针对这些结构进行调整，最终是否还能将其结果解释为 unseen graph structure generalization。
Graph Grounding 是否只使用 Answer–Retrieved Result Consistency，还是还需要加入干预实验，例如移除或替换 KG 信息。
是否需要实现统一 KG 工具封装层，还是只统一各 Agent 的日志输出。
是否加入 RAG 基线，以及如何保证 KG Agent 和 RAG 获得等价信息。
最终使用哪些模型、运行多少次、使用多少测试样本，以及如何控制调用成本。

Langfuse trace 中哪些字段可以直接作为运行证据，哪些字段需要转换为论文定义的统一日志结构。
Prompt 是否全部迁移到 Langfuse Prompt Management，还是继续在代码中保留默认版本并在实验记录中保存版本标识。
Langfuse 中的 evaluator 结果是否作为主要实验结果存储，还是同时导出到独立的本地结构化结果文件。

5.2需要导师确认的问题
Exposé 是否已经完成最终签字和正式注册流程。
KIT 工作站的 Ollama Endpoint 是否能够远程使用。

Circular Factory Knowledge Graph 预计何时可以提供初步 schema、ontology 或最小样例。
是否可以在完整 Circular Factory Knowledge Graph 完成前提供不包含敏感内容的小型 RDF/OWL 示例，用于验证 Agent 接口兼容性。
未来 Circular Factory Knowledge Graph 与 GTSQA 在结构上的相似性具体体现在哪些方面，以及论文中应如何界定这种迁移关系。
CR-LT-KGQA 的推荐版本、两个子集的区别、获取方式和预期实验角色。
GTSQA、GTSQA_UA 和 CR-LT-KGQA 的小型开发子集是否需要由导师进一步确认。
是否必须加入 RAG 或其他额外基线。
正式实验可使用的 OpenRouter 额度、模型范围、预算和允许的调用规模。

5.3需要文献或实验验证的问题
哪些指标能够可靠区分“答案正确”和“答案确实来自知识图谱”。
不要求标准推理路径时，是否仍能对多跳能力进行有效评价。
hop_count 能否从 Gold SPARQL、Logical Form 或查询结构中稳定推导。
不同 Agent 架构在统一日志接口下是否能够公平比较。
answer_type 的最终取值应包括哪些类型。
answer_payload 在第一版 Agent 中由哪个上游状态生成。
结构化答案节点采用确定性程序、LLM Structured Output，还是混合实现。
URI、实体 ID、别名、日期、数值和集合答案如何规范化。
hop_count 如何在不同数据集中统一定义。
第一版 Agent 是否能够可靠提取 retrieved_facts。
大规模实验中完整 result 是内嵌保存，还是通过 result_ref 单独保存。
数值、布尔、日期、聚合和比较答案如何评价 Graph Grounding。
Answer–Retrieved Result Consistency 是作为核心指标，还是只作为辅助诊断指标。
哪些指标因数据缺失需要设置降级方案。
GTSQA 的 answer subgraph 在多大程度上可以作为 Graph Grounding 的参考证据，而不会被错误解释为 Agent 必须遵循的唯一推理路径。
受控删除生成的 GTSQA_UA 是否会产生问题语义异常、替代路径仍然存在或答案泄漏等构造偏差。
ARK_V1 在 property graph 与 RDF/OWL 图上的性能差异有多少来自 Agent 架构，又有多少来自数据适配和查询接口。
CR-LT-KGQA 的最终表现应如何区分 KG evidence 使用、commonsense reasoning、模型参数知识和猜测。

ARK_V1 在更多 GTSQA 样本上能否稳定完成多跳搜索，而不是只在样本 13311 上成功。
不同模型或调用路径产生的 structured-output parsing failure、关系选择失败和重试行为应如何分类和量化。
Langfuse callback 是否能够完整观察 ARK_V1 的 LangGraph 节点、工具调用、Token 用量、执行时间和状态变化。

5.4当前评测边界与已知局限
Answer Accuracy by Hop 测量的是按题目跳数分组的最终答案表现，不能证明 Agent 实际执行了标注数量的图跳数或正确的多跳推理路径。
Answer–Retrieved Result Consistency 只能检查最终答案是否与记录的检索实体一致，不能证明 Agent 在因果上依赖了这些实体，也不能证明相关关系充分支持答案。
Retrieved Fact Validity Rate 只能验证日志中规范化后的事实是否存在于目标 KG，不能验证这些事实是否与问题相关、是否足以推出答案，或 Agent 是否实际使用了这些事实。
当前不要求逐题人工标注 supporting_triples 或完整推理路径，因此 Graph Grounding 和 Multi-hop Reasoning 主要采用轻量代理指标，并辅以少量案例分析。
实体答案的 Grounding 比较相对容易；数值、布尔、日期、聚合和比较问题的 Grounding 规则尚未确定。
GTSQA_UA 的正确性不仅取决于删除了某个目标事实，还取决于修改后的知识图谱中不存在其他能够得到同一答案的路径。因此，自动构造结果可能需要额外验证或抽样人工检查。
Circular Factory Knowledge Graph 尚未完成，因此论文当前最多能够验证架构和接口面向相似 RDF/OWL 图结构的可迁移性，不能直接证明 Agent 已经适用于最终 Circular Factory Knowledge Graph。
当前 12 道 GTSQA 候选题来自 test split。如果这些题用于 Agent 接口开发、失败分析和架构迭代，其结果只能作为 development/pilot evidence，不能直接作为无偏正式测试结果。
所选问题属于 unseen_graph_type，但如果其具体结构已经用于 ARK_V2 开发，就不能再将同一批问题上的表现解释为严格的 unseen graph structure generalization。

当前仅在 GTSQA 样本 13311 上获得两次成功结果，不能据此推断 ARK_V1 已经稳定适配全部 12 道开发题或全部 GTSQA。
当前保存的运行结果主要用于开发诊断，尚未通过统一 evaluator、固定实验配置和自动结果存储形成正式可比较的实验结果。
Langfuse 可以保存运行 trace，但 trace 完整并不自动证明 Graph Grounding，也不能替代论文定义的规范化日志字段和评价指标。

6. Current Main Bottleneck
6.1当前最重要的卡点：
当前最重要的卡点已经不再是缺少 GTSQA Agent Input 或 Gold Evaluation Data，而是尚未把已经生成的 GTSQA 开发数据、ARK_V1 单题运行能力、结构化答案、Langfuse tracing、自动 evaluator 和结果存储整合为一条可复现、可自动评分和可扩展的端到端实验管线。
目前 ARK_V1 已经能够载入 GTSQA question-specific graph，并在样本 13311 的两次初步运行中得到正确答案。但是，当前结果主要保存为文本日志，尚未自动关联 sample_id 与 Gold Data，尚未输出统一的 predicted_answer、answer_status、execution_status 和 evaluator score，也尚未通过 Langfuse 保存和提取完整实验 trace。
GTSQA adapter、MultiDiGraph 和结构化 Entity List 答案已经完成第一阶段实现，但 incoming 查询、seed entities 直接使用、triple 返回上限或分页、截断状态记录等适配仍未完成。12 道开发题的 question、seed、gold answer、gold evidence 和 candidate graph 也尚未通过统一程序完成系统一致性验证。

6.2为什么它会影响后续工作：
如果没有完成 12 道问题的数据一致性检查，后续失败仍可能来自数据准备错误，而不是 Agent 本身。
如果没有把 sample_id、Agent Input、Gold Data、运行输出和 evaluator 结果自动关联，就无法形成可复现的开发实验，也无法保证 ARK_V1、ARK_V2 和 Evaluation Program 使用相同条件。
如果没有结构化的 predicted_answer、answer_status 和 execution_status，就无法区分错误答案、正确拒答、查询失败、解析失败和可恢复重试。
如果没有实现最小 evaluator，目前保存的正确答案只能通过人工阅读日志确认，无法扩展到多个样本和重复运行。
如果没有接入 Langfuse 或等价 tracing，Token 用量、执行时间、Prompt 版本、Agent 节点状态和完整 trace 无法稳定进入实验分析。
如果没有完成 triple 返回限制和截断记录，大型 question-specific graph 可能产生过长工具输出，影响成本、稳定性和不同 Agent 之间的比较公平性。
如果没有冻结 ARK_V1 的最小适配边界，就无法区分为了运行 GTSQA 所必需的基线兼容性修改和真正属于 ARK_V2 的架构改进。
如果不提前区分开发题和正式测试题，使用 test split 中的 12 题开发 ARK_V2 可能造成 test leakage，并削弱正式实验的可信度。
在完成最小端到端 pilot 前直接扩大 GTSQA_UA、CR-LT-KGQA 或 ARK_V2，会使多个尚未验证的接口同时变化，并增加重复实现风险。

6.3已经解决的卡点：
已经区分 Agent Capability、Test Task、Dataset Requirement、Ground Truth / Annotation、Logging Requirement、Evaluation Metric 和 Implementation Method，避免将不同评测层次混为一体。
已经区分数据集静态标准侧与 Agent 动态运行侧，并明确通过 id 与 sample_id 连接。
已经通过统一结构化答案节点解决不同 Agent 最终输出难以自动比较的问题。
已经明确 answer_payload、predicted_answer 和 final_answer_text 的生成顺序，以及 null 与空集合的语义差异。
已经通过最小运行日志设计解决不同 Agent 架构缺少统一评测输入定义的问题。
已经明确每次工具调用独立记录、失败重试不覆盖旧记录，并且工具调用次数不能作为 hop_count。
已经明确不需要逐题人工标注完整推理链和 supporting_triples，显著降低数据构建工作量。
已经明确结构化答案本身不能证明 Graph Grounding，必须结合实际 KG 检索日志。
已经明确 Answer Accuracy by Hop、Answer–Retrieved Result Consistency 和 Retrieved Fact Validity Rate 的解释边界，避免将轻量代理指标解释为完整推理或因果证据。
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
已经修正部分节点和关系候选索引问题，并加强 relation-selection Prompt。
已经在样本 13311 上通过 OpenRouter 和 LiteLLM 两条调用路径获得正确的四跳 Entity List 答案，证明当前 GTSQA 接入能够支持至少一个完整开发案例。
已经明确 ARK_V1 的最小适配和公平比较原则，不再把持续改进旧版 Agent 作为新 Agent 的主要目标。
已经明确应先完成实验、日志和结果存储工作流，运行 ARK_V1 并分析真实失败案例，再设计 ARK_V2。
已经明确 ARK_V2 应首先在 GTSQA、GTSQA_UA 和 CR-LT-KGQA 的小型子集上迭代测试，然后再运行完整实验。
已经将每题启动 sub-agent 的并行方案排除出当前论文主要范围。

7. Next Direction
下一步主要方向：
优先核验已经生成的 GTSQA 12 题开发数据，完成 ARK_V1 对 GTSQA 的剩余最小适配，并将当前单题运行能力扩展为包含 Langfuse Agent Tracing、结构化结果、答案规范化、最小 evaluator 和结果提取的端到端实验管线。在该流程通过少量 GTSQA 开发样本验证后，再继续深入核验 CR-LT-KGQA、构造 GTSQA_UA，并通过 ARK_V1 的真实失败案例确定 ARK_V2 的功能和架构需求。
建议按照以下顺序推进：
核验 12 道 GTSQA 问题的 ID、问题文本、seed_entities、图结构标注和 Gold Answer。
通过稳定 id 检查 Agent Input、question-specific graph 和 Gold Evaluation Data 的对应关系。
检查每道题的 seed、gold answer 和 gold answer subgraph 是否存在于对应 candidate graph 中。
统计每道题的节点数、边数、关系类型数量、seed 邻居规模和潜在工具返回风险。
根据一致性检查和接口风险最终冻结 12 道开发问题，必要时使用预先定义的替补题替换。
明确 12 道开发问题不得直接作为无偏正式 test results，并为最终实验保留独立的 held-out questions。
完成 ARK_V1 对 GTSQA 的剩余必要适配，包括 incoming 查询、seed entities 直接使用、triple 返回上限或分页、工具返回数量和截断状态记录。
将当前 OpenRouter 和 LiteLLM 单题脚本整理为统一的实验运行入口。
为 GTSQA pilot 定义 Langfuse dataset item，将 question 作为 input、Gold Answer 作为 expected output，并通过 metadata 或稳定引用关联 question-specific graph 和样本信息。
将 Langfuse callback 接入 ARK_V1，确认完整 trace、节点状态、Token 用量和执行时间能够被保存。
实现 Entity List 的第一版答案规范化和精确集合匹配 evaluator。
输出包含 sample_id、predicted_answer、gold_answer、correct、answer_status、execution_status、模型配置、Prompt 版本或标识、运行时间和 trace reference 的结构化结果。
首先在样本 13311 上完成可重复的端到端验证，再扩展到少量其他 GTSQA 开发题。
通过 Langfuse API 或本地结果接口提取实验输出、evaluator score、Token 用量、执行时间和关键 trace 数据。
记录多样本运行中的主要失败案例、循环、接口限制、关系选择错误、structured-output parsing failure、错误答案、错误拒答和缺失日志字段。
根据真实运行结果收敛 GTSQA/CR-LT-KGQA–ARK_V1 Compatibility and Adaptation Contract，明确哪些组件必须修改、哪些核心策略保持不变，以及哪些需求不属于基线适配范围。
深入读取 CR-LT-KGQA 的论文、仓库、两个子集和实际问题样本，确认其 KG triples、Boolean labels、commonsense reasoning 设置及预期 Agent 输入方式。
确定 CR-LT-KGQA 使用 given-evidence 输入还是需要额外图检索接口，并明确其与 GTSQA 主实验之间的角色差异。
实现并验证 ARK_V1 对 CR-LT-KGQA 的最小适配。
参考 GrailQAbility 设计 GTSQA_UA 构造方法，明确删除对象、不可回答标签、原始样本关联、验证方式和质量控制。
首先构造小规模 GTSQA_UA，并验证修改后问题相对于修改后知识图谱确实不可回答。
在小型开发子集上运行 ARK_V1 第一轮系统评测，形成初始性能基准和错误分类。
将 ARK_V1 的真实局限转换为 ARK_V2 的功能与架构需求，再开始 ARK_V2 的设计和代码实现。
在 GTSQA、GTSQA_UA 和 CR-LT-KGQA 的小型开发子集上迭代测试 ARK_V2，并避免在开发过程中直接依赖正式 held-out evaluation questions 反复调参。
ARK_V2 和实验管线稳定后，冻结正式实验配置并使用独立样本运行完整实验。
核心实验完成且时间、计算预算和实现成本允许时，再将 ARK_V2 扩展到 KQA Pro。
当前阶段不宜立即投入大规模 ARK_V2 开发，也不应重新从零开始筛选或提取 GTSQA 数据。
当前最优先的交付物应是一条能够在 GTSQA 样本上完成 Dataset Input、Graph Access、ARK_V1 Execution、Langfuse Tracing、Structured Answer、Normalized Prediction、Gold Comparison、Metric Calculation 和 Result Storage 的最小端到端实验管线。该管线至少应先在样本 13311 上稳定复现，再扩展到其余开发样本。
