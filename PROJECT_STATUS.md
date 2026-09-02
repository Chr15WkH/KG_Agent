KG Agent Master Thesis Project Status

Last Updated: 2026-09-01

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
GTSQA 开发子集整理、ARK_V1 适配合同正式化、CR-LT-KGQA 深入核验，以及统一实验评测管线准备阶段。
项目已经完成初步课题定义、评测框架设计和少量优先候选 KGQA 数据集的深入分析，但尚未进入改进版 Agent 的正式实现。第三次导师会议形成了以 KQA Pro 小型 pilot 为起点的阶段性方案；导师随后根据未来 Circular Factory Knowledge Graph 的 RDF/OWL 形式和预期结构，进一步确认并调整了数据集与实施顺序。
当前重点不是从零开始筛选 GTSQA 样本，也不是立即开发复杂 Agent，而是将已经选出的 12 道 GTSQA 问题及其 question-specific graphs 整理为可运行的开发数据，包括 Agent Input、Graph Input 和 Gold Evaluation Data；将已经发现的 ARK_V1 图接口限制正式收敛为最小适配合同；进一步核验 CR-LT-KGQA 的实际文件、字段和任务设置；并建立可供 ARK_V1 与 ARK_V2 共用的端到端实验评测管线。
当前阶段的具体目标：
将 Agent Capability、Test Task、Dataset Requirement、Ground Truth、Logging Requirement、Evaluation Metric 和 Implementation Method 明确区分并建立对应关系。
确定硕士论文的最小可执行评测范围，避免同时实现过多能力、指标、数据集和 Agent 版本。
继续整理与当前实验直接相关的 GTSQA 数据和实际样本，并深入核验 CR-LT-KGQA，重点记录和判断：
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
数据集分析与评测设计相互迭代：通过 GTSQA 和 CR-LT-KGQA 的实际问题类型、标注、图结构和 KG 可访问性验证评测方案；参考 GrailQAbility 的受控不完整性构造方法设计 GTSQA_UA；再反向确定 ARK_V1 的最小适配需求和 ARK_V2 的具体功能需求。
当前实施顺序为：
1. Retrofit ARK_V1，使其能够处理 GTSQA 和 CR-LT-KGQA；
2. 参考 GrailQAbility，通过构造知识图谱不完整性创建 GTSQA_UA，其中 UA 表示 Unanswerable；
3. 实现包含 Agent Tracing 和必要评测指标的实验管线；
4. 对 ARK_V1 开展第一轮评测，以了解其性能和主要失败模式；
5. 设计 ARK_V2，并在 GTSQA、GTSQA_UA 和 CR-LT-KGQA 的小型子集上迭代测试；
6. 运行完整实验；
7. 条件允许时，将 ARK_V2 扩展到 KQA Pro。

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

4. Current Progress
4.1已完成
已完成第一次导师会议的校订转录和详细中英文总结。
已完成第二次导师会议内容整理，进一步明确当前下一步应聚焦 KGQA 数据集及其 Question Type。
已完成第三次导师会议的详细中英文对照总结，并整理了 KQA Pro、GrailQAbility 和 GTSQA 的阶段性分工、ARK v1.1 的最小适配原则以及先建立评测工作流再设计新 Agent 的执行思路。
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
已初步分析 ARK_V1 接入 GTSQA 的具体接口限制，包括多关系边可能被覆盖、缺少 incoming-edge 查询、triple 顺序不一致、每题重复生成 embedding、工具结果缺少分页或返回上限等问题。
已初步确定 ARK_V1 接入 GTSQA 的最小适配方向：建立明确的 GTSQA adapter 和内部 triple schema；保留同一节点对之间的多种关系；支持 incoming 和 outgoing 查询；为关系和 triple 返回增加分页或统一上限；直接使用 GTSQA 提供的 seed_entities；逐题载入并释放图；记录导入边数、节点数、工具返回数量和截断状态。
已初步分析 CR-LT-KGQA 的任务定位：其相关 KG triples 可能主要作为给定证据，Agent 仍需结合 commonsense knowledge 产生 Boolean 答案，因此它可能适合作为 KG-grounded commonsense reasoning 的补充实验。
已确定 ARK_V1 应作为第一轮实验基线，ARK_V2 应根据 ARK_V1 的真实失败案例独立设计。
此前已完成的 KQA Pro pilot、qualifier 和复杂答案类型分析仍可作为未来可选扩展和接口设计参考，但不再属于当前核心实施路线。

