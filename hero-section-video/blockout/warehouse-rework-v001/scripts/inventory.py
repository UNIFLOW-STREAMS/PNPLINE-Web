"""Record immutable deliverables and reproducibility inputs after verification."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1]
files=[]
for p in sorted(R.rglob('*')):
 if not p.is_file() or '__pycache__' in p.parts or p.name=='inventory.json' or p.name.startswith('server.'):continue
 with p.open('rb') as stream:sha=hashlib.file_digest(stream,'sha256').hexdigest()
 files.append({'path':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':sha})
(R/'inventory.json').write_text(json.dumps({'final_model':'candidate-warehouse-v008.blend','excluded':'Live server logs/pid, Python cache, and this self-referential inventory. Intermediate candidates retained for audit.','files':files},indent=2))
print(f'Inventoried {len(files)} files.')
