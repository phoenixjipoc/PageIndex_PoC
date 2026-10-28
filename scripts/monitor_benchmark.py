"""Read completed item checkpoints independently of the coordinator's progress lock."""
import argparse
from collections import Counter
import json
from pathlib import Path
from benchmark_audit import utc_now, write_json

ROOT = Path(__file__).resolve().parents[1]


def snapshot(out):
    index = [json.loads(p.read_text(encoding='utf-8')) for p in (out/'index').glob('*/result.json')]
    questions = [json.loads(p.read_text(encoding='utf-8')) for p in (out/'questions').glob('*/result.json')]
    done_index = [r for r in index if r['status'] in ('completed','failed')]
    done_questions = [r for r in questions if r['status'] in ('completed','failed')]
    result = {'at_utc':utc_now(), 'index':dict(Counter(r['status'] for r in index)),
        'questions':dict(Counter(r['status'] for r in questions)),
        'index_terminal':len(done_index), 'questions_terminal':len(done_questions),
        'active_documents':[r['file'] for r in index if r['status']=='running'],
        'active_questions':[r['id'] for r in questions if r['status']=='running'],
        'recent_questions':[{'id':r['id'],'status':r['status'],'elapsed_seconds':r.get('elapsed_seconds'),
            'error_type':r.get('error_type'),'error':r.get('error'),
            'read_sources':r.get('successfully_read_documents',[]),
            'request_settings_match':r.get('all_request_settings_match')} for r in sorted(done_questions,key=lambda x:x.get('finished_at_utc',''),reverse=True)[:5]]}
    write_json(out/'live_progress.json',result)
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--run-dir',required=True)
    args=parser.parse_args(); snapshot((ROOT/args.run_dir).resolve())