4.2正在进行
将已经完成的 GTSQA 初步分析正式整理为数据接口和实验设计要求，避免重复从零分析数据集。
从 GTSQA 无图数据中按已选 12 个 ID 提取并整理 Agent Input 和 Gold Evaluation Data，并通过 id 与已经提取的 question-specific graphs 连接。
检查 12 道候选题的 seed、gold answer 和 gold evidence 是否均能在对应 candidate graph 中稳定匹配，并计算每题必要的图规模和接口风险信息。
将已发现的 ARK_V1 图接口问题收敛为正式的 Compatibility and Adaptation Contract。
深入核验 CR-LT-KGQA 的准确数据版本、两个子集、实际样本字段、KG triples 来源、Boolean ground truth、commonsense reasoning 设置和本地可用性。
设计 GTSQA_UA 的构造原则，包括可删除的知识元素、不可回答标签、原始样本与修改样本的关联、答案验证以及数据污染控制。
设计统一实验管线，明确 Dataset Input、Graph Access、Agent Execution、Agent Tracing、Normalized Prediction、Ground Truth、Metric Calculation 和 Result Storage 之间的接口。
结合实际 pilot 样本，继续收敛最终需要保留的 Agent 能力和测试任务。
继续确定最终静态数据集 schema、answer_type 枚举和答案规范化规则。
结合实际数据字段，研究 ARK_V1 日志可获得性、retrieved entities、retrieved facts、查询状态和失败状态的记录方式。
明确开发样本与正式评测样本之间的隔离原则，避免在正式实验中将已经用于架构开发的题目解释为无偏测试结果。
控制论文范围，区分：必须完成的核心贡献；
条件允许时加入的扩展实验；
适合作为未来工作的设计。

4.3尚未开始
按 12 个已选 ID 生成正式的 GTSQA Agent Input 和 Gold Evaluation Data。
建立 12 题的 question、seed、candidate graph、gold answer 和 gold answer subgraph 一致性检查。
根据图完整性和 ARK_V1 接口风险最终冻结 12 题，或使用预先定义的替补题替换不合适样本。
明确 12 道开发问题与正式 held-out evaluation questions 的隔离规则。
形成 GTSQA/CR-LT-KGQA–ARK_V1 Compatibility and Adaptation Contract。
深入读取和核验 CR-LT-KGQA 的实际问题样本和数据文件。
确定 CR-LT-KGQA 应采用 given-evidence 输入，还是需要额外的图检索接口。
实现 GTSQA 和 CR-LT-KGQA 数据适配层。
实现 ARK_V1 对 GTSQA 和 CR-LT-KGQA 的最小适配。
构造第一版小规模 GTSQA_UA，并验证修改后问题相对于修改后知识图谱确实不可回答。
实现包含 Agent Tracing 和必要指标的第一版端到端 Evaluation Program。
在小型开发子集上运行 ARK_V1 第一轮评测。
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

5.2需要导师确认的问题
Exposé 是否已经完成最终签字和正式注册流程。
KIT 工作站的 Ollama Endpoint 是否能够远程使用。

Circular Factory Knowledge Graph 预计何时可以提供初步 schema、ontology 或最小样例。
是否可以在完整 Circular Factory Knowledge Graph 完成前提供不包含敏感内容的小型 RDF/OWL 示例，用于验证 Agent 接口兼容性。
未来 Circular Factory Knowledge Graph 与 GTSQA 在结构上的相似性具体体现在哪些方面，以及论文中应如何界定这种迁移关系。
CR-LT-KGQA 的推荐版本、两个子集的区别、获取方式和预期实验角色。
GTSQA、GTSQA_UA 和 CR-LT-KGQA 的小型开发子集是否需要由导师进一步确认。
是否必须加入 RAG 或其他额外基线。
导师何时提供 OpenRouter API Key，以及初步测试可使用的额度和模型范围。
正式实验预算、模型范围和允许的调用规模。

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

