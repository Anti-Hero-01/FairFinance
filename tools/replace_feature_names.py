#!/usr/bin/env python3
"""Safe utility to find and optionally replace feature_* tokens with friendly names.

Usage:
  python tools/replace_feature_names.py --dry-run
  python tools/replace_feature_names.py --apply

This script creates a .bak copy before writing changes when --apply is used.
"""
import argparse
import os
import io
from pathlib import Path

FEATURE_NAME_MAP = [
    'age',
    'monthly_income',
    'credit_score',
    'employment_years',
    'credit_history_length',
    'debt_to_income_ratio',
    'number_of_accounts',
    'number_of_defaults',
    'loan_amount',
    'region',
    'gender',
]

REPO_ROOT = Path(__file__).resolve().parents[1]

EXT_SKIP = {'.png', '.jpg', '.jpeg', '.gif', '.gz', '.zip', '.tar', '.bz2', '.whl', '.pyc', '.pkl', '.db'}
DIR_SKIP = {'node_modules', '.git', '__pycache__', 'venv', 'dist'}

def build_map():
    m = {}
    for i, name in enumerate(FEATURE_NAME_MAP):
        key = f'feature_{i}'
        m[key] = name
        # also map quoted variants
        m[f'"{key}"'] = f'"{name}"'
        m[f"'{key}'"] = f"'{name}'"
    return m

def is_text_file(path: Path) -> bool:
    try:
        with open(path, 'rb') as f:
            chunk = f.read(4096)
            if b'\0' in chunk:
                return False
    except Exception:
        return False
    return True

def scan_and_replace(dry_run=True):
    mapping = build_map()
    total_matches = 0
    files_changed = 0
    results = []

    for root, dirs, files in os.walk(REPO_ROOT):
        # skip dirs
        dirs[:] = [d for d in dirs if d not in DIR_SKIP]
        for fname in files:
            path = Path(root) / fname
            if path.suffix.lower() in EXT_SKIP:
                continue
            if not is_text_file(path):
                continue
            try:
                text = path.read_text(encoding='utf-8')
            except Exception:
                continue

            file_matches = 0
            new_text = text
            for old, new in mapping.items():
                if old in new_text:
                    count = new_text.count(old)
                    file_matches += count
                    new_text = new_text.replace(old, new)

            if file_matches:
                total_matches += file_matches
                results.append((str(path.relative_to(REPO_ROOT)), file_matches))
                if not dry_run:
                    bak = path.with_suffix(path.suffix + '.bak')
                    if not bak.exists():
                        path.rename(bak)
                        bak.write_text(text, encoding='utf-8')
                        path.write_text(new_text, encoding='utf-8')
                        files_changed += 1
                    else:
                        # if .bak exists, do not overwrite backups; write directly
                        path.write_text(new_text, encoding='utf-8')
                        files_changed += 1

    return total_matches, files_changed, results

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--apply', action='store_true', help='Apply replacements (writes files, creates .bak)')
    p.add_argument('--dry-run', action='store_true', help='Only show matches (default)')
    args = p.parse_args()
    dry = not args.apply
    print('Repo root:', REPO_ROOT)
    print('Dry run:' if dry else 'Applying replacements:')
    total, changed, results = scan_and_replace(dry_run=dry)
    if results:
        print('\nFiles with matches:')
        for fp, cnt in results:
            print(f' - {fp}: {cnt} matches')
    else:
        print('No matches found.')
    print(f'\nTotal matches: {total}')
    if not dry:
        print(f'Files modified: {changed}')

if __name__ == '__main__':
    main()
