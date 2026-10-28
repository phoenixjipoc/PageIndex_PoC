# PageIndex PoC

A local document retrieval and question-answering experiment using [VectifyAI/PageIndex](https://github.com/VectifyAI/PageIndex).
This repository contains the original PDFs, evaluation questions, reproduction scripts, index trees, per-question outputs, and experiment records.

## Results

Full-corpus run `20261027-164054` completed on October 27, 2026:

| Metric | Result |
|---|---:|
| Documents / pages | 78 PDFs / 2,546 pages |
| Successful indexing / completed answers | 78/78 / 110/110 |
| Preliminary answer assessment | 107 correct / 3 partial / 0 incorrect |
| Preliminary fully correct rate | 97.3% |
| All required sources read | 99/102 answerable questions |
| Unanswerable questions | 8/8 assessed as correct |
| Median / P95 question latency | 13.383 / 26.128 seconds |
| Indexing and answering wall time | Approximately 37.3 minutes, including recovery gaps |
| Estimated indexing and answering API cost | $9.755929; not an invoice |

**Scores come from a question-by-question review against the reference answers and acceptance criteria in the Codex conversation after generation. They are not human-verified accuracy or independent model-judge results.**
`CONS-16` remains flagged for human review. No other retrieval system was run alongside this experiment, so these results do not establish comparative performance.

- [Full results report](docs/RESULTS.md)
- [Per-question answers, source coverage, and scores (CSV)](outputs/benchmark/20261027-164054/question_results.csv)
- [Per-document indexing results (CSV)](outputs/benchmark/20261027-164054/index_results.csv)
- [Machine-readable summary](outputs/benchmark/20261027-164054/summary.json)
- [Final integrity checks](outputs/benchmark/20261027-164054/final_verification.json)
- [Experiment protocol](outputs/benchmark/20261027-164054/EXPERIMENT_PROTOCOL.md)

## Fixed configuration

- PageIndex 0.2.10, with official source pinned to [`e38b40e`](https://github.com/VectifyAI/PageIndex/tree/e38b40ebaeea26d2c7206b80ce7bc9bf2935cdec).
- Windows / Python 3.11; `gpt-6-luna` for indexing and `gpt-6-sol` for answering, both with `medium` reasoning effort.
- Official Flash/full indexing and default prompts; no custom instructions or optional citation prompt.
- Every question can access all 78 documents, without correct-source hints, a supplied doc_id, or shared conversation history. Reference answers never enter generation requests.
- Documents indexed in filename order; questions shuffled with seed 42 and run in four independent concurrent sessions.

## Data and records

| Directory or file | Purpose |
|---|---|
| `documents/S/` | 78 original public PDFs; the only retrieval corpus input |
| `documents/manifest_S.csv` | Original source URLs, file sizes, and SHA-256 hashes |
| `questions/queries.json` | 110 questions without reference answers |
| `questions/standards.json` | Reference answers, acceptance criteria, and required sources, used only after generation |
| `questions/questions_verified.csv` | Full reference records and original audit notes |
| `scripts/` | Environment preparation, generation, auditing, summarization, and reporting scripts |
| `outputs/benchmark/20261027-164054/` | Raw records and final results of the full-corpus experiment |
| `outputs/example/` | Three earlier examples with different configurations; consult each run's records |
| `requirements.lock.txt` / `pageindex_source.json` | Dependency versions and the pinned official source |

Within the benchmark output, `index/` stores index trees and model usage; `questions/` stores answers, tool traces, and returned evidence;
`evaluation/` stores review inputs, scores, and reasons. The two recording-process recoveries and script snapshots are documented in `runner_revisions.json`.

Raw experiment records remain unchanged and may contain absolute paths from the original machine. The reports and protocol have been translated into English;
[translation provenance](docs/translation_manifest.json) records their original and translated hashes. `docs/RESULTS.md` uses repository-relative links.
`copy_manifest.json` and `questions/verification_report.md` are preparation-stage records that still mention the subsequently removed
`approved_corrections.jsonl`. That file is absent from the current dataset; use `standards.json` and the verified CSV for the current references.
Rights to PDFs and other third-party text remain with their respective owners; source URLs are listed in the document manifest.

## Reproduction

[Environment setup and new runs](docs/REPRODUCING.md) · [Full benchmark guide](RUN_BENCHMARK.md) · [Single-document example](RUN_EXAMPLE.md)

`.venv/`, `.cache/`, `.pageindex/`, and the downloaded `vendor/` directory are excluded from version control. Index trees and execution evidence are included in the outputs.
Credentials are supplied through the process environment and are not stored in the repository. Reading the historical container configuration is optional; PageIndex itself runs locally.

The planned additional grading API run was rejected by automatic approval review before execution and replaced with review in the Codex conversation.
The original grading script and prompt are retained as an unexecuted plan; that grading API did not receive the scoring materials.
