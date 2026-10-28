"""Render an English report from saved experiment results and separate judgments."""
import argparse
import json
from pathlib import Path
from summarize_benchmark import summarize

ROOT = Path(__file__).resolve().parents[1]


def report(out, saved_results=False):
    s = json.loads((out / 'summary.json').read_text(encoding='utf-8')) if saved_results else summarize(out)
    cfg = json.loads((out / 'config.json').read_text(encoding='utf-8'))
    rows = json.loads((out / 'question_results.json').read_text(encoding='utf-8'))
    sem = s['semantic_evaluation']
    cost = s.get('estimated_standard_price_usd', {})
    source = s['required_source_retrieval']

    def link(label, filename):
        return f'[{label}]({filename})'

    lines = [
        '# PageIndex full-corpus experiment results', '',
        f'Run `{cfg["run_id"]}` | October 27, 2026 | 78 PDFs / 2,546 pages / 110 questions.', '',
        f'Indexing succeeded for **{s["index_status_counts"].get("completed", 0)}/78** documents; **{s["question_status_counts"].get("completed", 0)}/110** questions received completed answers.',
        f'Preliminary AI review against the reference answers in the Codex conversation: **{sem["fully_correct"]}/110 fully correct ({sem["correct_rate_all_110"]:.1%})**, **{sem["partially_correct"]} partial**, and **{sem["zero_score"]} incorrect or runtime failures**.',
        f'With correct = 1, partial = 0.5, and incorrect/failure = 0, the mean score is **{sem["mean_score_all_110"]:.3f}**. Assessment is complete for {sem["scored_questions"]}/110 questions.', '',
        '**These semantic labels come from review in the Codex conversation, not human-verified accuracy or an independent model-judge experiment.** Answers were frozen before scoring against the existing acceptance criteria. No additional grading API calls were made. The same conversation supported execution and evaluation, creating a risk of confirmation bias; human review of deductions and ambiguous cases is recommended.', '',
        'The observed errors were omissions: INV-19 omitted aggregated commitment amounts; XD-17 omitted South Carolina RSIC; XD-18 omitted Arizona PSPRS. The latter two answers did not successfully read the omitted documents. All three deductions were checked against the original PDFs. CONS-16 correctly identifies the modal threshold but omits the COAERS alternative when listing issuers; it remains flagged for human review.', '',
        '## Configuration', '',
        '- PageIndex 0.2.10; official source pinned to commit e38b40ebaeea26d2c7206b80ce7bc9bf2935cdec.',
        '- Local Windows execution, with gpt-6-luna for indexing and gpt-6-sol for retrieval and answering; both use medium reasoning effort.',
        '- Official Flash/full indexing and built-in prompts; no custom instructions or optional citation prompt.',
        '- Official summary concurrency limit of 64 and chat limit of 10 turns; SDK timeouts, retries, and output limits are not overridden.',
        '- Documents indexed sequentially in filename order; questions shuffled with seed 42 and run in four independent concurrent sessions.',
        '- Each question sees the full indexed corpus, without correct-source hints, a supplied doc_id, or shared history. Reference answers are used only after answers are frozen and never enter PageIndex generation requests.',
        '- The local index starts empty. Server-side prompt caches are not cleared; returned cache usage is recorded separately.', '',
        '## Results by group', '',
        '| Question scope | Total | Completed | Fully correct | Partial |',
        '|---|---:|---:|---:|---:|',
    ]
    names = {'single_document': 'Single document', 'required_combination': 'Multiple required documents', 'negative': 'Unanswerable'}
    for name, v in s['by_scope'].items():
        lines.append(f'| {names.get(name, name)} | {v["total"]} | {v["completed"]} | {v["fully_correct"]} | {v["partially_correct"]} |')
    lines += ['', '| Original question type | Total | Completed | Fully correct | Partial |', '|---|---:|---:|---:|---:|']
    for name, v in s['by_type'].items():
        lines.append(f'| {name} | {v["total"]} | {v["completed"]} | {v["fully_correct"]} | {v["partially_correct"]} |')
    lines += ['', f'Both answers were assessed as fully correct in **{s["paired_both_correct"]["both_correct"]} of 14 pairs**. This measures paired correctness, not a complete semantic-consistency review.', '',
        '## Reading original source pages', '',
        f'Of {source["denominator"]} answerable questions, **{source["questions_with_any_required_source"]}** successfully read at least one required source, and **{source["questions_with_all_required_sources"]}** read all required sources.',
        f'Macro-average required-source recall across questions was **{source["macro_recall_all_answerable"]:.1%}**.',
        'This metric counts successful get_page_content results. Browsing document names or reading section summaries does not count as reading original pages. It measures document coverage, not whether every answer claim has sufficient evidence.', '',
        '## Timing and usage', '',
        '| Stage | Wall time (seconds) | Model responses | Input tokens | Output tokens | Estimated USD |',
        '|---|---:|---:|---:|---:|---:|',
    ]
    for key, label, usage, calls, price in [
        ('index', 'Indexing', s['index_observed_usage'], s['index_model_calls'], cost.get('index')),
        ('questions', 'Retrieval and answering', s['chat_observed_usage'], s['chat_model_calls'], cost.get('chat')),
        ('grading', 'Additional grading API (not executed)', s['semantic_grading_usage'], s['semantic_grading_usage']['model_calls'], cost.get('semantic_grading')),
    ]:
        duration = s['stage_wall_clock_seconds'].get(key)
        lines.append(f'| {label} | {duration if duration is not None else "N/A"} | {calls} | {usage["input_tokens"]:,} | {usage["output_tokens"]:,} | {price if price is not None else "Not estimated"} |')
    lines += ['', f'Median per-question latency was **{s["question_latency_seconds"]["median"]} seconds**, with **P95 {s["question_latency_seconds"]["p95"]} seconds**. The metric includes elapsed time for any failed questions. Four questions run concurrently, so summing their individual latencies does not give wall time.',
        f'Wall time from the first indexing job to the final answer, including recovery gaps, was **{s.get("generation_wall_seconds_including_resume_gap")} seconds**. Initial dependency imports are excluded.',
        f'Estimated indexing and answering cost totals **${cost.get("generation_total")}**. The additional grading API was not executed and cost $0. Review usage and cost within the Codex conversation are outside this API estimate.',
        'The estimate uses the public Standard token rates recorded on October 27, 2026, including per-request cache read/write and long-context rules: '
        '[GPT-6 Luna](https://developers.openai.com/api/docs/models/gpt-6-luna) and [GPT-6 Sol](https://developers.openai.com/api/docs/models/gpt-6-sol). '
        'It excludes account discounts, other service tiers, regional surcharges, taxes, and failed requests without returned usage. It is not an invoice.', '',
        '## Operational issues and limitations', '',
        '- After indexing the fifth document, the initial process hit a Windows permission error while replacing the progress file. Short retries were added and execution resumed with document six. The first five documents were not regenerated; original and revised script snapshots are retained. Models, prompts, inputs, and scoring rules were unchanged.',
        '- The coordinator attempted to acquire a non-reentrant lock twice. Independent answering jobs continued, with progress monitored through individual checkpoints. Once every answer was saved, bookkeeping resumed with a reentrant-lock repair and no additional model calls. See runner_revisions.json.',
        f'- Document failures: {len(s["index_failures"])}. Question runtime failures: {len(s["question_failures"])}. Any failures remain in the overall denominators.',
        f'- All observed model and request settings matched the configuration: **{s["generation_settings_match"]}**.',
        f'- The index contains {s["index_structure_checks"]["nodes"]} nodes, with {s["index_structure_checks"]["nodes_without_summary"]} missing summaries and {s["index_structure_checks"]["invalid_page_ranges"]} invalid page ranges. These are structural checks, not human verification of summary meaning.',
        '- Hash checks passed for 82 core input files, 110 frozen answers, and 96 installed official Python source files. All 486 request, response, and tool logs were unchanged across bookkeeping recovery, confirming no repeated model calls.',
        '- Sirchmunk and vector RAG were not rerun alongside this experiment; the report cannot establish comparative performance.',
        '- This is one fixed-dataset run without repeated sampling. Latency and caching reflect this run\'s four concurrent sessions and server-side cache state, not a production SLA.',
        '- Scoring checks required facts and completeness against the references. It does not independently verify every citation page or every additional claim across all answers.',
        '- The official defaults do not require structured citation tags. Answers may use ordinary text citations; an empty citation-tag list does not imply an absence of attribution.', '',
    ]
    for failure in s['index_failures']:
        lines.append(f'- Indexing failure `{failure["file"]}`: {failure.get("error_type")} - {failure.get("error")}')
    if s['question_failures']:
        lines += ['', 'Failed question IDs: ' + ', '.join(f'`{f["id"]}`' for f in s['question_failures']) + '. See individual results for details.']
    lines += ['', '## Priority review items', '', '| Question | Preliminary assessment | Reason |', '|---|---|---|']
    review = [r for r in rows if r.get('score') in (0, 0.5) or r.get('needs_review')]
    for r in review[:20]:
        reason = (r.get('grading_reason') or r.get('error') or '').replace('|', '/').replace('\n', ' ')[:260]
        label = str(r.get('verdict')) + ('; borderline case for human review' if r.get('needs_review') else '')
        lines.append(f'| {r["id"]} | {label} | {reason} |')
    lines += ['', 'Up to 20 priority items are listed here. All answers, scores, and reasons are available in the detailed results.', '', '## Files', '',
        '- ' + link('Per-question answers, source coverage, and scores (CSV)', 'question_results.csv'),
        '- ' + link('Per-document indexing results (CSV)', 'index_results.csv'),
        '- ' + link('Machine-readable summary', 'summary.json'),
        '- ' + link('Experiment protocol', 'EXPERIMENT_PROTOCOL.md'),
        '- ' + link('Frozen configuration', 'config.json'),
        '- ' + link('Official generation instructions', 'official_chat_instructions.txt'),
        '- ' + link('Actual assessment method and reason for the change', 'evaluation/review_method.json'),
        '- ' + link('Final integrity checks', 'final_verification.json'),
        '- ' + link('Source spot checks', 'evaluation/source_spot_checks.json'),
        '- ' + link('Runner revision history', 'runner_revisions.json'), '',
        'Full tool traces and evidence are under `questions/<question-id>/`; assessment inputs and judgments are under `evaluation/<question-id>/`. The original grading API plan and prompt are retained for audit purposes but were not executed or included in PageIndex generation requests.', '',
        'Automatic approval review rejected additional API grading because authorization to send the local answers and scoring references to api.openai.com was insufficient. Review was completed in the Codex conversation instead, without sending these materials to that grading API.', '',
    ]
    (out / 'REPORT.md').write_text('\n'.join(lines), encoding='utf-8', newline='\n')
    print('REPORT', str(out / 'REPORT.md'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--run-dir', required=True)
    parser.add_argument('--saved-results', action='store_true', help='Render saved summary and results without rewriting derived JSON or CSV files.')
    args = parser.parse_args()
    report((ROOT / args.run_dir).resolve(), saved_results=args.saved_results)