6. Current Main Bottleneck
6.1当前最重要的卡点：
当前最重要的卡点不是缺少 GTSQA 样本，而是尚未把已有的 12 题、对应 question-specific graphs、Gold Data 和已经识别的 ARK_V1 接口问题正式整合为一个可执行的数据合同与适配合同。同时，CR-LT-KGQA 目前只完成了任务定位层面的初步分析，尚未通过实际数据确认其输入方式和接入范围。
目前 12 道 GTSQA 问题和对应图已经选出并成功提取，但尚未形成正式分离的 Agent Input、Graph Input 和 Gold Evaluation Data，也尚未完成 question、seed、answer、gold evidence 和 candidate graph 的系统一致性验证。
ARK_V1 接入 GTSQA 的主要接口问题已经初步识别，包括多关系边表示、双向图访问、triple schema、embedding、分页和工具返回 Token 风险，但尚未将这些要求冻结为正式合同，也尚未通过实际 Agent 运行验证。

6.2为什么它会影响后续工作：
如果没有将 12 道问题的输入、图和 Gold Data 正式分离并通过稳定 id 连接，就无法形成可复现的开发数据，也无法保证 ARK_V1、ARK_V2 和 Evaluation Program 使用相同输入条件。
如果没有完成 seed、gold answer 和 gold evidence 在 candidate graph 中的一致性检查，后续失败可能来自数据准备错误，而不是 Agent 本身。
如果没有冻结 ARK_V1 的适配合同，就无法区分为了运行 GTSQA 所必需的基线兼容性修改和真正属于 ARK_V2 的架构改进。
如果 CR-LT-KGQA 的实际输入设置没有确认，就无法判断 ARK_V1 是否需要完整图访问、given-evidence 工具或独立的 commonsense reasoning 接口。
如果 ARK_V1 无法稳定提供结构化答案、检索实体、检索事实、查询输入、工具调用和执行状态，就无法接入统一评测流程，也难以公平比较 ARK_V1 与 ARK_V2。
如果不提前区分开发题和正式测试题，使用 test split 中的 12 题开发 ARK_V2 可能造成 test leakage，并削弱正式实验的可信度。
在完成数据合同、适配合同和开发样本隔离规则前，无法冻结日志接口、Evaluation Program、正式实验规模和模型调用成本。
如果现在直接设计 ARK_V2，后续可能因图接口、数据字段、不可回答样本或 CR-LT-KGQA 输入方式变化而重复修改架构。

6.3已经解决的卡点：
已经区分 Agent Capability、Test Task、Dataset Requirement、Ground Truth / Annotation、Logging Requirement、Evaluation Metric 和 Implementation Method，避免将不同评测层次混为一体。
已经区分数据集静态标准侧与 Agent 动态运行侧，并明确通过 id 与 sample_id 连接。
已经通过统一结构化答案节点解决不同 Agent 最终输出难以自动比较的问题。
已经明确 answer_payload、predicted_answer 和 final_answer_text 的生成顺序，以及 null 与空集合的语义差异。
已经通过最小运行日志解决不同 Agent 架构缺少统一评测输入的问题。
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
已经确认逐题加载和释放最多约 30,000 条边的图，比同时载入所有图更适合当前设备和执行流程。
已经初步识别 ARK_V1 接入 GTSQA 时需要解决的图表示、访问方向、数据顺序、embedding 和工具返回问题。
已经明确 ARK_V1 的最小适配和公平比较原则，不再把持续改进旧版 Agent 作为新 Agent 的主要目标。
已经明确应先完成实验、日志和结果存储工作流，运行 ARK_V1 并分析真实失败案例，再设计 ARK_V2。
已经明确 ARK_V2 应首先在 GTSQA、GTSQA_UA 和 CR-LT-KGQA 的小型子集上迭代测试，然后再运行完整实验。
已经将每题启动 sub-agent 的并行方案排除出当前论文主要范围。

