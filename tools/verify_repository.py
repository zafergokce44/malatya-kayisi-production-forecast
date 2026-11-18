#!/usr/bin/env python3
"""Static archive verification, without any access to restricted source datasets."""
from pathlib import Path
import hashlib, py_compile, sys
BASE=Path(__file__).resolve().parent.parent
manifest=BASE/'checksums.sha256'
errors=[]
count=0
for line in manifest.read_text(encoding='utf-8').splitlines():
    if not line.strip(): continue
    digest, rel = line.split('  ',1)
    file=BASE/rel
    if not file.is_file():
        errors.append(f'MISSING: {rel}')
        continue
    actual=hashlib.sha256(file.read_bytes()).hexdigest()
    if actual!=digest:
        errors.append(f'HASH MISMATCH: {rel}')
    count+=1
for rel in ['scripts/tezfinal.py','scripts/analiz_v2.py']:
    try:compile((BASE/rel).read_bytes(),str(BASE/rel),'exec')
    except SyntaxError as e:errors.append(f'INVALID SYNTAX: {rel}: {e}')
for p in BASE.rglob('*'):
    if p.suffix.lower() in {'.xlsx','.xls','.xlsm','.ods'}:
        errors.append(f'RESTRICTED SPREADSHEET FOUND: {p.relative_to(BASE)}')
if errors:
    print('ARCHIVE CHECK FAILED:')
    print('\n'.join(errors))
    sys.exit(1)
print(f'ARCHIVE STATIC CHECK OK: {count} files verified, 2 Python source files syntax-checked. No input spreadsheet included.')
print('This does not verify model execution, data rights, or exact numerical reproducibility.')
