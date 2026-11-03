# PageIndex: 300-document formal test

**November 2, 2026 · 300 PDFs · 120 questions · 240 A/B outcomes**

Adding a metadata router reduced median question latency by **24.25%** and avoided three turn-limit failures. API-reviewed full passes were **116/120 versus 110/120**. Estimated answering cost increased **8.52%**.

**Published results use only the second API grading run**, selected for reporting on November 3, 2026. Answers and API scores are unchanged. [Errors and partial answers: all 14 cases](errors/README.md).

## Document library

| Property | Value |
|---|---:|
| Documents | 300: 282 RFPs (including 5 templates), 18 DDQs |
| Pages | 10,828: 10,480 RFP, 348 DDQ |
| Total size | 199,741,098 bytes / 190.49 MiB |
| Pages per document | Median 34; mean 36.09; range 2–131; P95 79 |
| File size | Median 504.79 KiB; range 23.50 KiB–4.18 MiB |
| Page-count bands | 1–10: 46; 11–25: 72; 26–50: 104; 51–100: 73; 101+: 5 |
| Exact duplicates | 0 by file hash; 0 by normalized-text hash |

All **44,850 document pairs** were compared. The 71 similar pairs were reviewed and retained as distinct mandates or procurement rounds sharing templates. Distinct documents can therefore share substantial wording. The collection focuses on institutional investment, pensions and related financial services; it is not a balanced market sample.

Every PDF passed the local parser checks. Native text extraction used **PyPDF2 3.0.1, without OCR**. Three PDFs had permission encryption removed with content-equivalence checks. Five observed image-only pages in four documents remain text-extraction limitations. Per-file source URLs, pages, bytes, hashes and exceptions are in [the inventory](data/corpus.jsonl).

## Test process

1. Freeze the same 300 PDFs and existing official indices for both arms. Use 120 held-out English questions: **90 cross-document (75%), 24 single-document (20%), 6 insufficient-evidence (5%)**. Evidence document families are separated from the development split; no development questions or results are included here.
2. **A — official:** official local PageIndex discovers documents across the full library, reads pages and answers. **B — router + official:** an LLM first selects IDs from all 300 filename/description records; official chat then operates within those IDs. No fixed top-k or full-library fallback. Neither pipeline normally reads every PDF in full.
3. Run locally with **PageIndex 0.2.10**, shared `gpt-6-luna` indices, `gpt-6-sol` routing/chat, and **medium** reasoning. Keep official answer instructions and the default **10 chat turns**. No custom answer/citation prompt or evidence-coverage intervention. Four workers, seed 42, shuffled/interleaved arms, fresh conversations, one generation per arm/question. The 240 jobs finished in **20.59 minutes**; failures were retained.
4. Grade the frozen answers through the external API: **120 paired requests**, randomized anonymous labels, references and a common union of evidence pages; `gpt-6-sol`, medium. This is the second grading run and the sole published score set. Previous scores were excluded from judge inputs. No answering/routing model received references. Neither prompts nor routing were tuned using formal results.

Scoring: **1 = complete, supported answer with source/page citations; 0.5 = supported but incomplete or missing page citations; 0 = material error or runtime failure.** Full-pass rate counts only score 1.

## Results

| Metric | A: official | B: router + official |
|---|---:|---:|
| Completed answers | 117/120 | 120/120 |
| Full passes | **110/120 (91.67%)** | **116/120 (96.67%)** |
| Partial answers | 5 | 4 |
| Completed material errors | 2 | 0 |
| Runtime failures | 3 | 0 |
| Median question latency | 23.231 s | 17.598 s |
| P95 question latency | 30.659 s | 26.796 s |
| Model calls | 978 | 682 |
| Input tokens | 18,448,995 | 9,861,584 |
| Estimated answering cost | $16.06 | $17.43 |
| All annotated required documents selected | 112/114 | **114/114** |
| All annotated required documents read | 112/114 | 113/114 |

Latency includes routing in B and retained failed attempts. Median is the 50th percentile; P95 is the 95th percentile. Document-coverage denominators exclude the six insufficient-evidence questions. The read metric means a successful page read from each required document, not every required evidence page.

| Question type | N | A: full passes | B: full passes |
|---|---:|---:|---:|
| Cross-document | 90 | 84/90 (93.33%) | 87/90 (96.67%) |
| Single-document | 24 | 21/24 (87.50%) | 24/24 (100%) |
| Insufficient evidence | 6 | 5/6 (83.33%) | 5/6 (83.33%) |

Answering cost was **$33.49 total**, including **$9.88 for B's router**. API grading added **$2.27**: **$35.76 combined**, excluding index preparation. These are estimates under recorded rates, not an invoice. B used 46.55% fewer input tokens but cost more because of routing and the observed cache mix; provider caches were not controlled. Exact usage, rates and metrics are in [summary](data/summary.json) and [configuration](experiment.json).

## What failed, and where

**A:** two material errors, three turn-limit failures and five incomplete answers. **B:** two detail omissions and two missing page citations; no zero-score outcomes. B's four cases selected the relevant documents and read the annotated evidence pages. The missing facts were present in returned text, so increasing router candidates alone would not directly fix those omissions.

The separate [error README](errors/README.md) lists all **14 outcomes below full credit across 13 questions**, with questions, actual answers, required facts, API deductions and failure stages. Partial credit and runtime failures are distinguished from materially wrong answers.

**Selection is not answer accuracy.** B selected all annotated required sources in 114/114 answerable questions. Its apparent read miss, **145**, used a valid 2023 alternative to the annotated 2018 RFP; the question did not specify a year. Both answers were accepted, while raw coverage metrics remain unchanged.

## Interpretation and limits

- **Supported in this run:** faster answering and more reliable completion with broadly comparable answer quality. Chat browsed a median 200 catalogue entries in A versus 2 in B, but B's router still receives **all 300 metadata entries on every question**. This does not establish efficient scaling to 3,000–4,000 documents.
- **Model-judge limitations:** the API judge is the answering model, with no independent human adjudication. On **082/B**, its full-credit rationale overstates the answer's explicit coverage of the 18–24-month window. The API score remains unchanged; this case is a review caveat, not an additional failed answer.
- **Reference limitations:** 004 has a placeholder-text mismatch; 016's judge packet omits an incumbent-supporting page subsequently checked locally; 032 omits a historical appendix value; 049 contains conflicting source-template dates. These are recorded in per-answer API flags.
- **Next validation:** independently adjudicate ambiguous scores, test answer-completeness/citation checks on development data, then evaluate larger-library routing. This single-run, authored benchmark does not establish a general accuracy gain.

## Files

- [Corpus inventory](data/corpus.jsonl): 300 records, including the exact router metadata.
- [Questions](data/questions.jsonl) and [references](data/references.jsonl): only the 120 formal cases; references were used only for evaluation.
- [Answers](data/answers.jsonl): all 240 outcomes, API scores/reasons, document/page selections, timing and usage. Answer strings are unchanged; their original document links refer to filenames in the inventory.
- [Evidence pages](data/evidence_pages.jsonl): 719 unique pages, deduplicated from the judge's 1,008 page occurrences; references list each question's evidence IDs.
- [Configuration](experiment.json), [router instructions](router_instructions.txt), [official chat instructions](official_chat_instructions.txt), [source hashes](provenance.json) and [file checksums](SHA256SUMS): settings and integrity records for this export.

This is a compact results snapshot. Original PDF binaries, local indices, credentials, verbose traces and earlier experiments are excluded; PDF source links and hashes identify the documents used. It is not a standalone executable pipeline package.
