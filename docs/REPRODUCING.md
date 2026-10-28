# 复现实验

本次验证环境为 Windows、Python 3.11、PageIndex 0.2.10。已有结果可直接阅读，无需凭证或安装依赖。
完整重新生成会调用模型 API；结果、耗时与服务端缓存可能随运行变化。

## 安装

在仓库根目录的 PowerShell 中执行。以下命令使用已安装的 `uv`：

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe scripts/fetch_pageindex.py
uv pip install --python .venv/Scripts/python.exe -r requirements.lock.txt
uv pip install --python .venv/Scripts/python.exe --no-deps ./vendor/PageIndex
.\.venv\Scripts\python.exe -c "from pageindex import PageIndexClient; import importlib.metadata; print(importlib.metadata.version('pageindex'))"
```

`requirements.lock.txt` 锁定第三方依赖，PageIndex 本体从固定 commit 的源码单独安装。
fetch 脚本不会覆盖已有 `vendor/PageIndex`。源码版本和下载归档哈希见 [pageindex_source.json](../pageindex_source.json)。

通过本机的凭证管理方式为当前进程提供 `OPENAI_API_KEY`，按需要提供 `OPENAI_BASE_URL`；默认接口为
`https://api.openai.com/v1`。没有配置文件或 Key 需要提交到仓库。当前运行器的模型名是
`gpt-6-luna` / `gpt-6-sol`，所选接口需要支持这两个模型及 medium reasoning。

## 新的全量运行

使用新的输出目录，不要用已归档实验目录启动新实验：

```powershell
.\.venv\Scripts\python.exe scripts/run_benchmark.py --prepare --run-dir outputs/benchmark/reproduction-01
.\.venv\Scripts\python.exe scripts/run_benchmark.py --run-dir outputs/benchmark/reproduction-01
```

第一步冻结文档、问题、配置和脚本快照，不调用模型；第二步建索引并回答全部问题。
同一目录的续跑跳过已有完成或失败检查点。需要保留新运行的本地 `.pageindex/` 才能从其索引续跑。
发布的仓库不包含该可重建缓存；其中的索引树和检索证据保存在 `outputs/`。

旧环境的 `--credentials-container sirchmunk` 选项只用于读取已有连接配置；新环境使用进程变量即可，
不需要 Docker。

## 查看和核验现有结果

安装固定源码后，可以离线核验原始文档、答案哈希、实际模型和提示词记录：

```powershell
.\.venv\Scripts\python.exe scripts/audit_benchmark_results.py --run-dir outputs/benchmark/20261027-164054
```

该命令不调用模型，但会更新 `final_verification.json` 的检查时间。需要保留归档文件原样时，直接阅读
[已有核验记录](../outputs/benchmark/20261027-164054/final_verification.json)。

报告汇总脚本只读取已保存的输出与判定，不会替新实验自动产生语义评分。
本次 110 题采用本会话 AI 参考答案审阅；方法、限制和原文重点复核见
[review_method.json](../outputs/benchmark/20261027-164054/evaluation/review_method.json)。
`evaluate_benchmark.py` 是未执行的额外 API 评分方案，不属于本次已完成的流程。

## 冻结记录

原实验目录中的脚本快照、配置、答案和评估记录均按运行时状态保存。
历史绝对路径用于溯源；新实验会根据当前仓库路径生成自己的配置。
新运行如修改模型、提示词、并发或数据，需要使用新的 run ID 并记录差异。
