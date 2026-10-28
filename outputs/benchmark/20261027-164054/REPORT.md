# PageIndex 全量实验结果

实验 `20261027-164054` · 2026-10-27 · 78 份 PDF / 2,546 页 / 110 道问题。

索引成功 **78/78**；获得完成回答 **110/110**。
本会话 AI 逐题对照参考答案的初评：完全正确 **107/110（97.3%）**，部分正确 **3**，错误或运行失败 **0**。
正确=1、部分正确=0.5、错误/失败=0 时，平均得分为 **0.986**。已完成评分 110/110。

**语义标签来自当前 Codex 会话逐题审阅，不是人工确认准确率，也不是独立评审模型实验。** 答案先冻结，再按原有 acceptance 标准计 1/0.5/0 分；没有额外评分 API 调用。本会话 AI 同时参与实验执行与评估，存在确认偏差，建议人工复核扣分项和有歧义的题目。

本次观察到的主要问题是遗漏：INV-19 漏掉组合层面的承诺金额汇总；XD-17 漏掉南卡 RSIC；XD-18 漏掉 Arizona PSPRS。后两题均没有成功读取被遗漏文件的原文。三项扣分已额外对照原 PDF 核实。CONS-16 的众数回答正确，但列举 COAERS 时没有提到例外路径，保留一项人工复核标记。

## 实验设置

- PageIndex 0.2.10；固定官方源码 commit e38b40ebaeea26d2c7206b80ce7bc9bf2935cdec。
- Windows 本机运行，gpt-6-luna 建索引、gpt-6-sol 检索回答，全部 medium。
- 官方 Flash/full、官方提示词；不添加自定义 instructions，不开启可选 citation prompt。
- 官方摘要并发上限 64、问答上限 10 轮；不覆盖 SDK 超时、重试、输出上限。
- 文档按文件名升序逐份索引；问题以种子 42 打乱，4 个独立会话并发。
- 每题面对整个已索引库，不给正确来源、不传 doc_id、不共享历史；参考答案仅在答案冻结后用于评分，不进入 PageIndex 的生成请求。
- 初始本地索引为空。服务端自然缓存不清空，缓存命中单独记录。

## 分组表现

| 问题范围 | 题数 | 完成回答 | 完全正确 | 部分正确 |
|---|---:|---:|---:|---:|
| 不可回答 | 8 | 8 | 8 | 0 |
| 多文档组合 | 10 | 10 | 8 | 2 |
| 单文档 | 92 | 92 | 91 | 1 |

| 原始题型 | 题数 | 完成回答 | 完全正确 | 部分正确 |
|---|---:|---:|---:|---:|
| broad | 10 | 10 | 8 | 2 |
| detail | 47 | 47 | 47 | 0 |
| medium | 17 | 17 | 16 | 1 |
| pair_a | 14 | 14 | 14 | 0 |
| pair_b | 14 | 14 | 14 | 0 |
| unanswerable | 8 | 8 | 8 | 0 |

14 组配对题中，两题均获完全正确评分的有 **14 组**。这是配对全对率，不等同于完整的语义一致性评审。

## 检索到原文的情况

在 102 道可回答题中，至少成功读到一个必需来源：**102**；读齐全部必需来源：**99**。
逐题必需来源召回率的宏平均为 **99.2%**。
统计依据是实际成功的 get_page_content 返回；仅浏览到文档名或读取章节摘要不算读到原文。它衡量文档覆盖，不能证明具体答案句子的证据充分性。

## 耗时与用量

| 阶段 | 墙钟秒数 | 模型响应数 | 输入 tokens | 输出 tokens | 估算美元 |
|---|---:|---:|---:|---:|---:|
| 建索引 | 1821.42 | 2072 | 2,240,986 | 568,067 | 0.538854 |
| 检索与回答 | 415.364 | 671 | 9,020,534 | 47,903 | 9.217075 |
| 额外评分 API（未执行） | — | 0 | 0 | 0 | 0.0 |

