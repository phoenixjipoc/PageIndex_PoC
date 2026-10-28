"""Record in-session reference comparisons locally. No network/model API calls."""
import hashlib
import json
from pathlib import Path
from benchmark_audit import utc_now,write_json


def save_reviews(out, reviews):
    out=Path(out)
    refs={x['id']:x for x in json.loads((out/'evaluation/standards_snapshot.json').read_text(encoding='utf-8'))}
    frozen=json.loads((out/'generation_manifest.json').read_text(encoding='utf-8'))['answer_sha256']
    for review in reviews:
        qid,score,reason,*options=review
        flags=options[0] if options else {}
        answer_path=out/'questions'/qid/'result.json'
        sha=hashlib.sha256(answer_path.read_bytes()).hexdigest()
        assert sha==frozen[str(answer_path.relative_to(out))]
        answer=json.loads(answer_path.read_text(encoding='utf-8'))
        ref=refs[qid]
        directory=out/'evaluation'/qid
        write_json(directory/'input.json',{k:ref[k] for k in ['question','gold_answer','acceptance','scope']} | {'candidate_answer':answer['answer']})
        judgment={'question_id':qid,'grading_status':'completed','method':'in_session_ai_reference_review',
                  'reviewer':'Codex current conversation','human_verified':False,'model_call_made':False,
                  'answer_sha256':sha,'score':score,'verdict':{1:'correct',0.5:'partial',0:'incorrect'}[score],
                  'reason':reason,'needs_review':flags.get('needs_review',False),
                  'confidence':flags.get('confidence','high'),'reviewed_at_utc':utc_now()}
        write_json(directory/'judgment.json',judgment)
    completed=len(list((out/'evaluation').glob('*/judgment.json')))
    write_json(out/'evaluation/status.json',{'phase':'reference_review_completed' if completed==110 else 'reference_review',
               'completed':completed,'failed':0,'method':'in_session_ai_reference_review','at_utc':utc_now()})
    print('Recorded reference reviews:',completed,'/ 110')
