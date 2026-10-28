# 官方默认提示词重跑结果

2026-10-27 · Illinois FPIF 33 页 PDF · INV-04 · 成功。

已从运行脚本中删除自定义提示词和对应开关。此次建索引和问答均使用固定版本
PageIndex 0.2.10 的官方实现及内置提示词。

## 本次配置

| 项目 | 实际设置 |
|---|---|
| 索引模型 | 官方 Quickstart 的 gpt-6-luna |
| 问答模型 | 官方 Quickstart 的 gpt-6-sol |
| 两阶段 reasoning | 按用户要求显式设置 medium |
| 索引模式与优化 | 官方默认 Flash、full |
| 摘要并发上限 | 官方默认 64 |
| 问答轮次上限 | 官方默认 10 |
| 自定义 instructions | 没有传入；代码已移除 |
| 可选 citation prompt | 官方默认关闭 |
| 超时、重试、输出 token 上限 | 不再由脚本覆盖，交由 SDK 默认处理 |

为了支持 medium 下的工具调用，问答显式选择官方支持的 Responses API。
连接沿用既有授权配置，索引存入新的本地目录。模型、medium、API 协议、连接和存储位置是
明确指定的运行配置；未声称所有参数都与官方 Quickstart 的最短代码完全相同。

## 答案和证据

问题询问 FPIF 的私募市场长期配置及资产类别划分。模型回答：

- 私募市场合计：**31%**。
- 私募股权：**10%**。
- 私募债权：**7%**。
- 房地产：**10%**。
- 基础设施：**4%**。

模型自行调用 `get_document_structure`，然后通过 `get_page_content` 读取第 3–4 页。
最终以普通文字注明：Section 1.2、纸面第 1 页（PDF 第 3 页）。
答案和页码均与原文及评分标准一致。评分标准仅在回答完成后用于核验。

此次没有开启可选引用提示词，因此没有 `<cite>` 标签，`get_citations()` 返回空列表；
这不代表没有来源说明，实际回答包含正确的文字引用，原文见 `result.json`。

## 耗时与用量

| 阶段 | 耗时 | 模型响应次数 | 输入 tokens | 输出 tokens |
|---|---:|---:|---:|---:|
| 建索引 | 17.072 秒 | 17 | 22,809 | 4,418 |
| 检索与回答 | 9.058 秒 | 3 | 15,253 | 175 |
| 合计 | 26.184 秒 | 20 | 38,062 | 4,593 |

总计 42,655 tokens，输出中包含 912 个 reasoning tokens。所有请求均显式发送 medium；
问答响应的 reasoning token 计数为 0，不代表该请求参数未生效。
输入缓存命中分别为索引 14,825、问答 7,410 tokens。
耗时不包含依赖导入。这是一次运行观测，不能把耗时变化单独归因于提示词。

## 核验

- 17 个索引响应均返回 gpt-6-luna，3 个问答响应均返回 gpt-6-sol，共 20 个唯一响应。
- 20 个实际 HTTP 请求均为 medium，模型配置全部匹配。
- 每个问答请求的完整 `instructions` 均与官方 `CHAT_HEADER + AGENT_INSTRUCTIONS`
  完全相同；原始官方文本已保存供检查。
- 安装目录的 96 个 Python 源文件与固定官方源码逐字节相同。
- 官方源码 commit：`e38b40ebaeea26d2c7206b80ce7bc9bf2935cdec`。
- 78 份 PDF、题库及清单共 82 个核心输入文件的哈希保持一致。
- 公开 PDF 的来源核验及此前视觉核验的同一原始页面一并保存。

本次仍是指定单份文档的功能示例，未执行整个语料库的 110 题评测。

## 查看记录

- [官方提示词原文](<C:/Users/XUJI/OneDrive - Capco/Desktop/PageIndex_PoC/outputs/example/20261027-163520/official_chat_instructions.txt>)
- [完整回答及运行结果](<C:/Users/XUJI/OneDrive - Capco/Desktop/PageIndex_PoC/outputs/example/20261027-163520/result.json>)
- [实际请求参数及提示词一致性](<C:/Users/XUJI/OneDrive - Capco/Desktop/PageIndex_PoC/outputs/example/20261027-163520/wire_requests.jsonl>)
- [工具调用过程](<C:/Users/XUJI/OneDrive - Capco/Desktop/PageIndex_PoC/outputs/example/20261027-163520/tool_trace.json>)
- [核验记录](<C:/Users/XUJI/OneDrive - Capco/Desktop/PageIndex_PoC/outputs/example/20261027-163520/verification.json>)
- [本次运行脚本快照](<C:/Users/XUJI/OneDrive - Capco/Desktop/PageIndex_PoC/outputs/example/20261027-163520/runner_snapshot.py>)

![PDF 第 3 页，纸面第 1 页](<C:/Users/XUJI/OneDrive - Capco/Desktop/PageIndex_PoC/outputs/example/20261027-163520/evidence_page_3.png>)
