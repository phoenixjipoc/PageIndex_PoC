"""Offline accounting and required-source retrieval evaluation; makes no model calls."""
import argparse
from collections import Counter, defaultdict
import csv
from datetime import datetime
import hashlib
import json
from pathlib import Path
import statistics

from benchmark_audit import write_json, read_jsonl

ROOT = Path(__file__).resolve().parents[1]


def percentile(values, fraction):
    if not values:
        return None
    values = sorted(values)
    pos = (len(values) - 1) * fraction
    lower = int(pos)
    upper = min(lower + 1, len(values) - 1)
    return round(values[lower] + (values[upper] - values[lower]) * (pos - lower), 3)


def total_usage(items):
    keys = ['input_tokens', 'output_tokens', 'cached_input_tokens', 'cache_write_tokens', 'reasoning_tokens', 'total_tokens']
    return {key: sum((r.get('observed_usage') or {}).get(key, 0) for r in items) for key in keys}


def load_results(directory):
    return [json.loads(p.read_text(encoding='utf-8')) for p in sorted(directory.glob('*/result.json'))]


def csv_rows(path, rows, fields):
    with path.open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction='ignore')
        writer.writeheader()
        for row in rows:
            writer.writerow({k: json.dumps(v, ensure_ascii=False) if isinstance(v, (list, dict)) else v for k, v in row.items() if k in fields})


