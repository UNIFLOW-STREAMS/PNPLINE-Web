import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
paths=[p for p in ROOT.rglob('*') if p.is_file() and p.name!='hashes.json' and p.suffix not in ['.blend1','.pyc'] and '__pycache__' not in p.parts]
entries={p.relative_to(ROOT).as_posix():{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(paths)}
(ROOT/'hashes.json').write_text(json.dumps({'algorithm':'SHA256','status':'approved integrated master-v004; prior alternatives retained as history','files':entries},indent=2),encoding='utf-8')
assert all(hashlib.sha256((ROOT/n).read_bytes()).hexdigest()==v['sha256'] for n,v in entries.items())
print('Verified',len(entries),'file hashes')
