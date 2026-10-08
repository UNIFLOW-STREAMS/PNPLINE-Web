"""SHA256 inventory for the final handoff. Run after report/ledger edits."""
import hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
files=[p for p in R.rglob('*') if p.is_file() and p.name not in ['hashes.json'] and not p.name.endswith('.blend1') and '__pycache__' not in p.parts]
rows=[{'path':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(files)]
(R/'hashes.json').write_text(json.dumps({'algorithm':'SHA256','excludes':['hashes.json (self)','*.blend1','__pycache__'],'files':rows},indent=2),encoding='utf-8')
print('Hashed files:',len(rows))
