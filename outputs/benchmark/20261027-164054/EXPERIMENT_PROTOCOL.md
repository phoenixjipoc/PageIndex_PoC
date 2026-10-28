# PageIndex full-corpus experiment protocol

Run ID: 20261027-164054. Configuration and input manifests were frozen before answer generation.

## Inputs and runtime conditions

- 78 public PDFs, totaling 2,546 pages; 110 original questions.
- 92 single-document questions, 10 requiring multiple documents, and 8 unanswerable questions; 14 question pairs.
- PageIndex 0.2.10 pinned to commit e38b40ebaeea26d2c7206b80ce7bc9bf2935cdec.
- Official Flash/full indexing and built-in retrieval prompts, without custom prompts.
- gpt-6-luna for indexing and gpt-6-sol for answering, both using medium reasoning effort. Chat uses the officially supported Responses API interface.
- Official limits of 64 concurrent summaries and 10 chat turns; no overrides of timeouts, retries, or output-token limits.
- The optional citation prompt remains disabled. Missing `<cite>` tags alone do not make an answer incorrect.
- Local Windows execution; only existing connection configuration is read, and keys are not saved in experiment files.

## Execution order and isolation

1. Create a fresh local index, processing documents in ascending filename order. Save each file's page count, hash, tree, status, timing, and usage.
2. After all indexing attempts, freeze the available document list. Do not silently switch indexing mode or model when a document fails.
3. Shuffle questions with seed 42 and execute four independent sessions concurrently. Each receives only the original question, the full available library, and official prompts.
4. Do not supply a doc_id, correct filename, reference answer, scoring criteria, or history from another question. The generator reads only the answer-free queries.json.
5. Maintain independent checkpoints for every document and question. Keep failures in the denominators; do not select the best answer from repeated runs.
6. After answers are complete and frozen, read standards.json separately for evaluation. Never feed grading content back to PageIndex or trigger answer retries based on grading.

## Required records

Retain input manifests and SHA-256 hashes; software versions and source consistency checks; actual model responses;
medium reasoning settings in outgoing requests; official-prompt consistency; stage start/end times and usage;
cache statistics; every tool call and returned evidence; complete final answers; failure types and messages;
index coverage; and the documents/pages read for each question. Include model responses completed before a failure in usage accounting.

Exclude API keys, authorization headers, and private model reasoning from logs. Requests without returned usage may incur unobserved consumption;
token totals are not an invoice. Reuse natural server-side caches and do not describe the experiment as a cold-cache test.

## Evaluation definitions

- **Indexing success rate:** successfully indexed documents / 78. Retain failed files and affected questions.
- **Answer completion rate:** nonempty final answers with completed status / 110. Successful execution does not establish factual correctness.
- **Required-source page reads:** count successful get_page_content results. Seeing a filename or section summary does not count as reading original pages.
  For 102 answerable questions, report whether at least one required source and all required sources were read, plus per-question required-source recall.
  Tool-limit failures, missing source reads, and missing answers remain in the results and denominators.
- **Semantic answer score:** use each question's gold_answer and acceptance criteria. Correct = 1, partial = 0.5, incorrect or incomplete execution = 0.
  Report fully correct rate separately from mean score. If a model performs grading, label it as preliminary automated assessment and retain the model,
  grading prompt, reasons, and usage; do not call it human-verified accuracy. Evaluation prompts belong only to separate grading, not the retrieval/generation pipeline.
- **Unanswerable questions:** follow each acceptance criterion to distinguish an unspecified threshold, a false premise, and missing information.
  Failure to find a file does not automatically constitute a correct refusal.
- **Paired questions:** report the proportion of 14 pairs in which both answers are correct. Semantic consistency is not simply identical wording.
- Break down results by original question type and single_document / required_combination / negative scope, including failures and partial answers.
- Report total and per-stage wall time plus median/P95 per-question latency. Explain concurrent question latency separately from sequential indexing time.

This run evaluates PageIndex only. Sirchmunk and vector RAG are not rerun in parallel, so it does not support a comparative system ranking.
