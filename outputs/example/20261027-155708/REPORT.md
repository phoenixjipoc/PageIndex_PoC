# PageIndex 本机示例结果

2026-10-27 · 单文档示例已成功完成，答案和页码引用均核对正确。

## 问题与回答

**文档：** CAJPA Sample Investment Management Request for Proposal，9 页。

**问题 INV-01：** 该 RFP 要求提交多少份 proposal？运行时使用题库原始英文问题，未改写。

**PageIndex 回答：** “Ten (10) copies of the proposal must be sent.” 引用 PDF 第 8 页。

**原文证据：** “Please send ten (10) copies of your proposal and correspondence to:”

在回答完成后读取评分标准，其要求为 Ten/10 copies。原文文本匹配及整页视觉核对均确认正确。
参考答案没有进入建索引或问答过程。

## 实际执行过程

1. 本机读取原始 PDF，用 Flash 建立包含 11 个节点的章节索引。
2. 模型调用 `get_document_structure` 查看章节结构。
3. 定位到 `VI. SELECTION PROCESS`，页码范围 8–9。
4. 模型调用 `get_page_content` 读取第 8–9 页原文。
5. 返回“10 份”，引用第 8 页。

本次主动添加了“先查结构，再读原文”的通用指令，以便在这份短 PDF 上展示树检索路径。

## 耗时与用量

| 阶段 | 耗时 | 模型调用次数 | 输入 tokens | 输出 tokens |
|---|---:|---:|---:|---:|
| 建索引 | 25.974 秒 | 8 | 5,158 | 1,156 |
| 检索与回答 | 17.274 秒 | 3 | 9,742 | 111 |
| 合计 | 43.411 秒（含阶段间开销） | 11 | 14,900 | 1,267 |

耗时不含安装和首次依赖导入。建索引是一次性成本；问答用量包含多轮工具调用上下文，
其中 5,399 个输入 tokens 为缓存读取。计费还涉及缓存写入，token 统计不是最终账单。

## 运行配置与验证

- Windows 本机 Python 3.11.15，独立 `.venv`。
- PageIndex 0.2.10，源代码 commit：`e38b40ebaeea26d2c7206b80ce7bc9bf2935cdec`。
- 建索引和问答均明确指定 `gpt-6-sol`；11 次模型响应均返回 `gpt-6-sol`。
- Flash 索引，summary concurrency=2，索引 reasoning=none；问答使用 Responses API，reasoning=low。
- 只读取既有 Sirchmunk 容器中的连接配置，PageIndex 未在容器中运行。
- 仅发送所选公开文件的文本和查询到 `api.openai.com`，密钥没有保存到项目。
- 该 PDF 与无需登录即可下载的 CAJPA 公开原件逐字节一致。
- 78 份 PDF、三份题库及文档清单，共 82 个核心输入文件的 SHA-256 均保持一致。

单独发现原 `copy_manifest.json` 还引用了当前已不存在的
`questions/approved_corrections.jsonl`；该辅助文件未被示例使用，没有恢复或修改它。

## 本次结果的范围

这是指定一份 PDF 的功能验证，证明本机能够完成建索引、查章节、读原文和带页码回答。
尚未测试从 78 份文档中自主选择来源，也未运行全部 110 道题。

## 查看详细记录

- [原始结果](<C:/Users/XUJI/OneDrive - Capco/Desktop/PageIndex_PoC/outputs/example/20261027-155708/result.json>)
- [章节索引](<C:/Users/XUJI/OneDrive - Capco/Desktop/PageIndex_PoC/outputs/example/20261027-155708/tree.json>)
- [工具调用与证据](<C:/Users/XUJI/OneDrive - Capco/Desktop/PageIndex_PoC/outputs/example/20261027-155708/tool_trace.json>)
- [核验记录](<C:/Users/XUJI/OneDrive - Capco/Desktop/PageIndex_PoC/outputs/example/20261027-155708/verification.json>)

![已核对的 PDF 第 8 页](<C:/Users/XUJI/OneDrive - Capco/Desktop/PageIndex_PoC/outputs/example/20261027-155708/evidence_page_8.png>)
