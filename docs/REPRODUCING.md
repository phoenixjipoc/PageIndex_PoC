# Reproducing the experiment

The validated environment was Windows, Python 3.11, and PageIndex 0.2.10. Existing results can be read without credentials or installed dependencies.
A full rerun calls the model API; outputs, latency, and server-side cache behavior may vary.

## Installation

Run these commands in PowerShell from the repository root. They assume `uv` is already installed:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe scripts/fetch_pageindex.py
uv pip install --python .venv/Scripts/python.exe -r requirements.lock.txt
uv pip install --python .venv/Scripts/python.exe --no-deps ./vendor/PageIndex
.\.venv\Scripts\python.exe -c "from pageindex import PageIndexClient; import importlib.metadata; print(importlib.metadata.version('pageindex'))"
```

`requirements.lock.txt` pins third-party dependencies. PageIndex itself is installed separately from the pinned source commit.
The fetch script refuses to overwrite an existing `vendor/PageIndex`. See [pageindex_source.json](../pageindex_source.json) for the revision and source archive hash.

Use your local credential-management mechanism to provide `OPENAI_API_KEY` to the current process and, if needed, `OPENAI_BASE_URL`.
The default endpoint is `https://api.openai.com/v1`. No credential file or key needs to be committed.
The current runner uses `gpt-6-luna` and `gpt-6-sol`; the selected endpoint must support these models and medium reasoning effort.

## Start a new full-corpus run

Use a new output directory rather than an archived experiment directory:

```powershell
.\.venv\Scripts\python.exe scripts/run_benchmark.py --prepare --run-dir outputs/benchmark/reproduction-01
.\.venv\Scripts\python.exe scripts/run_benchmark.py --run-dir outputs/benchmark/reproduction-01
```

The first command freezes document, query, configuration, and script snapshots without calling a model. The second indexes the corpus and answers every question.
Resuming the same directory skips completed and recorded-failed checkpoints. Keep the new run's local `.pageindex/` store to resume from its index.
This rebuildable store is excluded from the published repository; index trees and retrieval evidence are preserved under `outputs/`.

The historical `--credentials-container sirchmunk` option only reads an existing connection configuration. A new environment can use process variables without Docker.

## Inspect and verify existing results

After installing the pinned source, verify original documents, answer hashes, observed models, and prompt records offline:

```powershell
.\.venv\Scripts\python.exe scripts/audit_benchmark_results.py --run-dir outputs/benchmark/20261027-164054
```

This command does not call a model, but it updates the check timestamp in `final_verification.json`.
To leave archived files untouched, read the [saved verification record](../outputs/benchmark/20261027-164054/final_verification.json) instead.

The reporting scripts only read saved outputs and judgments; they do not automatically grade a new experiment.
The 110-question run used reference-based AI review in the Codex conversation. See
[review_method.json](../outputs/benchmark/20261027-164054/evaluation/review_method.json) for the method and limitations.
`evaluate_benchmark.py` is the unexecuted additional API grading plan, not a step performed in this completed run.

## Frozen records and translated documentation

Script snapshots, configuration, answers, scores, and logs retain their recorded state. Reports and the protocol were translated into English on October 28, 2026;
[translation_manifest.json](translation_manifest.json) records the original commit and document hashes.
The completion manifest's report hash was updated for the English report; its other artifact hashes were preserved.
Historical absolute paths provide provenance. A new run generates its own paths from the current checkout.
Use a new run ID and document any changes to models, prompts, concurrency, or input data.
