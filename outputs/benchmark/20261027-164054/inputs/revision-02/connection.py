"""Read an existing model connection without logging or persisting its secret."""
import json
import os
import subprocess
from urllib.parse import urlsplit


def load_connection(container=None):
    if container:
        result = subprocess.run(
            ['docker', 'inspect', '--format', '{{json .Config.Env}}', container],
            capture_output=True, text=True, timeout=20,
        )
        if result.returncode:
            raise RuntimeError('Cannot read the selected container configuration: ' + result.stderr.strip())
        source = dict(item.split('=', 1) for item in json.loads(result.stdout) if '=' in item)
        key = source.get('LLM_API_KEY', '')
        endpoint = source.get('LLM_BASE_URL', '')
        previous_model = source.get('LLM_MODEL_NAME', '')
    else:
        key = os.environ.get('OPENAI_API_KEY') or os.environ.get('LLM_API_KEY', '')
        endpoint = os.environ.get('OPENAI_BASE_URL') or os.environ.get('LLM_BASE_URL', 'https://api.openai.com/v1')
        previous_model = os.environ.get('LLM_MODEL_NAME', '')
    if not key or not endpoint:
        raise RuntimeError('An API key and endpoint must be configured before running the example.')
    parsed = urlsplit(endpoint)
    if parsed.scheme not in ('https', 'http') or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError('Invalid model endpoint')
    return key, endpoint.rstrip('/'), previous_model


def redact(text, key):
    return str(text).replace(key, '[REDACTED]') if key else str(text)
