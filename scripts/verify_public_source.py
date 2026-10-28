"""Verify that the selected local PDF exactly matches its public publisher URL."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
NAME = 'CAJPA__28._Appendix_Z-Sample_Invest.pdf'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--document', default=NAME)
    parser.add_argument('--output', default='outputs/example/public_source_check.json')
    args = parser.parse_args()
    with (ROOT / 'documents/manifest_S.csv').open(encoding='utf-8-sig', newline='') as source:
        row = next(row for row in csv.DictReader(source) if row['file'] == args.document)
    local = (ROOT / 'documents/S' / args.document).read_bytes()
    request = urllib.request.Request(row['url'], headers={'User-Agent': 'PageIndex-PoC-public-source-check'})
    with urllib.request.urlopen(request, timeout=40) as response:
        public = response.read()
        final_url = response.url
        status = response.status
    record = {
        'file': args.document, 'public_source_url': row['url'], 'resolved_public_url': final_url,
        'http_status': status, 'public_download_without_authentication': True,
        'local_sha256': hashlib.sha256(local).hexdigest(),
        'public_sha256': hashlib.sha256(public).hexdigest(),
        'local_bytes': len(local), 'public_bytes': len(public),
        'byte_identical': local == public,
    }
    output = ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(record, indent=2))
    if local != public:
        raise SystemExit(2)


if __name__ == '__main__':
    main()
