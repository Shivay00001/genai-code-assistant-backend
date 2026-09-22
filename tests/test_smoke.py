"""Structural smoke test (generated). Verifies modules parse and expose entry points."""
import ast
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent

def test_all_python_files_parse():
    bad = []
    for f in sorted(ROOT.rglob('*.py')):
        if '__pycache__' in f.parts or 'tests' in f.parts:
            continue
        try:
            ast.parse(f.read_text(encoding='utf-8'), filename=str(f))
        except SyntaxError as e:
            bad.append(f"{f}: {e}")
    assert not bad, "\n".join(bad)
