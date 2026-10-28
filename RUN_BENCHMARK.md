# Full-corpus PageIndex experiment

Completed run: `outputs/benchmark/20261027-164054/`.
Its `config.json` and `EXPERIMENT_PROTOCOL.md` describe the frozen configuration and procedure; `status.json` records generation status.

The local run covers 78 PDFs and 110 questions using official source and default prompts.
Indexing uses `gpt-6-luna`; answering uses `gpt-6-sol`; both use `medium` reasoning effort.
Every question can access the full indexed corpus without a supplied correct source.

## Run or resume

For a fresh checkout or a new experiment, follow [the reproduction guide](docs/REPRODUCING.md) and choose a new run directory.
The historical resume command below applies only to the original machine with its matching local index store:

```powershell
.\.venv\Scripts\python.exe scripts/run_benchmark.py --run-dir outputs/benchmark/20261027-164054 --credentials-container sirchmunk
```

The command skips completed and recorded-failed checkpoints and continues unfinished items. Do not start a second instance while a run is active.
Failures remain in the results; the runner does not silently change parameters or repeatedly answer a question to select the best output.
Any operational repair must retain a script snapshot and a reason.

`--credentials-container` only reads an existing container configuration; PageIndex runs in the local process.
Alternatively, set `OPENAI_API_KEY` and `OPENAI_BASE_URL` in the process environment and omit this option.

## Results and assessment

All 78 documents and 110 questions completed. Read the [full report](docs/RESULTS.md).

Answer SHA-256 hashes were frozen after generation. Each answer was then reviewed in the Codex conversation against its reference answer and acceptance criteria:
correct = 1, partial = 0.5, incorrect = 0. The method is recorded in `evaluation/review_method.json` and individual judgments in `evaluation/<question-id>/judgment.json`.
These labels are not human-verified accuracy or independent model-judge results.

Automatic approval review rejected the planned additional API grading run because authorization to send the local answers and scoring references to `api.openai.com` was insufficient.
`evaluate_benchmark.py` and its original prompt are retained as an unexecuted plan. No additional grading API calls were made.

Rebuild the offline report and integrity checks without calling a model:

```powershell
.\.venv\Scripts\python.exe scripts/audit_benchmark_results.py --run-dir outputs/benchmark/20261027-164054
.\.venv\Scripts\python.exe scripts/report_benchmark.py --run-dir outputs/benchmark/20261027-164054
```

These commands rewrite derived files and verification timestamps. To preserve archived bytes, read the existing outputs or work in a separate checkout.
Generation uses only question text and PDF documents; scoring references never enter PageIndex indexing, retrieval, or answering requests.

## Artifacts

- `config.json`, `inputs/`: configuration, input manifests, query order, code, and dependency snapshots.
- `environment.json`, `official_chat_instructions.txt`: runtime environment and exact official prompts.
- `index/<file-id>/`: each PDF's index tree, result, request settings, and model usage.
- `questions/<question-id>/`: answer, timing, tool calls, returned evidence, request settings, and usage.
- `runner_revisions.json`: operational script repairs and their reasons.
- `generation_manifest.json`: answer SHA-256 hashes frozen before assessment.
- `evaluation/`: review inputs, judgments, reasons, source spot checks, and the unexecuted API grading plan.
- `summary.json`, `question_results.csv`, `index_results.csv`: summary and item-level results.
- `REPORT.md`: final experiment report, now available in English.

API keys, authorization headers, and private model reasoning are excluded from logs.
Token accounting includes responses completed before a failure. Costs use saved public rates and are estimates rather than invoices.
The [translation manifest](docs/translation_manifest.json) records the documentation-only language update.