def summarize(out):
    cfg = json.loads((out / 'config.json').read_text(encoding='utf-8'))
    status = json.loads((out / 'status.json').read_text(encoding='utf-8'))
    index = load_results(out / 'index')
    answers = load_results(out / 'questions')
    expected = json.loads((out / 'inputs/queries.json').read_text(encoding='utf-8'))
    snapshot = json.loads((out / 'inputs/hashes.json').read_text(encoding='utf-8'))
    standards_path = ROOT / 'questions/standards.json'
    if hashlib.sha256(standards_path.read_bytes()).hexdigest() != snapshot['questions/standards.json']:
        raise RuntimeError('Scoring standards changed after preparation.')
    standards = {s['id']: s for s in json.loads(standards_path.read_text(encoding='utf-8'))}
    original_name = {r.get('stored_name', r['file']): r['file'] for r in index}
    judgments = {}
    for path in (out / 'evaluation').glob('*/judgment.json'):
        j = json.loads(path.read_text(encoding='utf-8'))
        judgments[j['question_id']] = j
    review_path = out / 'evaluation/review_method.json'
    review_method = json.loads(review_path.read_text(encoding='utf-8')) if review_path.exists() else {}
    rows = []
    for answer in answers:
        s = standards[answer['id']]
        read = {original_name.get(n, n) for n in answer.get('successfully_read_documents', [])}
        required = set(s.get('required_sources') or [])
        matched = sorted(required & read)
        judge = judgments.get(answer['id'], {})
        score = 0 if answer['status'] == 'failed' else judge.get('score')
        row = {**answer, 'scope': s['scope'], 'required_sources': sorted(required), 'read_sources': sorted(read),
               'matched_required_sources': matched, 'required_source_recall': len(matched) / len(required) if required else None,
               'any_required_source_read': bool(matched) if required else None,
               'all_required_sources_read': required <= read if required else None,
               'score': score, 'verdict': 'runtime_failure' if answer['status'] == 'failed' else judge.get('verdict'),
               'grading_reason': judge.get('reason'), 'grading_status': judge.get('grading_status'),
               'grading_method': judge.get('method'), 'needs_review': judge.get('needs_review', False),
               'grading_confidence': judge.get('confidence'),
               **{k: v for k, v in (answer.get('observed_usage') or {}).items()}}
        rows.append(row)
    answerable = [r for r in rows if r['required_source_recall'] is not None]
    scored = [r for r in rows if r['score'] is not None]
    all_answerable_count = sum(bool(s.get('required_sources')) for s in standards.values())
    summary = {
        'run_id': cfg['run_id'], 'phase': status['phase'], 'documents_total': cfg['documents'], 'pdf_pages_total': cfg['pdf_pages'],
        'index_status_counts': dict(Counter(r['status'] for r in index)),
        'questions_total': len(expected), 'question_status_counts': dict(Counter(r['status'] for r in rows)),
        'index_model_calls': sum(r.get('model_calls', 0) for r in index),
        'chat_model_calls': sum(r.get('model_calls', 0) for r in rows),
        'index_observed_usage': total_usage(index), 'chat_observed_usage': total_usage(rows),
        'index_latency_seconds': {'sum': round(sum(r.get('elapsed_seconds') or 0 for r in index), 3),
                                  'median': percentile([r['elapsed_seconds'] for r in index if r.get('elapsed_seconds') is not None], 0.5)},
        'question_latency_seconds': {'median': percentile([r['elapsed_seconds'] for r in rows if r.get('elapsed_seconds') is not None], 0.5),
                                     'p95': percentile([r['elapsed_seconds'] for r in rows if r.get('elapsed_seconds') is not None], 0.95)},
        'required_source_retrieval': {'denominator': all_answerable_count,
             'questions_with_any_required_source': sum(r['any_required_source_read'] for r in answerable),
             'questions_with_all_required_sources': sum(r['all_required_sources_read'] for r in answerable),
             'macro_recall_all_answerable': sum(r['required_source_recall'] for r in answerable) / all_answerable_count},
        'semantic_evaluation': {'kind': review_method.get('method', 'automatic_initial_assessment'),
                               'human_verified': False, 'scored_questions': len(scored),
                               'fully_correct': sum(r['score'] == 1 for r in scored),
                               'partially_correct': sum(r['score'] == 0.5 for r in scored),
                               'zero_score': sum(r['score'] == 0 for r in scored),
                               'correct_rate_all_110': sum(r['score'] == 1 for r in scored) / len(expected),
                               'mean_score_all_110': sum(r['score'] for r in scored) / len(expected)},
        'index_failures': [{k: r.get(k) for k in ['file', 'pages', 'error_type', 'error']} for r in index if r['status'] == 'failed'],
        'question_failures': [{k: r.get(k) for k in ['id', 'error_type', 'error']} for r in rows if r['status'] == 'failed'],
        'generation_settings_match': all(r.get('all_models_match') and r.get('all_request_settings_match') for r in index + rows if r.get('model_calls', 0)),
    }
    summary['by_scope'] = {}
    for scope in sorted({s['scope'] for s in standards.values()}):
        group = [r for r in rows if r['scope'] == scope]
        summary['by_scope'][scope] = {'total': sum(s['scope'] == scope for s in standards.values()),
             'completed': sum(r['status'] == 'completed' for r in group),
             'fully_correct': sum(r['score'] == 1 for r in group),
             'partially_correct': sum(r['score'] == 0.5 for r in group)}
    pairs = defaultdict(list)
    for row in rows:
        if row.get('pair_id'):
            pairs[row['pair_id']].append(row)
    summary['paired_both_correct'] = {'total_pairs': 14, 'both_correct': sum(len(g)==2 and all(r['score']==1 for r in g) for g in pairs.values())}
    summary['by_type'] = {}
    for kind in sorted({s['type'] for s in standards.values()}):
        group = [r for r in rows if r['type'] == kind]
        summary['by_type'][kind] = {'total': sum(s['type'] == kind for s in standards.values()),
            'completed': sum(r['status'] == 'completed' for r in group),
            'fully_correct': sum(r['score'] == 1 for r in group),
            'partially_correct': sum(r['score'] == 0.5 for r in group)}
    pricing_path = out / 'pricing_reference.json'
    if pricing_path.exists():
        pricing = json.loads(pricing_path.read_text(encoding='utf-8'))
        def cost(usage, model):
            rates = pricing['models'][model]
            tokens_in = usage.get('input_tokens', usage.get('prompt_tokens', 0)) or 0
            tokens_out = usage.get('output_tokens', usage.get('completion_tokens', 0)) or 0
            detail = usage.get('input_tokens_details') or usage.get('prompt_tokens_details') or {}
            cached = detail.get('cached_tokens', 0) or 0
            written = detail.get('cache_write_tokens', 0) or 0
            regular = max(0, tokens_in - cached - written)
            long = tokens_in > pricing['long_context_threshold_input_tokens']
            return ((regular * rates['input'] + cached * rates['cached_input'] + written * rates['cache_write']) *
                    (pricing['long_context_input_multiplier'] if long else 1) + tokens_out * rates['output'] *
                    (pricing['long_context_output_multiplier'] if long else 1)) / 1_000_000
        index_cost = sum(cost(c.get('usage') or {}, cfg['index_model']) for p in (out / 'index').glob('*/model_calls.jsonl') for c in read_jsonl(p))
        chat_cost = sum(cost(c.get('usage') or {}, cfg['chat_model']) for p in (out / 'questions').glob('*/model_calls.jsonl') for c in read_jsonl(p))
        judge_cost = sum(cost(j.get('usage') or {}, 'gpt-6-sol') for j in judgments.values())
        summary['estimated_standard_price_usd'] = {'index': round(index_cost, 6), 'chat': round(chat_cost, 6),
            'semantic_grading': round(judge_cost, 6), 'generation_total': round(index_cost + chat_cost, 6),
            'including_grading': round(index_cost + chat_cost + judge_cost, 6),
            'assumptions': pricing['assumption'], 'unobserved_failed_request_usage_excluded': True}
    summary['semantic_grading_usage'] = {
        'input_tokens': sum((j.get('usage') or {}).get('input_tokens', 0) for j in judgments.values()),
        'output_tokens': sum((j.get('usage') or {}).get('output_tokens', 0) for j in judgments.values()),
        'model_calls': sum(bool(j.get('response_id')) for j in judgments.values()),
        'needs_review': sum(bool(j.get('needs_review')) for j in judgments.values()),
        'grading_errors': sum(j.get('grading_status') != 'completed' for j in judgments.values()),
    }
    def wall_time(records):
        starts = [datetime.fromisoformat(r['started_at_utc']) for r in records if r.get('started_at_utc')]
        finishes = [datetime.fromisoformat(r['finished_at_utc']) for r in records if r.get('finished_at_utc')]
        return round((max(finishes) - min(starts)).total_seconds(), 3) if starts and finishes else None
    summary['stage_wall_clock_seconds'] = {'index': wall_time(index), 'questions': wall_time(rows), 'grading': wall_time(list(judgments.values()))}
    summary['experiment_complete'] = len(index) == cfg['documents'] and len(rows) == len(expected) and len(scored) == len(expected)
    summary['generation_wall_seconds_including_resume_gap'] = wall_time(index + rows)
    if status.get('finished_at_utc') and status.get('started_at_utc'):
        summary['wall_seconds_through_bookkeeping_completion'] = round((datetime.fromisoformat(status['finished_at_utc']) - datetime.fromisoformat(status['started_at_utc'])).total_seconds(), 3)
    quality_path = out / 'index_quality.json'
    if quality_path.exists():
        quality = json.loads(quality_path.read_text(encoding='utf-8'))
        summary['index_structure_checks'] = {key: sum(r[key] for r in quality) for key in ['nodes', 'nodes_without_summary', 'invalid_page_ranges']}
    write_json(out / 'summary.json', summary)
    write_json(out / 'question_results.json', rows)
    csv_rows(out / 'question_results.csv', rows, ['id','type','scope','pair_id','status','question','answer','elapsed_seconds','model_calls',
        'input_tokens','output_tokens','cached_input_tokens','cache_write_tokens','reasoning_tokens','required_sources','read_sources',
        'matched_required_sources','required_source_recall','all_required_sources_read','score','verdict','grading_method','grading_reason','needs_review','grading_confidence','error_type','error'])
    csv_rows(out / 'index_results.csv', [{**r, **r.get('observed_usage', {})} for r in index],
             ['file','pages','sha256','status','doc_id','elapsed_seconds','model_calls','input_tokens','output_tokens','cached_input_tokens','cache_write_tokens','error_type','error'])
    print(json.dumps({k:summary[k] for k in ['phase','index_status_counts','question_status_counts','required_source_retrieval','semantic_evaluation']},indent=2))
    return summary


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--run-dir', required=True)
    args = parser.parse_args()
    summarize((ROOT / args.run_dir).resolve())
