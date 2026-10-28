# 全量 PageIndex 实验

当前实验目录：`outputs/benchmark/20261027-164054/`。
冻结配置见该目录的 `config.json` 和 `EXPERIMENT_PROTOCOL.md`；实时状态见 `status.json`。

本机运行 78 份 PDF、110 道问题。使用官方源码、官方默认提示词，索引模型 gpt-6-luna、
问答模型 gpt-6-sol，两者 medium。每题可访问整个已索引文档库，不预先提供正确来源。

## 运行或续跑

```powershell
.\.venv\Scripts\python.exe scripts/run_benchmark.py --run-dir outputs/benchmark/20261027-164054 --credentials-container sirchmunk
```

同一命令会跳过已完成及已记录失败的检查点，继续未完成项。正在运行时不要再启动第二个实例。
失败会原样计入实验结果，不自动改参数或反复答题挑选最好结果。代码如需修复，必须保存修订快照及原因。

`--credentials-container` 仅读取既有容器配置，PageIndex 本身在本机运行。
也可以在进程环境中设置 `OPENAI_API_KEY`、`OPENAI_BASE_URL` 后省略该参数。

## 本次结果与评估

78 份文档和 110 道问题已全部完成。最终报告见当前实验目录的 `REPORT.md`。

答案生成完毕后已冻结 SHA256。本次由当前 Codex 会话逐题对照参考答案及 acceptance 标准，
按正确 1 / 部分正确 0.5 / 错误 0 记录分数和理由。评估方式见 `evaluation/review_method.json`，
判定见 `evaluation/<题号>/judgment.json`，不属于人工确认准确率或独立评审模型实验。

自动审批拒绝了原计划的额外 API 评分，因为向 api.openai.com 发送本地答案及评分标准的授权不足。
`evaluate_benchmark.py` 和原评分提示词仅保留为未执行的计划记录；本次没有额外评分 API 调用。

重新生成离线报告和完整性核验（不调用模型）：

```powershell
.\.venv\Scripts\python.exe scripts/audit_benchmark_results.py --run-dir outputs/benchmark/20261027-164054
.\.venv\Scripts\python.exe scripts/report_benchmark.py --run-dir outputs/benchmark/20261027-164054
```

生成阶段仅使用问题文本和 PDF 文档，评分标准不进入 PageIndex 的索引、检索或回答请求。

## 主要产物

- `config.json`、`inputs/`：运行配置、输入清单、查询顺序、代码和依赖快照。
- `environment.json`、`official_chat_instructions.txt`：运行环境及实际官方提示词。
- `index/<文件标识>/`：每份 PDF 的索引树、结果、请求设置与模型用量。
- `questions/<题号>/`：每题答案、耗时、工具调用、返回证据、请求设置及模型用量。
- `runner_revisions.json`：运行中仅为恢复执行而做的脚本修订及原因。
- `generation_manifest.json`：评分开始前冻结的全部答案 SHA256。
- `evaluation/`：本会话审阅依据、判定、理由、原文重点复核记录及未执行的 API 评分计划。
- `summary.json`、`question_results.csv`、`index_results.csv`：汇总及逐项结果。
- `REPORT.md`：最终实验报告。

API Key、鉴权头和模型私有推理内容不会写入记录。token 统计包含失败前已经返回的响应，
成本使用已保存的公开单价估算，实际账单可能不同。
