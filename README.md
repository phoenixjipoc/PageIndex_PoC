# PageIndex PoC

使用 [VectifyAI/PageIndex](https://github.com/VectifyAI/PageIndex) 在本机完成的文档检索问答实验。
仓库保存原始 PDF、评估问题、复现脚本、索引树、逐题输出和实验记录。

## 实验结果

2026-10-27 完成全量运行 `20261027-164054`：

| 指标 | 结果 |
|---|---:|
| 文档 / 页数 | 78 份 PDF / 2,546 页 |
| 索引成功 / 问答完成 | 78/78 / 110/110 |
| 答案初评 | 107 完全正确 / 3 部分正确 / 0 错误 |
| 初评全对率 | 97.3% |
| 读齐全部必需来源 | 99/102 道可回答题 |
| 8 道不可回答题 | 8/8 初评正确 |
| 单题延迟中位数 / P95 | 13.383 / 26.128 秒 |
| 索引与问答墙钟时间 | 约 37.3 分钟，含恢复间隔 |
| 索引与问答 API 费用估算 | $9.755929，非实际账单 |

**评分来自实验完成后 Codex 会话对参考答案和 acceptance 标准的逐题审阅，尚非人工确认准确率或独立模型评审结果。**
另有 `CONS-16` 保留人工复核标记。未同步运行其他检索系统，不能据此判定跨系统优劣。

- [完整结果报告（GitHub 可读版）](docs/RESULTS.md)
- [逐题答案、来源覆盖和评分 CSV](outputs/benchmark/20261027-164054/question_results.csv)
- [逐文档索引结果 CSV](outputs/benchmark/20261027-164054/index_results.csv)
- [机器可读汇总](outputs/benchmark/20261027-164054/summary.json)
- [最终完整性核验](outputs/benchmark/20261027-164054/final_verification.json)
- [实验规程](outputs/benchmark/20261027-164054/EXPERIMENT_PROTOCOL.md)

## 固定配置

- PageIndex 0.2.10，官方源码固定于 [`e38b40e`](https://github.com/VectifyAI/PageIndex/tree/e38b40ebaeea26d2c7206b80ce7bc9bf2935cdec)。
- Windows / Python 3.11；索引 `gpt-6-luna`，问答 `gpt-6-sol`，两阶段 reasoning effort 均为 `medium`。
- 官方 Flash/full 和官方默认提示词；不添加自定义 instructions，不开启可选 citation prompt。
- 每道题访问全部 78 份文档，不提供正确来源或 doc_id，不共享会话历史；参考答案不进入生成请求。
- 文档按文件名顺序索引；问题以 seed 42 打乱，4 路独立会话并发。

## 数据和记录

| 目录或文件 | 用途 |
|---|---|
| `documents/S/` | 78 份原始公开 PDF，唯一的检索语料输入 |
| `documents/manifest_S.csv` | 原始来源 URL、文件大小与 SHA-256 |
| `questions/queries.json` | 110 道问题，不含参考答案 |
| `questions/standards.json` | 参考答案、acceptance 及必需来源，仅供生成后的评估 |
| `questions/questions_verified.csv` | 完整参考记录和原始审核备注 |
| `scripts/` | 环境准备、生成、审计、汇总及报告脚本 |
| `outputs/benchmark/20261027-164054/` | 本次全量实验的原始记录和最终结果 |
| `outputs/example/` | 三次早期示例，配置存在差异，以各次记录为准 |
| `requirements.lock.txt` / `pageindex_source.json` | 依赖版本与官方源码版本 |

全量结果中的 `index/` 保存索引树和模型用量；`questions/` 保存原始答案、工具轨迹和返回证据；
`evaluation/` 保存审阅依据、分数和理由。运行中两次记录器恢复的原因与快照见 `runner_revisions.json`。

原始实验文件保持冻结，部分包含运行机器的绝对路径；`docs/RESULTS.md` 仅将报告链接转换成仓库相对路径。
`copy_manifest.json` 和 `questions/verification_report.md` 是数据准备阶段记录，仍提到后来移除的
`approved_corrections.jsonl`；该文件不在当前数据集内，现行参考以 `standards.json` 和 verified CSV 为准。
PDF 与第三方文本的权利归各原作者，来源见文档清单。

## 复现

[环境安装与新实验操作](docs/REPRODUCING.md) · [全量实验说明](RUN_BENCHMARK.md) · [单文档示例](RUN_EXAMPLE.md)

`.venv/`、`.cache/`、`.pageindex/` 和下载的 `vendor/` 不纳入版本管理；索引树和所需运行证据已保存在输出目录。
凭证通过进程环境提供，不写入仓库。历史实验使用的容器配置读取方式是可选项，PageIndex 始终在本机运行。

原计划的额外 API 评分在执行前被自动审批拒绝，已改为本会话审阅。
原评分脚本和提示词保留为未执行的计划记录，未向该评分 API 发送这批评分材料。
