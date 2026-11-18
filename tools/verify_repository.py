#!/usr/bin/env python3
"""Verify repository file hashes and static source integrity; does NOT run ML models."""
from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / 'checksums.sha256'
SCRIPTS = [
    'scripts/tezfinal.py',
    'scripts/analiz_v2.py',
    'scripts/nested_cv_reconstruction.py',
    'scripts/ilkbahar_min_reconstruction.py',
]
ERRORS = []

if not MANIFEST.is_file():
    ERRORS.append('CHECKSUM MANIFEST MISSING')
else:
    for line in MANIFEST.read_text(encoding='utf-8').splitlines():
        if not line.strip():
            continue
        if '  ' not in line:
            ERRORS.append('INVALID CHECKSUM LINE: '+line[:90]); continue
        digest, rel = line.split('  ', 1)
        path = ROOT / rel
        if not path.is_file() or path.is_symlink():
            ERRORS.append('MISSING OR LINKED: '+rel); continue
        if hashlib.sha256(path.read_bytes()).hexdigest()!=digest:
            ERRORS.append('HASH MISMATCH: '+rel)

if not (ROOT/'LICENSE').is_file():
    ERRORS.append('LICENSE FILE MISSING')
for rel in SCRIPTS:
    path=ROOT/rel
    if not path.is_file():
        ERRORS.append('SOURCE MISSING: '+rel); continue
    try:
        compile(path.read_bytes(), str(path), 'exec')
    except SyntaxError as e:
        ERRORS.append(f'SYNTAX ERROR: {rel}: {e}')

ipynb=ROOT/'notebooks/tezfinal.ipynb'
if ipynb.is_file():
    try:
        notebook=json.loads(ipynb.read_text(encoding='utf8'))
        if not isinstance(notebook.get('cells'),list) or not notebook.get('nbformat'):
            ERRORS.append('NOTEBOOK JSON INVALID STRUCTURE')
    except (ValueError,UnicodeDecodeError) as e:
        ERRORS.append('NOTEBOOK JSON INVALID: '+str(e))

for suffix in ('.xlsx','.xls','.xlsm','.ods'):
    for path in ROOT.rglob('*'+suffix):
        ERRORS.append('SOURCE WORKBOOK PRESENT: '+str(path.relative_to(ROOT)))
for path in (ROOT/'data').rglob('*'):
    if path.is_file() and path.name!='README.md':
        ERRORS.append('UNEXPECTED FILE UNDER DATA/: '+str(path.relative_to(ROOT)))

if ERRORS:
    print('ARCHIVE STATIC CHECK FAILED')
    print('\n'.join(' - '+e for e in ERRORS))
    sys.exit(1)
print('ARCHIVE STATIC CHECK OK')
print(f' SHA-256 records: {sum(1 for x in MANIFEST.read_text().splitlines() if x.strip())}')
print(f' Python sources: {len(SCRIPTS)} syntax checked')
print(' Source Excel files: none; LICENSE present; notebook JSON valid')
print(' NOTE: this is NOT an independent reproduction of model metrics or a data-rights audit.')