7. Next Direction
下一步主要方向：
优先将已经选择的 12 道 GTSQA 问题、对应 question-specific graphs 和 Gold Data 整理为正式的开发数据合同；将已经识别的 ARK_V1 图接口问题收敛为适配合同；深入核验 CR-LT-KGQA 的实际数据和任务设置；建立包含 Agent Tracing 和必要指标的端到端评测工作流；并通过 ARK_V1 的实际失败案例确定 ARK_V2 的功能和架构需求。
建议按照以下顺序推进：
确认 12 道 GTSQA 问题的 ID、问题文本、seed_entities 和图结构标注。
按相同 ID 从 GTSQA 无图数据中提取 Agent Input 和 Gold Evaluation Data。
通过 id 连接 Agent Input、question-specific graphs 和 Gold Evaluation Data。
检查每道题的 seed、gold answer 和 gold answer subgraph 是否存在于对应 candidate graph 中。
统计每道题的节点数、边数、关系类型数量、seed 邻居规模和潜在的工具返回风险。
根据一致性检查和接口风险最终冻结 12 道开发问题，必要时使用预先定义的替补题替换。
明确 12 道开发问题不得直接作为无偏正式 test results，并为最终实验保留独立的 held-out questions。
检查 ARK_V1 当前的数据输入、图表示、图工具、搜索流程、答案生成和日志能力。
形成 GTSQA/CR-LT-KGQA–ARK_V1 Compatibility and Adaptation Contract，明确哪些组件必须修改、哪些核心策略保持不变，以及哪些需求不属于基线适配范围。
深入读取 CR-LT-KGQA 的论文、仓库、两个子集和实际问题样本，确认它提供的 KG triples、Boolean labels、commonsense reasoning 设置及预期 Agent 输入方式。
确定 CR-LT-KGQA 使用 given-evidence 输入还是需要额外图检索接口，并明确其与 GTSQA 主实验之间的角色差异。
实现并验证 ARK_V1 对 GTSQA 和 CR-LT-KGQA 的最小适配。
参考 GrailQAbility 设计 GTSQA_UA 构造方法，明确删除对象、不可回答标签、原始样本关联、验证方式和质量控制。
首先构造小规模 GTSQA_UA，并验证修改后问题相对于修改后知识图谱确实不可回答。
实现统一实验管线，串联 Dataset Input、Graph Access、Agent Execution、Agent Tracing、Structured Logging、Normalized Prediction、Ground Truth、Metric Calculation 和 Result Storage。
在小型开发子集上运行 ARK_V1 第一轮评测，记录主要失败案例、循环、接口限制、错误答案、错误拒答和缺失日志字段。
将这些真实局限转换为 ARK_V2 的功能与架构需求，再开始 ARK_V2 的设计和代码实现。
在 GTSQA、GTSQA_UA 和 CR-LT-KGQA 的小型开发子集上迭代测试 ARK_V2，并避免在开发过程中直接依赖正式 held-out evaluation questions 反复调参。
ARK_V2 和实验管线稳定后，冻结正式实验配置并使用独立样本运行完整实验。
核心实验完成且时间、计算预算和实现成本允许时，再将 ARK_V2 扩展到 KQA Pro。
当前阶段不宜立即投入大规模 ARK_V2 开发，也不应重新从零开始筛选 GTSQA 数据。
当前最优先的交付物应包括：一套由 Agent Input、Graph Input 和 Gold Evaluation Data 组成的 GTSQA 12 题开发数据合同；一份范围明确、能够指导基线实现并支持后续实验解释的 GTSQA/CR-LT-KGQA–ARK_V1 Compatibility and Adaptation Contract。
