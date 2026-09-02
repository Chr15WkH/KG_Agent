# KG Agent Literature Research Prompt

请结合 KG_Agent 项目的项目指令、PROJECT_STATUS.md
以及当前对话中提供的研究问题，查找和分析与当前项目阶段
最相关的学术论文。

## 1. 确定本次检索范围

先判断当前问题属于以下哪个方向：

- KG Agent architecture
- KGQA evaluation
- Agent capability evaluation
- Multi-hop Reasoning
- Graph Grounding
- Refusal
- Robustness and Generalization
- Problem understanding
- Dataset or benchmark construction
- Structured logging
- Evaluation of intermediate reasoning steps

一次只确定一个主要检索方向，避免同时覆盖过多主题。

## 2. 查找候选论文

优先查找：

- 真实存在且有效的论文；
- 与当前研究问题直接相关的论文；
- 正式发表或可靠的预印本；
- 可以获得全文的论文；
- 方法、数据和评测描述较完整的论文；
- 能对当前评测框架、数据集、Agent 实现或实验设计
  提供具体帮助的论文。

首先给出 3～5 篇候选论文，并说明每篇为什么相关。

不要仅根据论文标题作出判断。
在能够获得全文时，应查看论文正文后再分析。

## 3. 深入分析最相关论文

针对最相关的一篇论文回答：

1. 论文解决了什么问题？
2. 使用了什么数据、知识图谱和方法？
3. 最关键的实验结果是什么？
4. 创新点具体位于哪个环节？
5. 还存在哪些未解决的问题或局限？

## 4. 与我的项目对照

结合我的研究目标、数据条件、Agent 架构、
评测需求和计算资源，判断：

- 哪些内容可以直接借鉴？
- 哪些内容需要修改后才能借鉴？
- 哪些内容不能直接照搬？
- 论文主要影响项目的哪个部分？
- 是否值得修改当前的评测框架、数据要求、
  Agent 架构或实验设计？

## 5. 最终输出

最后给出：

- 最值得记录的一条研究结论；
- 当前项目下一步最具体的一个行动；
- 哪些结论来自论文原文；
- 哪些结论属于针对当前项目的推断。
- 与我的项目对照