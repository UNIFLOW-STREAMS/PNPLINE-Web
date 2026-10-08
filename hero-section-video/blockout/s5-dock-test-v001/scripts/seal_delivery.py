"""Hash a reviewed bundle and optionally copy to a new destination, never overwrite."""
import argparse,json,hashlib,shutil
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--destination');a=p.parse_args();root=Path(__file__).resolve().parents[1]
def allowed(p):return p.is_file() and '__pycache__' not in p.parts and p.suffix not in ['.blend1','.blend2','.pyc'] and p.name!='hashes.json'
files=sorted(p for p in root.rglob('*') if allowed(p));manifest={p.relative_to(root).as_posix():dict(sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size) for p in files}
(root/'hashes.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
if a.destination:
 dest=Path(a.destination)
 if dest.exists():raise ValueError('Destination exists; refusing overwrite')
 dest.mkdir(parents=True)
 for src in files+[root/'hashes.json']:
  out=dest/src.relative_to(root);out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,out)
 for name,entry in manifest.items():assert hashlib.sha256((dest/name).read_bytes()).hexdigest()==entry['sha256'],name
 print('DELIVERED',dest,'verified files',len(manifest))
else:print('SEALED',len(manifest),'files')
