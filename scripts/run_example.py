"""Run one local PageIndex example. Never reads standards or reference answers."""
import argparse
from datetime import datetime, timezone, timedelta
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import sys
import threading
import time
from urllib.parse import urlsplit

from connection import load_connection, redact

ROOT = Path(__file__).resolve().parents[1]
PDF_NAME = 'CAJPA__28._Appendix_Z-Sample_Invest.pdf'
QUESTION_ID = 'INV-01'


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--credentials-container')
    parser.add_argument('--model', help='Optional override for both models.')
    parser.add_argument('--index-model', default='gpt-6-luna')
    parser.add_argument('--chat-model', default='gpt-6-sol')
    parser.add_argument('--document', default=PDF_NAME)
    parser.add_argument('--question-id', default=QUESTION_ID)
    parser.add_argument('--reasoning-effort', default='medium')
    parser.add_argument('--index-reasoning-effort')
    parser.add_argument('--chat-reasoning-effort')
    args = parser.parse_args()
    models = {'index': args.model or args.index_model, 'chat': args.model or args.chat_model}
    efforts = {'index': args.index_reasoning_effort or args.reasoning_effort,
               'chat': args.chat_reasoning_effort or args.reasoning_effort}
    key, endpoint, previous_model = load_connection(args.credentials_container)
    os.environ['OPENAI_API_KEY'] = key
    os.environ['OPENAI_BASE_URL'] = endpoint
    os.environ['OPENAI_AGENTS_DISABLE_TRACING'] = '1'
    os.environ['HF_HOME'] = str(ROOT / '.cache' / 'huggingface')
    os.environ['TIKTOKEN_CACHE_DIR'] = str(ROOT / '.cache' / 'tiktoken')
    os.environ['LITELLM_LOCAL_MODEL_COST_MAP'] = 'True'

    print('Loading local PageIndex runtime...', flush=True)
    from pageindex import PageIndexClient
    from pageindex.local_chat import CHAT_HEADER
    from pageindex.utils import SUMMARY_CONCURRENCY
    import litellm
    import httpx
    from openai.resources.responses import AsyncResponses
    from PyPDF2 import PdfReader

    run_id = datetime.now(timezone(timedelta(hours=8))).strftime('%Y%m%d-%H%M%S')
    output = ROOT / 'outputs' / 'example' / run_id
    output.mkdir(parents=True, exist_ok=False)
    storage = ROOT / '.pageindex' / ('example-' + run_id)
    pdf = ROOT / 'documents' / 'S' / args.document
    query = next(row['question'] for row in json.loads((ROOT / 'questions/queries.json').read_text(encoding='utf-8')) if row['id'] == args.question_id)
    source = json.loads((ROOT / 'pageindex_source.json').read_text(encoding='utf-8'))
    record = {
        'status': 'started', 'run_id': run_id, 'scope': 'single_document_smoke_test',
        'question_id': args.question_id, 'question': query, 'document': args.document,
        'pdf_sha256': hashlib.sha256(pdf.read_bytes()).hexdigest(),
        'pdf_pages': len(PdfReader(pdf).pages), 'models_requested': models,
        'previous_container_default': previous_model, 'endpoint_host': urlsplit(endpoint).hostname,
        'pageindex_version': importlib.metadata.version('pageindex'), 'source_commit': source['commit'],
        'python_version': sys.version.split()[0], 'index_mode': 'flash',
        'index_reasoning_effort': efforts['index'], 'chat_protocol': 'responses', 'chat_reasoning_effort': efforts['chat'],
        'max_chat_turns': 10, 'summary_concurrency': SUMMARY_CONCURRENCY,
        'backend_timeout_override': None, 'backend_retries_override': None,
        'max_output_tokens_override': None, 'citations_option': False,
        'custom_instructions_supplied': False,
        'index_storage': str(storage), 'reference_answers_used_in_generation': False,
        'routing_note': 'The source document is supplied for this smoke test; this is not whole-corpus retrieval.',
        'instruction_note': 'Official default agent instructions only. No custom instructions or optional citation prompt.',
    }
    write_json(output / 'result.json', record)
    write_json(ROOT / 'outputs/example/latest.json', {'run_directory': str(output), 'status': 'started'})
    calls = []
    wire_requests = []
    lock = threading.Lock()
    phase = 'index'
    expected_chat_instructions = None

    def note_request(request):
        if request.method != 'POST' or request.url.path not in ('/v1/chat/completions', '/v1/responses'):
            return
        payload = json.loads(request.content)
        effort = payload.get('reasoning_effort') or (payload.get('reasoning') or {}).get('effort')
        item = {'lane': phase, 'endpoint_host': request.url.host, 'path': request.url.path,
                'requested_model': payload.get('model'), 'reasoning_effort': effort,
                'model_matches': payload.get('model') == models[phase],
                'reasoning_matches': effort == efforts[phase]}
        if phase == 'chat':
            item['official_instructions_match'] = payload.get('instructions') == expected_chat_instructions
        with lock:
            wire_requests.append(item)
            with (output / 'wire_requests.jsonl').open('a', encoding='utf-8') as log:
                log.write(json.dumps(item) + '\n')
        if not item['model_matches'] or not item['reasoning_matches']:
            raise RuntimeError(f'Outbound model/reasoning settings differ from the requested {phase} configuration: {item}')
        if phase == 'chat' and not item['official_instructions_match']:
            raise RuntimeError('Outbound instructions differ from the official default agent instructions.')

    def note_response(lane, response, elapsed, requested):
        body = response.model_dump(mode='json') if hasattr(response, 'model_dump') else dict(response)
        returned = body.get('model', '')
        normalized_requested = requested.removeprefix('openai/') if isinstance(requested, str) else requested
        good = normalized_requested == models[lane] and (returned == models[lane] or returned.startswith(models[lane] + '-'))
        item = {'lane': lane, 'requested_model': requested, 'response_model': returned,
                'model_matches': good, 'elapsed_seconds': round(elapsed, 3), 'usage': body.get('usage'),
                'response_id': body.get('id')}
        with lock:
            calls.append(item)
            with (output / 'model_calls.jsonl').open('a', encoding='utf-8') as log:
                log.write(json.dumps(item, ensure_ascii=False) + '\n')
        if not good:
            raise RuntimeError(f'Model mismatch: requested {models[lane]}, received {returned}')

    # Instrument public SDK calls for response-model and usage checks only.
    # Prompts, headers and API keys are never logged by these hooks.
    original_completion = litellm.completion
    original_acompletion = litellm.acompletion
    original_responses_create = AsyncResponses.create
    original_http_send = httpx.Client.send
    original_async_http_send = httpx.AsyncClient.send

    def http_send(client, request, *a, **kw):
        note_request(request)
        return original_http_send(client, request, *a, **kw)

    async def async_http_send(client, request, *a, **kw):
        note_request(request)
        return await original_async_http_send(client, request, *a, **kw)

    def completion(*a, **kw):
        started = time.perf_counter()
        response = original_completion(*a, **kw)
        note_response('index', response, time.perf_counter() - started, kw.get('model'))
        return response

    async def acompletion(*a, **kw):
        started = time.perf_counter()
        response = await original_acompletion(*a, **kw)
        note_response('index', response, time.perf_counter() - started, kw.get('model'))
        return response

    async def responses_create(resource, *a, **kw):
        started = time.perf_counter()
        response = await original_responses_create(resource, *a, **kw)
        note_response('chat', response, time.perf_counter() - started, kw.get('model'))
        return response

    litellm.completion = completion
    litellm.acompletion = acompletion
    AsyncResponses.create = responses_create
    httpx.Client.send = http_send
    httpx.AsyncClient.send = async_http_send
    started_all = time.perf_counter()
    try:
        client = PageIndexClient(
            index={
                'model': models['index'], 'storage_path': str(storage),
                'summary_reasoning_effort': efforts['index'],
                'backend': {'api_key': key, 'api_base': endpoint, 'reasoning_effort': efforts['index']},
            },
            chat={'model': models['chat'], 'backend': {'api_key': key, 'base_url': endpoint}},
        )
        expected_chat_instructions = '\n\n'.join([CHAT_HEADER, client.agent_instructions()])
        (output / 'official_chat_instructions.txt').write_text(expected_chat_instructions + '\n', encoding='utf-8')
        record['official_chat_instructions_sha256'] = hashlib.sha256(expected_chat_instructions.encode('utf-8')).hexdigest()
        print(f'INDEX_START {args.document} ({record["pdf_pages"]} pages); {models["index"]}, effort={efforts["index"]}', flush=True)
        started_index = time.perf_counter()
        submitted = client.submit_document(str(pdf))
        record['index_seconds'] = round(time.perf_counter() - started_index, 3)
        record['index_usage'] = submitted.get('usage')
        record['doc_id'] = submitted['doc_id']
        record['stored_document_name'] = submitted.get('name')
        write_json(output / 'tree.json', client.get_tree(submitted['doc_id'], node_summary=True, include_text=False))
        record['status'] = 'indexed'
        write_json(output / 'result.json', record)
        print(f'INDEX_DONE {record["index_seconds"]} seconds', flush=True)
        print(f'QUESTION {args.question_id}: {query}', flush=True)
        phase = 'chat'
        started_chat = time.perf_counter()
        response = client.chat(
            query, doc_id=submitted['doc_id'], protocol='responses',
            reasoning_effort=efforts['chat'],
        )
        record['chat_seconds'] = round(time.perf_counter() - started_chat, 3)
        record['chat_usage'] = response.get('usage')
        record['response_status'] = response.get('status')
        answer_parts = []
        for item in response.get('output', []):
            if item.get('type') == 'message':
                answer_parts.extend(part['text'] for part in item.get('content', []) if part.get('type') == 'output_text')
        answer = '\n'.join(answer_parts).strip()
        record['answer'] = answer
        # Save evidence/tool traffic and final answer, excluding reasoning items.
        transcript = [item for item in response.get('messages', []) if item.get('type') in ('function_call', 'function_call_output', 'message')]
        write_json(output / 'tool_trace.json', transcript)
        record['citations'] = client.get_citations(answer)
        record['tool_calls'] = [{'name': item.get('name'), 'arguments': item.get('arguments')} for item in transcript if item.get('type') == 'function_call']
        record['model_response_ids'] = sorted({call['response_model'] for call in calls})
        record['model_call_count'] = len(calls)
        record['all_models_match'] = bool(calls) and all(call['model_matches'] for call in calls)
        record['wire_request_count'] = len(wire_requests)
        record['all_wire_settings_match'] = bool(wire_requests) and all(r['model_matches'] and r['reasoning_matches'] for r in wire_requests)
        record['all_chat_requests_use_official_instructions'] = any(r['lane'] == 'chat' for r in wire_requests) and all(r.get('official_instructions_match', True) for r in wire_requests)
        if record['response_status'] != 'completed' or not answer:
            raise RuntimeError('The example did not produce a completed answer.')
        for lane in models:
            observed = sum(call['lane'] == lane for call in calls)
            requests = sum(request['lane'] == lane for request in wire_requests)
            if not observed or requests < observed:
                raise RuntimeError(f'Incomplete {lane} model/request observation: {observed} responses, {requests} requests.')
        record['status'] = 'completed'
        print('ANSWER ' + answer, flush=True)
        print('CITATIONS ' + json.dumps(record['citations'], ensure_ascii=False), flush=True)
    except (Exception, KeyboardInterrupt) as exc:
        record['status'] = 'failed'
        record['error_type'] = type(exc).__name__
        record['error'] = redact(exc, key)
        record['model_call_count'] = len(calls)
        print('FAILED ' + record['error_type'] + ': ' + record['error'], flush=True)
    finally:
        record['total_seconds'] = round(time.perf_counter() - started_all, 3)
        write_json(output / 'result.json', record)
        write_json(ROOT / 'outputs/example/latest.json', {'run_directory': str(output), 'status': record['status']})
        print('RESULT ' + str(output / 'result.json'), flush=True)
    if record['status'] != 'completed':
        raise SystemExit(1)


if __name__ == '__main__':
    main()