逐题延迟中位数 **13.383 秒**，P95 **26.128 秒**，包括失败题的实际耗时。问答有 4 路并发，不能用每题延迟之和代替墙钟时间。
从首次索引启动至全部答案结束，包含恢复间隔的墙钟时间为 **2236.862 秒**；运行时首次依赖导入不在该计时内。
索引和问答估算合计 **$9.755929**。额外评分 API 未执行，费用为 $0；当前 Codex 会话的审阅用量和费用不在该 API 成本统计内。
估算使用 2026-10-27 的公开 Standard token 单价及逐次缓存读写、长上下文规则：[GPT-6 Luna](https://developers.openai.com/api/docs/models/gpt-6-luna)、[GPT-6 Sol](https://developers.openai.com/api/docs/models/gpt-6-sol)。未计账户折扣、其他服务档位、地区附加费、税费及无 usage 返回的失败请求，不是实际账单。

## 运行异常和边界

- 初始进程在完成第 5 份索引后遇到 Windows 进度文件替换权限错误。已为记录文件增加短暂重试，从第 6 份续跑；前 5 份没有重新生成，原始脚本与修订快照均保留。模型、提示词、数据和评分规则没有因该修复改变。
- 进度汇总主线程存在重复获取非重入锁的问题。独立答题任务继续执行，进度通过逐题检查点另行监控；全部答案检查点完成后，用重入锁修复版恢复汇总，不重新调用模型。修复与恢复记录保存在 runner_revisions.json。
- 文档处理失败 0 份；问答运行失败 0 题。下列失败保留在总分母中。
- 所有已观测模型与请求配置核对结果：**True**。
- 索引结构共 2470 个节点，缺摘要 0 个，页码范围异常 0 个。这是结构完整性检查，不代表摘要语义均已人工验证。
- 82 个核心输入文件、110 份冻结答案和 96 个已安装官方 Python 源文件均通过哈希核验；恢复前后 486 份请求、响应及工具日志未改变，确认汇总恢复没有重复调用模型。
- 没有同步重跑 Sirchmunk 或向量 RAG，本报告不能用于断言跨系统优劣。
- 这是一次固定数据集运行，没有重复采样；延迟与缓存表现取决于本次 4 路并发及服务端缓存状态，不代表稳定生产 SLA。
- 本次评分按参考答案的事实与完整性要求进行，未另做全量逐条引用页码及额外陈述的独立核验。
- 官方默认没有强制结构化引用，答案可能使用普通文字引用；不能用空 citation 标签列表代表未引用。


## 优先复核项

| 题号 | 初评 | 简要原因 |
|---|---|---|
| CONS-16 | correct；边界待人工复核 | Correct modal five-year threshold and frequency distribution. COAERS alternative is not explained in the brief issuer list; review whether this optional elaboration needs a caveat. |
| INV-19 | partial | Per-fund requirements are correct, but the enumerated portfolio aggregates omit commitment amounts (item vi), required along with items vii-xi. |
| XD-17 | partial | Correct Illinois and NYC requirements and LAFPP exemption, but omits the operative South Carolina RSIC Iran provision. |
| XD-18 | partial | Correct three documents and purposes, but omits Arizona PSPRS and ILPA-recommended portfolio metrics. |

这里只列前 20 个优先复核项，全部逐题结果和理由均在明细文件中。

## 文件入口

- [逐题答案、来源覆盖和评分 CSV](<C:/Users/XUJI/OneDrive - Capco/Desktop/PageIndex_PoC/outputs/benchmark/20261027-164054/question_results.csv>)
- [逐文档索引结果 CSV](<C:/Users/XUJI/OneDrive - Capco/Desktop/PageIndex_PoC/outputs/benchmark/20261027-164054/index_results.csv>)
- [机器可读汇总](<C:/Users/XUJI/OneDrive - Capco/Desktop/PageIndex_PoC/outputs/benchmark/20261027-164054/summary.json>)
- [实验规程](<C:/Users/XUJI/OneDrive - Capco/Desktop/PageIndex_PoC/outputs/benchmark/20261027-164054/EXPERIMENT_PROTOCOL.md>)
- [冻结配置](<C:/Users/XUJI/OneDrive - Capco/Desktop/PageIndex_PoC/outputs/benchmark/20261027-164054/config.json>)
- [官方生成提示词](<C:/Users/XUJI/OneDrive - Capco/Desktop/PageIndex_PoC/outputs/benchmark/20261027-164054/official_chat_instructions.txt>)
- [实际评估方式及变更原因](<C:/Users/XUJI/OneDrive - Capco/Desktop/PageIndex_PoC/outputs/benchmark/20261027-164054/evaluation/review_method.json>)
- [最终完整性核验](<C:/Users/XUJI/OneDrive - Capco/Desktop/PageIndex_PoC/outputs/benchmark/20261027-164054/final_verification.json>)
- [原文重点复核记录](<C:/Users/XUJI/OneDrive - Capco/Desktop/PageIndex_PoC/outputs/benchmark/20261027-164054/evaluation/source_spot_checks.json>)
- [脚本修订记录](<C:/Users/XUJI/OneDrive - Capco/Desktop/PageIndex_PoC/outputs/benchmark/20261027-164054/runner_revisions.json>)

每题完整证据和工具轨迹位于 `questions/<题号>/`；评分输入及判定位于 `evaluation/<题号>/`。原评分 API 计划和提示词保留作审计记录，未执行；它们没有进入 PageIndex 的索引或问答请求。

自动审批拒绝了额外 API 评分，理由是将本地答案和评分标准发送至 api.openai.com 的授权不足。已改为当前会话中的 AI 逐题审阅，没有向该评分 API 发送这批材料。
