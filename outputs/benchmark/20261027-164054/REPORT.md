# PageIndex full-corpus experiment results

Run `20261027-164054` | October 27, 2026 | 78 PDFs / 2,546 pages / 110 questions.

Indexing succeeded for **78/78** documents; **110/110** questions received completed answers.
Preliminary AI review against the reference answers in the Codex conversation: **107/110 fully correct (97.3%)**, **3 partial**, and **0 incorrect or runtime failures**.
With correct = 1, partial = 0.5, and incorrect/failure = 0, the mean score is **0.986**. Assessment is complete for 110/110 questions.

**These semantic labels come from review in the Codex conversation, not human-verified accuracy or an independent model-judge experiment.** Answers were frozen before scoring against the existing acceptance criteria. No additional grading API calls were made. The same conversation supported execution and evaluation, creating a risk of confirmation bias; human review of deductions and ambiguous cases is recommended.

The observed errors were omissions: INV-19 omitted aggregated commitment amounts; XD-17 omitted South Carolina RSIC; XD-18 omitted Arizona PSPRS. The latter two answers did not successfully read the omitted documents. All three deductions were checked against the original PDFs. CONS-16 correctly identifies the modal threshold but omits the COAERS alternative when listing issuers; it remains flagged for human review.

## Configuration

- PageIndex 0.2.10; official source pinned to commit e38b40ebaeea26d2c7206b80ce7bc9bf2935cdec.
- Local Windows execution, with gpt-6-luna for indexing and gpt-6-sol for retrieval and answering; both use medium reasoning effort.
- Official Flash/full indexing and built-in prompts; no custom instructions or optional citation prompt.
- Official summary concurrency limit of 64 and chat limit of 10 turns; SDK timeouts, retries, and output limits are not overridden.
- Documents indexed sequentially in filename order; questions shuffled with seed 42 and run in four independent concurrent sessions.
- Each question sees the full indexed corpus, without correct-source hints, a supplied doc_id, or shared history. Reference answers are used only after answers are frozen and never enter PageIndex generation requests.
- The local index starts empty. Server-side prompt caches are not cleared; returned cache usage is recorded separately.

## Results by group

| Question scope | Total | Completed | Fully correct | Partial |
|---|---:|---:|---:|---:|
| Unanswerable | 8 | 8 | 8 | 0 |
| Multiple required documents | 10 | 10 | 8 | 2 |
| Single document | 92 | 92 | 91 | 1 |

| Original question type | Total | Completed | Fully correct | Partial |
|---|---:|---:|---:|---:|
| broad | 10 | 10 | 8 | 2 |
| detail | 47 | 47 | 47 | 0 |
| medium | 17 | 17 | 16 | 1 |
| pair_a | 14 | 14 | 14 | 0 |
| pair_b | 14 | 14 | 14 | 0 |
| unanswerable | 8 | 8 | 8 | 0 |

Both answers were assessed as fully correct in **14 of 14 pairs**. This measures paired correctness, not a complete semantic-consistency review.

## Reading original source pages

Of 102 answerable questions, **102** successfully read at least one required source, and **99** read all required sources.
Macro-average required-source recall across questions was **99.2%**.
This metric counts successful get_page_content results. Browsing document names or reading section summaries does not count as reading original pages. It measures document coverage, not whether every answer claim has sufficient evidence.

## Timing and usage

| Stage | Wall time (seconds) | Model responses | Input tokens | Output tokens | Estimated USD |
|---|---:|---:|---:|---:|---:|
| Indexing | 1821.42 | 2072 | 2,240,986 | 568,067 | 0.538854 |
| Retrieval and answering | 415.364 | 671 | 9,020,534 | 47,903 | 9.217075 |
| Additional grading API (not executed) | N/A | 0 | 0 | 0 | 0.0 |

