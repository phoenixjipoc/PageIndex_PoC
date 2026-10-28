"""Frozen whole-corpus PageIndex experiment. Generation never reads reference answers."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone, timedelta
import csv
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import random
import sys
import threading
import time
from urllib.parse import urlsplit

from benchmark_audit import Audit, JOB, read_jsonl, summarize_job, utc_now, write_json
from connection import load_connection, redact

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def prepare(out):
    from PyPDF2 import PdfReader
    out.mkdir(parents=True, exist_ok=False)
    inputs = out / 'inputs'
    inputs.mkdir()
    queries = json.loads((ROOT / 'questions/queries.json').read_text(encoding='utf-8'))
    assert len(queries) == 110 and len({q['id'] for q in queries}) == 110
    manifest = list(csv.DictReader((ROOT / 'documents/manifest_S.csv').open(encoding='utf-8-sig', newline='')))
    docs = []
    for row in sorted(manifest, key=lambda r: r['file']):
        path = ROOT / 'documents/S' / row['file']
        sha = digest(path)
        if sha != row['sha256']:
            raise ValueError('Corpus hash mismatch: ' + row['file'])
        docs.append({'file': row['file'], 'sha256': sha, 'bytes': path.stat().st_size,
                     'pages': len(PdfReader(path).pages), 'public_source_url': row['url']})
    assert len(docs) == 78
    random.Random(42).shuffle(queries)
    write_json(inputs / 'queries.json', queries)
    write_json(inputs / 'documents.json', docs)
    write_json(inputs / 'source.json', json.loads((ROOT / 'pageindex_source.json').read_text()))
    tracked = ['questions/queries.json', 'questions/standards.json', 'questions/questions_verified.csv',
               'documents/manifest_S.csv', 'requirements.lock.txt', 'pageindex_source.json']
    write_json(inputs / 'hashes.json', {name: digest(ROOT / name) for name in tracked})
    for name in ['run_benchmark.py', 'benchmark_audit.py', 'connection.py']:
        (inputs / name).write_bytes((ROOT / 'scripts' / name).read_bytes())
    (inputs / 'requirements.lock.txt').write_bytes((ROOT / 'requirements.lock.txt').read_bytes())
    config = {
        'run_id': out.name, 'prepared_at_utc': utc_now(), 'local_timezone': 'Asia/Shanghai',
        'scope': 'whole_corpus_blind_retrieval', 'documents': len(docs), 'pdf_pages': sum(d['pages'] for d in docs),
        'questions': len(queries), 'index_model': 'gpt-6-luna', 'chat_model': 'gpt-6-sol',
        'reasoning_effort': 'medium', 'index_mode': 'official_default_flash',
        'optimization': 'official_default_full', 'summary_concurrency': 64, 'max_chat_turns': 10,
        'custom_instructions': False, 'optional_citation_prompt': False, 'chat_protocol': 'responses',
        'backend_timeout_override': None, 'backend_retry_override': None, 'output_token_limit_override': None,
        'index_document_workers': 1, 'question_workers': 4,
        'index_order': 'filename ascending', 'question_order': 'random.Random(42).shuffle',
        'reference_answers_used_in_generation': False, 'source_document_hints_used': False,
        'conversation_history_shared': False, 'outer_retries': 0,
        'index_storage': str(ROOT / '.pageindex' / ('benchmark-' + out.name)),
        'corpus_snapshot_sha256': digest(inputs / 'documents.json'),
        'query_snapshot_sha256': digest(inputs / 'queries.json'),
        'evaluation': 'After generation is frozen; report runtime success, required-document recall, answers, negative questions and paired consistency. Keep semantic adjudication separate from generation.',
        'cache_policy': 'Fresh local index; provider prompt caches are not cleared. Record returned cache usage.',
        'failure_policy': 'Record every failed item and continue; no silent model/mode/prompt fallback. Interrupted items can be resumed; completed/failed checkpoints are not silently rerun.',
    }
    write_json(out / 'config.json', config)
    write_json(out / 'status.json', {'phase': 'prepared', 'at_utc': utc_now(), 'indexed_completed': 0, 'indexed_failed': 0, 'questions_completed': 0, 'questions_failed': 0})
    write_json(out.parent / 'latest.json', {'run_directory': str(out), 'phase': 'prepared'})
    print(json.dumps(config, ensure_ascii=False, indent=2), flush=True)


def run(out, container):
    cfg = json.loads((out / 'config.json').read_text(encoding='utf-8'))
    for name in ['run_benchmark.py', 'benchmark_audit.py', 'connection.py']:
        if digest(ROOT / 'scripts' / name) != digest(out / 'inputs' / name):
            raise RuntimeError('Runner differs from frozen snapshot: ' + name)
    documents = json.loads((out / 'inputs/documents.json').read_text(encoding='utf-8'))
    queries = json.loads((out / 'inputs/queries.json').read_text(encoding='utf-8'))
    for doc in documents:
        if digest(ROOT / 'documents/S' / doc['file']) != doc['sha256']:
            raise RuntimeError('Document changed: ' + doc['file'])
    key, endpoint, previous_model = load_connection(container)
    os.environ.update(OPENAI_API_KEY=key, OPENAI_BASE_URL=endpoint, OPENAI_AGENTS_DISABLE_TRACING='1',
                      HF_HOME=str(ROOT / '.cache/huggingface'), TIKTOKEN_CACHE_DIR=str(ROOT / '.cache/tiktoken'),
                      LITELLM_LOCAL_MODEL_COST_MAP='True')
    print('Loading official PageIndex runtime...', flush=True)
    from pageindex import PageIndexClient
    from pageindex.local_chat import CHAT_HEADER
    source_root = ROOT / 'vendor/PageIndex/pageindex'
    installed = ROOT / '.venv/Lib/site-packages/pageindex'
    differences = [str(p.relative_to(source_root)) for p in source_root.rglob('*.py')
                   if not (installed / p.relative_to(source_root)).is_file() or digest(p) != digest(installed / p.relative_to(source_root))]
    if differences:
        raise RuntimeError('Installed official source differs: ' + ', '.join(differences))

    def new_client():
        return PageIndexClient(
            index={'model': cfg['index_model'], 'storage_path': cfg['index_storage'],
                   'summary_reasoning_effort': 'medium',
                   'backend': {'api_key': key, 'api_base': endpoint, 'reasoning_effort': 'medium'}},
            chat={'model': cfg['chat_model'], 'backend': {'api_key': key, 'base_url': endpoint}})

    client = new_client()
    official = '\n\n'.join([CHAT_HEADER, client.agent_instructions()])
    (out / 'official_chat_instructions.txt').write_text(official + '\n', encoding='utf-8')
    audit = Audit(key, official)
    audit.install()
    write_json(out / 'environment.json', {
        'python': sys.version, 'platform': platform.platform(), 'pageindex_version': importlib.metadata.version('pageindex'),
        'endpoint_host': urlsplit(endpoint).hostname, 'container_default_model_not_used': previous_model,
        'installed_source_matches': True, 'official_instructions_sha256': hashlib.sha256(official.encode()).hexdigest(),
        'packages': {name: importlib.metadata.version(name) for name in ['openai', 'openai-agents', 'litellm', 'PyPDF2', 'pypdfium2']},
    })
    counter_lock = threading.Lock()
    status = {'phase': 'indexing', 'started_at_utc': utc_now(), 'at_utc': utc_now(),
              'indexed_completed': 0, 'indexed_failed': 0, 'questions_completed': 0, 'questions_failed': 0}
    started_run = time.perf_counter()

    def checkpoint(**updates):
        with counter_lock:
            status.update(updates)
            status['at_utc'] = utc_now()
            status['current_invocation_seconds'] = round(time.perf_counter() - started_run, 3)
            write_json(out / 'status.json', status)

    checkpoint()
    for number, doc in enumerate(documents, 1):
        job_out = out / 'index' / hashlib.sha256(doc['file'].encode()).hexdigest()[:12]
        job_out.mkdir(parents=True, exist_ok=True)
        result_path = job_out / 'result.json'
        record = json.loads(result_path.read_text(encoding='utf-8')) if result_path.exists() else None
        if record and record['status'] in ('completed', 'failed'):
            status['indexed_' + record['status']] += 1
            checkpoint()
            continue
        existing = [d for d in client.list_documents(limit=10000)['documents'] if d['name'] == doc['file']]
        if existing:
            # Recover a save that completed just before a process interruption.
            record = {**doc, 'status': 'completed', 'doc_id': existing[0]['id'], 'recovered_existing_index': True,
                      'elapsed_seconds': None, **summarize_job(job_out)}
            write_json(result_path, record)
            status['indexed_completed'] += 1
            checkpoint()
            continue
        job = {'id': 'index:' + doc['file'], 'lane': 'index', 'model': cfg['index_model'], 'output': str(job_out)}
        token = JOB.set(job)
        audit.index_job = job
        record = {**doc, 'status': 'running', 'started_at_utc': utc_now()}
        write_json(result_path, record)
        checkpoint(current_document=doc['file'])
        print(f'INDEX_START {number}/{len(documents)} {doc["file"]} ({doc["pages"]} pages)', flush=True)
        started = time.perf_counter()
        try:
            result = client.submit_document(str(ROOT / 'documents/S' / doc['file']))
            tree = client.get_tree(result['doc_id'], node_summary=True, include_text=False)
            write_json(job_out / 'tree.json', tree)
            record.update(status='completed', doc_id=result['doc_id'], stored_name=result.get('name'), reported_usage=result.get('usage'))
        except Exception as exc:
            record.update(status='failed', error_type=type(exc).__name__, error=redact(exc, key))
        finally:
            record.update(elapsed_seconds=round(time.perf_counter() - started, 3), finished_at_utc=utc_now(), **summarize_job(job_out))
            write_json(result_path, record)
            status['indexed_' + record['status']] += 1
            checkpoint()
            audit.index_job = None
            JOB.reset(token)
            print(f'INDEX_{record["status"].upper()} {number}/{len(documents)} {record["elapsed_seconds"]}s {doc["file"]}', flush=True)
    library = client.list_documents(limit=10000)
    write_json(out / 'library.json', library)
    checkpoint(phase='questions', indexed_library_size=library['total'], current_document=None)
    write_json(out.parent / 'latest.json', {'run_directory': str(out), 'phase': 'questions'})

    def ask(question):
        job_out = out / 'questions' / question['id']
        job_out.mkdir(parents=True, exist_ok=True)
        path = job_out / 'result.json'
        if path.exists():
            record = json.loads(path.read_text(encoding='utf-8'))
            if record['status'] in ('completed', 'failed'):
                return record
        token = JOB.set({'id': 'chat:' + question['id'], 'lane': 'chat', 'model': cfg['chat_model'], 'output': str(job_out)})
        record = {**question, 'status': 'running', 'started_at_utc': utc_now(),
                  'available_documents': library['total'], 'source_hints': None, 'history': None}
        write_json(path, record)
        started = time.perf_counter()
        try:
            # Fresh client/context; no doc_id, source hint, custom prompt, reference answer, or prior question.
            response = new_client().chat(question['question'], protocol='responses', reasoning_effort='medium')
            answer = '\n'.join(part['text'] for item in response.get('output', []) if item.get('type') == 'message'
                               for part in item.get('content', []) if part.get('type') == 'output_text').strip()
            trace = [item for item in response.get('messages', []) if item.get('type') in ('message', 'function_call', 'function_call_output')]
            write_json(job_out / 'transcript.json', trace)
            record.update(answer=answer, response_status=response.get('status'), reported_usage=response.get('usage'))
            record['status'] = 'completed' if answer and response.get('status') == 'completed' else 'failed'
            if record['status'] == 'failed':
                record['error'] = 'No completed final answer.'
        except Exception as exc:
            record.update(status='failed', error_type=type(exc).__name__, error=redact(exc, key),
                          exception_usage=getattr(exc, 'usage', None))
        finally:
            record.update(elapsed_seconds=round(time.perf_counter() - started, 3), finished_at_utc=utc_now(), **summarize_job(job_out))
            write_json(path, record)
            JOB.reset(token)
        return record

    with ThreadPoolExecutor(max_workers=cfg['question_workers']) as pool:
        pending = {pool.submit(ask, q): q['id'] for q in queries}
        for future in as_completed(pending):
            record = future.result()
            with counter_lock:
                status['questions_' + record['status']] += 1
                checkpoint(last_question=record['id'])
                done = status['questions_completed'] + status['questions_failed']
            print(f'QUESTION_{record["status"].upper()} {done}/{len(queries)} {record["id"]} {record["elapsed_seconds"]}s sources={len(record["successfully_read_documents"])}', flush=True)
    checkpoint(phase='generation_completed', finished_at_utc=utc_now())
    write_json(out.parent / 'latest.json', {'run_directory': str(out), 'phase': 'generation_completed'})
    print('GENERATION_COMPLETED ' + str(out), flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--run-dir', required=True)
    parser.add_argument('--prepare', action='store_true')
    parser.add_argument('--credentials-container')
    args = parser.parse_args()
    out = (ROOT / args.run_dir).resolve()
    if not out.is_relative_to(ROOT / 'outputs/benchmark'):
        raise ValueError('Run directory must be inside outputs/benchmark.')
    if args.prepare:
        prepare(out)
    else:
        run(out, args.credentials_container)


if __name__ == '__main__':
    main()
