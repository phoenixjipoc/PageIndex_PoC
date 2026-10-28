"""Observe provider settings and public tool traffic without recording secrets/reasoning."""
from contextvars import ContextVar
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import threading
import time

JOB = ContextVar('benchmark_job', default=None)


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def write_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    temporary.replace(path)


def read_jsonl(path):
    if not Path(path).exists():
        return []
    return [json.loads(line) for line in Path(path).read_text(encoding='utf-8').splitlines() if line.strip()]


class Audit:
    def __init__(self, key, instructions):
        self.key = key
        self.instructions = instructions
        self.index_job = None
        self.lock = threading.RLock()
        self.seen_responses = set()
        self.seen_tool_outputs = set()

    def append(self, job, filename, item):
        with self.lock:
            path = Path(job['output']) / filename
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open('a', encoding='utf-8') as stream:
                stream.write(json.dumps({'at_utc': utc_now(), **item}, ensure_ascii=False).replace(self.key, '[REDACTED]') + '\n')

    def job(self):
        job = JOB.get() or self.index_job
        if not job:
            raise RuntimeError('Provider call is missing its experiment job context.')
        return job

    def request(self, request):
        if request.method != 'POST' or not request.url.path.endswith(('/chat/completions', '/responses')):
            return
        job = self.job()
        body = json.loads(request.content)
        effort = body.get('reasoning_effort') or (body.get('reasoning') or {}).get('effort')
        item = {'lane': job['lane'], 'model': body.get('model'), 'reasoning_effort': effort,
                'host': request.url.host, 'path': request.url.path,
                'model_matches': body.get('model') == job['model'], 'effort_matches': effort == 'medium'}
        if job['lane'] == 'chat':
            supplied = body.get('instructions')
            item['official_instructions_match'] = supplied == self.instructions
            item['instructions_sha256'] = hashlib.sha256((supplied or '').encode()).hexdigest()
            for entry in body.get('input', []):
                if isinstance(entry, dict) and entry.get('type') == 'function_call_output':
                    identity = (job['id'], entry.get('call_id'))
                    with self.lock:
                        if identity in self.seen_tool_outputs:
                            continue
                        self.seen_tool_outputs.add(identity)
                    self.append(job, 'tool_trace.jsonl', {'event': 'tool_result', 'item': entry})
        self.append(job, 'requests.jsonl', item)
        if not item['model_matches'] or not item['effort_matches'] or item.get('official_instructions_match') is False:
            raise RuntimeError('Provider request violates frozen model/reasoning/prompt configuration.')

    def response(self, response, elapsed):
        job = self.job()
        body = response.model_dump(mode='json') if hasattr(response, 'model_dump') else dict(response)
        identity = (job['id'], body.get('id'))
        with self.lock:
            if identity in self.seen_responses:
                return
            self.seen_responses.add(identity)
        returned = body.get('model') or ''
        matches = returned == job['model'] or returned.startswith(job['model'] + '-')
        self.append(job, 'model_calls.jsonl', {
            'lane': job['lane'], 'response_id': body.get('id'), 'response_model': returned,
            'model_matches': matches, 'elapsed_seconds': round(elapsed, 4), 'usage': body.get('usage'),
            'status': body.get('status'),
        })
        if job['lane'] == 'chat':
            for entry in body.get('output', []):
                if entry.get('type') in ('message', 'function_call'):
                    self.append(job, 'tool_trace.jsonl', {'event': 'model_output', 'item': entry})
        if not matches:
            raise RuntimeError(f'Unexpected response model: {returned}')

    def install(self):
        import httpx
        import litellm
        from openai.resources.responses import AsyncResponses
        old_send, old_asend = httpx.Client.send, httpx.AsyncClient.send
        old_completion, old_acompletion = litellm.completion, litellm.acompletion
        old_response = AsyncResponses.create

        def send(client, request, *a, **kw):
            self.request(request)
            return old_send(client, request, *a, **kw)

        async def asend(client, request, *a, **kw):
            self.request(request)
            return await old_asend(client, request, *a, **kw)

        def completion(*a, **kw):
            started = time.perf_counter()
            response = old_completion(*a, **kw)
            self.response(response, time.perf_counter() - started)
            return response

        async def acompletion(*a, **kw):
            started = time.perf_counter()
            response = await old_acompletion(*a, **kw)
            self.response(response, time.perf_counter() - started)
            return response

        async def responses(resource, *a, **kw):
            started = time.perf_counter()
            response = await old_response(resource, *a, **kw)
            self.response(response, time.perf_counter() - started)
            return response

        httpx.Client.send, httpx.AsyncClient.send = send, asend
        litellm.completion, litellm.acompletion = completion, acompletion
        AsyncResponses.create = responses


def summarize_job(output):
    calls = read_jsonl(Path(output) / 'model_calls.jsonl')
    requests = read_jsonl(Path(output) / 'requests.jsonl')
    trace = read_jsonl(Path(output) / 'tool_trace.jsonl')
    usage = {'input_tokens': 0, 'output_tokens': 0, 'cached_input_tokens': 0,
             'cache_write_tokens': 0, 'reasoning_tokens': 0}
    for call in calls:
        u = call.get('usage') or {}
        usage['input_tokens'] += u.get('input_tokens', u.get('prompt_tokens', 0)) or 0
        usage['output_tokens'] += u.get('output_tokens', u.get('completion_tokens', 0)) or 0
        details = u.get('input_tokens_details') or u.get('prompt_tokens_details') or {}
        usage['cached_input_tokens'] += details.get('cached_tokens', 0) or 0
        usage['cache_write_tokens'] += details.get('cache_write_tokens', 0) or 0
        details = u.get('output_tokens_details') or u.get('completion_tokens_details') or {}
        usage['reasoning_tokens'] += details.get('reasoning_tokens', 0) or 0
    usage['total_tokens'] = usage['input_tokens'] + usage['output_tokens']
    tools = [t['item'] for t in trace if t['event'] == 'model_output' and t['item'].get('type') == 'function_call']
    results = {}
    for event in trace:
        if event['event'] != 'tool_result':
            continue
        item = event['item']
        payload = item.get('output')
        if isinstance(payload, list):
            payload = '\n'.join(p.get('text', '') for p in payload if isinstance(p, dict))
        try:
            results[item.get('call_id')] = json.loads(payload)
        except (TypeError, ValueError):
            results[item.get('call_id')] = {'unparsed': payload}
    reads = []
    for tool in tools:
        if tool.get('name') != 'get_page_content':
            continue
        try:
            args = json.loads(tool.get('arguments') or '{}')
        except ValueError:
            args = {}
        outcome = results.get(tool.get('call_id'))
        reads.append({'document': args.get('doc_name'), 'pages': args.get('pages'),
                      'success': bool(outcome and outcome.get('success') is True),
                      'call_id': tool.get('call_id')})
    return {'model_calls': len(calls), 'http_attempts': len(requests), 'observed_usage': usage,
            'response_models': sorted({c['response_model'] for c in calls}),
            'all_models_match': bool(calls) and all(c['model_matches'] for c in calls),
            'all_request_settings_match': bool(requests) and all(r['model_matches'] and r['effort_matches'] and r.get('official_instructions_match', True) for r in requests),
            'tool_calls': [{'name': t.get('name'), 'arguments': t.get('arguments')} for t in tools],
            'page_reads': reads,
            'successfully_read_documents': sorted({r['document'] for r in reads if r['success'] and r['document']})}
