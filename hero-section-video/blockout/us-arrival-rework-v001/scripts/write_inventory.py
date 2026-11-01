"""Inventory saved artifacts without modifying inputs or intermediate candidates."""
from pathlib import Path
import json,hashlib,collections
R=Path(__file__).resolve().parents[1];output=R/'files-v010.json';rows=[]
for p in sorted(R.rglob('*')):
 if not p.is_file() or p==output or '__pycache__' in p.parts:continue
 rows.append({'path':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
deps=[]
for name in ['build_city.py','verify_preservation.py','safety.py']:
 p=R.parent/'us-city-concept-v001/scripts'/name
 deps.append({'path':str(p.relative_to(R.parent)).replace('\\','/'),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
output.write_text(json.dumps({'candidate':'candidate-arrival-v010.blend','scope':'All retained files in this task directory except this inventory and Python cache. Intermediate versions are historical, not final acceptance evidence.','dependencies_relative_to_blockout':deps,'files':rows},indent=2))
print('INVENTORY',len(rows),'files;',sum(r['bytes'] for r in rows),'bytes')
