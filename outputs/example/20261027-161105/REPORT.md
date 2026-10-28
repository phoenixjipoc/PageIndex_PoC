# PageIndex 第二个本机示例

2026-10-27 · Illinois FPIF，33 页 · INV-04 · 答案和原文引用核验通过。

本次按照固定版本官方 Quickstart 的模型分工运行：`gpt-6-luna` 建索引，
`gpt-6-sol` 检索回答；两个阶段均明确设置 `medium`。
使用官方默认的 Flash 索引和 agent 提示词，没有加入首个示例的“先查结构”指令。

## 问题与结果

**题目：** Illinois Firefighters' Pension Investment Fund 在 2023 年 2 月的
Private Markets RFP 中，私募市场长期目标配置是多少，如何分配到各资产类别？
实际调用使用 `queries.json` 中 INV-04 的原始英文问题。

**PageIndex 回答：** 私募市场长期目标合计 **31%**，其中私募股权 **10%**、
私募债权 **7%**、房地产 **10%**、基础设施 **4%**。

引用 PDF **第 3 页**，对应纸面页码 **1**、章节 **1.2 Background on this RFP**。
回答完成后，核对了评分标准、PDF 提取文本和完整页面图片，五项比例均正确。
参考答案及评分标准没有进入索引或问答过程。

## 模型配置与实际请求

| 阶段 | 模型 | Thinking | 成功调用 | 耗时 |
|---|---|---|---:|---:|
| 索引、章节摘要及文档描述 | gpt-6-luna | medium | 17 | 52.922 秒 |
| 检索、读页、生成答案 | gpt-6-sol | medium | 5 | 14.062 秒 |
| 合计 | — | — | 22 | 67.032 秒 |

22 个实际 HTTP 请求与 22 个唯一响应一一对应，全部请求的模型及 reasoning 参数符合配置，
全部响应返回的模型名称也符合预期。索引请求使用 Chat Completions 的
`reasoning_effort: medium`；问答使用 Responses API 的 `reasoning.effort: medium`。
这项核验覆盖发出前已序列化的请求体，不只是 Python 配置值。

耗时包含索引及问答阶段间少量开销，不包含 Python 依赖导入，也不包含下文说明的中断尝试。

## 实际检索路径

本机生成了 **18 个节点**的章节树，其中 **10 个为顶层节点**。
模型自主调用：

1. `browse_documents`：查看当前可用文档。
2. `get_document`：查看这份 RFP 的文档信息。
3. `get_document_structure`：读取章节树，定位 `1. Introduction`（PDF 第 3–5 页）。
4. `get_page_content`：读取 PDF 第 3–4 页。
5. 给出配置比例，并引用第 3 页。

## Token 用量

| 阶段 | 输入 tokens | 输出 tokens | 其中 reasoning tokens | 总 tokens |
|---|---:|---:|---:|---:|
| 索引 | 22,724 | 4,956 | 1,528 | 27,680 |
| 问答 | 20,925 | 278 | 74 | 21,203 |
| 合计 | 43,649 | 5,234 | 1,602 | 48,883 |

Reasoning tokens 已包含在输出 tokens 中。输入统计包含多轮上下文和缓存；
缓存读取分别为索引 1,486、问答 12,401 tokens，详细缓存写入统计见原始结果。
Token 数量不是美元账单。

## 环境与复现

- Windows 本机 Python 3.11.15；PageIndex 0.2.10。
- 固定官方源码 commit：`e38b40ebaeea26d2c7206b80ce7bc9bf2935cdec`。
- Flash 默认完整优化，摘要并发为 2；问答最多 8 轮，每请求超时 90 秒。
- 凭证沿用已授权的 Sirchmunk 配置，只读旧容器；PageIndex 在本机执行。
- 所选 PDF 与 [FPIF 公开原件](https://ifpif.org/wp-content/uploads/2023/02/Private-Markets-RFP-2023.02.13.pdf) 逐字节一致；请求发往 `api.openai.com`。
- 78 份 PDF 与题库、清单共 82 个核心输入文件的哈希保持一致。

复现命令见 [RUN_EXAMPLE.md](<C:/Users/XUJI/OneDrive - Capco/Desktop/PageIndex_PoC/RUN_EXAMPLE.md>)。
索引保存在 `.pageindex/example-20261027-161105/`，后续可以复用。

**中断尝试说明：** `20261027-160959` 首次尝试中，新增的记录脚本把 LiteLLM 的
`openai/gpt-6-luna` 前缀误判成模型不一致，造成重试。已中止、修正并完整重跑。
这不是模型服务或 PageIndex 的失败。该尝试的日志保留在原目录；已完成响应也有 API 用量，
未计入本报告成功运行的耗时及 token 表。详细记录见
[中断尝试](<C:/Users/XUJI/OneDrive - Capco/Desktop/PageIndex_PoC/outputs/example/20261027-160959/result.json>)。

本次是指定单份文档的功能示例。尚未验证从 78 份 PDF 中自动选择来源，也不是 110 题的完整评测；
文档长度与首个示例不同，两次耗时不能用于直接比较模型性能。

## 详细记录

- [原始回答、配置与用量](<C:/Users/XUJI/OneDrive - Capco/Desktop/PageIndex_PoC/outputs/example/20261027-161105/result.json>)
- [章节树](<C:/Users/XUJI/OneDrive - Capco/Desktop/PageIndex_PoC/outputs/example/20261027-161105/tree.json>)
- [工具调用与原文证据](<C:/Users/XUJI/OneDrive - Capco/Desktop/PageIndex_PoC/outputs/example/20261027-161105/tool_trace.json>)
- [实际请求参数](<C:/Users/XUJI/OneDrive - Capco/Desktop/PageIndex_PoC/outputs/example/20261027-161105/wire_requests.jsonl>)
- [实际响应模型与逐次用量](<C:/Users/XUJI/OneDrive - Capco/Desktop/PageIndex_PoC/outputs/example/20261027-161105/model_calls.jsonl>)
- [核验结果](<C:/Users/XUJI/OneDrive - Capco/Desktop/PageIndex_PoC/outputs/example/20261027-161105/verification.json>)

![PDF 第 3 页，纸面页码 1](<C:/Users/XUJI/OneDrive - Capco/Desktop/PageIndex_PoC/outputs/example/20261027-161105/evidence_page_3.png>)
