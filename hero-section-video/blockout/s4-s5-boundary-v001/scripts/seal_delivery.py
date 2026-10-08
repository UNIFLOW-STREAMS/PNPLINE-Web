"""Redact local user-home paths in logs, then hash delivered artifacts."""
import hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
home=str(Path.home());variants={home,home.replace('\\','/'),home.replace('\\','\\\\')}
for file in (R/'logs').glob('*'):
 if file.suffix not in {'.log','.txt','.json'}:continue
 try:content=file.read_text(encoding='utf-8-sig')
 except UnicodeError:continue
 for value in variants:content=content.replace(value,'<USER_HOME>')
 file.write_text(content,encoding='utf8')
hashes={str(file.relative_to(R)).replace('\\','/'):hashlib.sha256(file.read_bytes()).hexdigest() for file in sorted(R.rglob('*')) if file.is_file() and file.name!='hashes.json' and '__pycache__' not in file.parts}
(R/'hashes.json').write_text(json.dumps(hashes,indent=2),encoding='utf8');print('HASHED',len(hashes),'files')
