#!/usr/bin/env python3
"""Refresh the committed Codex bundle from canonical skills and native MCP config."""
from pathlib import Path
import shutil
ROOT = Path(__file__).resolve().parents[1]
bundle = ROOT / 'plugins/shiprust-skills'
for source in (ROOT / 'skills').rglob('*'):
    if source.is_file() and '__pycache__' not in source.parts:
        target = bundle / source.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
shutil.copyfile(ROOT / 'configs/codex.mcp.json', bundle / '.mcp.json')
print('Refreshed Codex skill and MCP bundle; review git diff before committing.')
