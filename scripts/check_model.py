"""Read-only availability check; does not generate text or store credentials."""
import argparse
import json
from pathlib import Path
import urllib.error
import urllib.parse
import urllib.request
from connection import load_connection, redact


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--credentials-container')
    parser.add_argument('--model', default='gpt-6-sol')
    parser.add_argument('--output', default='outputs/example/model_check.json')
    args = parser.parse_args()
    key, endpoint, previous_model = load_connection(args.credentials_container)
    request = urllib.request.Request(
        endpoint + '/models/' + urllib.parse.quote(args.model, safe=''),
        headers={'Authorization': 'Bearer ' + key},
    )
    record = {'requested_model': args.model, 'previous_container_default': previous_model,
              'endpoint_host': urllib.parse.urlsplit(endpoint).hostname}
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            body = json.load(response)
            record.update(http_status=response.status, returned_model=body.get('id'), available=True)
    except urllib.error.HTTPError as exc:
        detail = json.loads(exc.read().decode('utf-8'))
        record.update(http_status=exc.code, available=False, error=redact(detail.get('error', {}).get('message', ''), key))
    path = Path(__file__).resolve().parents[1] / args.output
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(record, indent=2))
    if not record['available']:
        raise SystemExit(2)


if __name__ == '__main__':
    main()