Median per-question latency was **13.383 seconds**, with **P95 26.128 seconds**. The metric includes elapsed time for any failed questions. Four questions run concurrently, so summing their individual latencies does not give wall time.
Wall time from the first indexing job to the final answer, including recovery gaps, was **2236.862 seconds**. Initial dependency imports are excluded.
Estimated indexing and answering cost totals **$9.755929**. The additional grading API was not executed and cost $0. Review usage and cost within the Codex conversation are outside this API estimate.
The estimate uses the public Standard token rates recorded on October 27, 2026, including per-request cache read/write and long-context rules: [GPT-6 Luna](https://developers.openai.com/api/docs/models/gpt-6-luna) and [GPT-6 Sol](https://developers.openai.com/api/docs/models/gpt-6-sol). It excludes account discounts, other service tiers, regional surcharges, taxes, and failed requests without returned usage. It is not an invoice.

## Operational issues and limitations

- After indexing the fifth document, the initial process hit a Windows permission error while replacing the progress file. Short retries were added and execution resumed with document six. The first five documents were not regenerated; original and revised script snapshots are retained. Models, prompts, inputs, and scoring rules were unchanged.
- The coordinator attempted to acquire a non-reentrant lock twice. Independent answering jobs continued, with progress monitored through individual checkpoints. Once every answer was saved, bookkeeping resumed with a reentrant-lock repair and no additional model calls. See runner_revisions.json.
- Document failures: 0. Question runtime failures: 0. Any failures remain in the overall denominators.
- All observed model and request settings matched the configuration: **True**.
- The index contains 2470 nodes, with 0 missing summaries and 0 invalid page ranges. These are structural checks, not human verification of summary meaning.
- Hash checks passed for 82 core input files, 110 frozen answers, and 96 installed official Python source files. All 486 request, response, and tool logs were unchanged across bookkeeping recovery, confirming no repeated model calls.
- Sirchmunk and vector RAG were not rerun alongside this experiment; the report cannot establish comparative performance.
- This is one fixed-dataset run without repeated sampling. Latency and caching reflect this run's four concurrent sessions and server-side cache state, not a production SLA.
- Scoring checks required facts and completeness against the references. It does not independently verify every citation page or every additional claim across all answers.
- The official defaults do not require structured citation tags. Answers may use ordinary text citations; an empty citation-tag list does not imply an absence of attribution.


## Priority review items

| Question | Preliminary assessment | Reason |
|---|---|---|
| CONS-16 | correct; borderline case for human review | Correct modal five-year threshold and frequency distribution. COAERS alternative is not explained in the brief issuer list; review whether this optional elaboration needs a caveat. |
| INV-19 | partial | Per-fund requirements are correct, but the enumerated portfolio aggregates omit commitment amounts (item vi), required along with items vii-xi. |
| XD-17 | partial | Correct Illinois and NYC requirements and LAFPP exemption, but omits the operative South Carolina RSIC Iran provision. |
| XD-18 | partial | Correct three documents and purposes, but omits Arizona PSPRS and ILPA-recommended portfolio metrics. |

Up to 20 priority items are listed here. All answers, scores, and reasons are available in the detailed results.

## Files

- [Per-question answers, source coverage, and scores (CSV)](question_results.csv)
- [Per-document indexing results (CSV)](index_results.csv)
- [Machine-readable summary](summary.json)
- [Experiment protocol](EXPERIMENT_PROTOCOL.md)
- [Frozen configuration](config.json)
- [Official generation instructions](official_chat_instructions.txt)
- [Actual assessment method and reason for the change](evaluation/review_method.json)
- [Final integrity checks](final_verification.json)
- [Source spot checks](evaluation/source_spot_checks.json)
- [Runner revision history](runner_revisions.json)

Full tool traces and evidence are under `questions/<question-id>/`; assessment inputs and judgments are under `evaluation/<question-id>/`. The original grading API plan and prompt are retained for audit purposes but were not executed or included in PageIndex generation requests.

Automatic approval review rejected additional API grading because authorization to send the local answers and scoring references to api.openai.com was insufficient. Review was completed in the Codex conversation instead, without sending these materials to that grading API.
