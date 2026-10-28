"""Fetch a pinned upstream source archive without modifying the input dataset."""
import hashlib
import io
import json
from pathlib import Path
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
REVISION = 'e38b40ebaeea26d2c7206b80ce7bc9bf2935cdec'
URL = f'https://codeload.github.com/VectifyAI/PageIndex/zip/{REVISION}'


def main():
    target = ROOT / 'vendor' / 'PageIndex'
    if target.exists():
        raise SystemExit('Upstream source already exists; will not overwrite it.')
    request = urllib.request.Request(URL, headers={'User-Agent': 'PageIndex-PoC'})
    with urllib.request.urlopen(request, timeout=90) as response:
        archive = response.read()
    with zipfile.ZipFile(io.BytesIO(archive)) as bundle:
        prefix = f'PageIndex-{REVISION}/'
        for member in bundle.infolist():
            if not member.filename.startswith(prefix):
                raise ValueError('Unexpected archive root')
            relative = member.filename[len(prefix):]
            if not relative:
                continue
            output = (target / relative).resolve()
            if not output.is_relative_to(target.resolve()):
                raise ValueError('Unsafe archive path')
            if member.is_dir():
                output.mkdir(parents=True, exist_ok=True)
            else:
                output.parent.mkdir(parents=True, exist_ok=True)
                output.write_bytes(bundle.read(member))
    manifest = {
        'repository': 'https://github.com/VectifyAI/PageIndex',
        'commit': REVISION,
        'archive_url': URL,
        'archive_sha256': hashlib.sha256(archive).hexdigest(),
        'source_directory': 'vendor/PageIndex',
    }
    (ROOT / 'pageindex_source.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(manifest, indent=2))


if __name__ == '__main__':
    main()
