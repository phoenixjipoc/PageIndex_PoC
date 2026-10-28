"""Verify corpus, generation settings and immutable answer records after a full run."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

from benchmark_audit import read_jsonl, utc_now, write_json

ROOT=Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audit(out):
    cfg=json.loads((out/'config.json').read_text(encoding='utf-8'))
    qs=json.loads((out/'inputs/queries.json').read_text(encoding='utf-8'))
    answers=[json.loads(p.read_text(encoding='utf-8')) for p in (out/'questions').glob('*/result.json')]
    docs=json.loads((out/'inputs/documents.json').read_text(encoding='utf-8'))
    index=[json.loads(p.read_text(encoding='utf-8')) for p in (out/'index').glob('*/result.json')]
    requests=[r for lane in ['index','questions'] for p in (out/lane).glob('*/requests.jsonl') for r in read_jsonl(p)]
    responses=[r for lane in ['index','questions'] for p in (out/lane).glob('*/model_calls.jsonl') for r in read_jsonl(p)]
    question_map={q['id']:q['question'] for q in qs}
    manifest=json.loads((ROOT/'copy_manifest.json').read_text(encoding='utf-8'))
    core=[f for f in manifest['files'] if f['path'].startswith('documents/') or f['path'] in ('questions/queries.json','questions/standards.json','questions/questions_verified.csv')]
    changed=[f['path'] for f in core if digest(ROOT/f['path'])!=f['sha256']]
    source=ROOT/'vendor/PageIndex/pageindex'; installed=ROOT/'.venv/Lib/site-packages/pageindex'
    files=list(source.rglob('*.py'))
    source_changes=[str(p.relative_to(source)) for p in files if not (installed/p.relative_to(source)).exists() or digest(p)!=digest(installed/p.relative_to(source))]
    record={'checked_at_utc':utc_now(),'document_count':len(docs),'index_checkpoints':len(index),
        'index_statuses':dict(Counter(r['status'] for r in index)),'question_checkpoints':len(answers),
        'question_statuses':dict(Counter(r['status'] for r in answers)),
        'all_question_ids_accounted_for':{q['id'] for q in qs}=={a['id'] for a in answers},
        'all_questions_unchanged':all(a['question']==question_map[a['id']] for a in answers),
        'all_questions_have_full_library':all(a['available_documents']==78 for a in answers),
        'all_source_hints_and_history_empty':all(a['source_hints'] is None and a['history'] is None for a in answers),
        'http_attempt_count':len(requests),'unique_response_count':len({r['response_id'] for r in responses}),
        'response_count':len(responses),'actual_models':dict(Counter(r['response_model'] for r in responses)),
        'all_medium':all(r['reasoning_effort']=='medium' for r in requests),
        'all_models_match':all(r['model_matches'] for r in requests+responses),
        'all_chat_instructions_official':all(r['official_instructions_match'] for r in requests if r['lane']=='chat'),
        'checked_core_input_files':len(core),'changed_core_inputs':changed,
        'official_python_source_files_checked':len(files),'changed_installed_official_sources':source_changes}
    freeze=out/'generation_manifest.json'
    if freeze.exists():
        frozen=json.loads(freeze.read_text(encoding='utf-8'))['answer_sha256']
        record['changed_frozen_answers']=[name for name,sha in frozen.items() if digest(out/name)!=sha]
        judgments=[json.loads(p.read_text(encoding='utf-8')) for p in (out/'evaluation').glob('*/judgment.json')]
        record['reviewed_questions']=len(judgments)
        record['all_questions_reviewed']={j['question_id'] for j in judgments}==set(question_map)
        record['review_methods']=dict(Counter(j.get('method') for j in judgments))
        record['all_review_answer_hashes_match']=all(j.get('answer_sha256')==digest(out/'questions'/j['question_id']/'result.json') for j in judgments)
        record['additional_grading_api_calls']=sum(bool(j.get('model_call_made') or j.get('response_id')) for j in judgments)
    write_json(out/'final_verification.json',record)
    print(json.dumps(record,ensure_ascii=False,indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--run-dir',required=True)
    a=p.parse_args();audit((ROOT/a.run_dir).resolve())
