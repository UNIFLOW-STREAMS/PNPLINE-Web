from pathlib import Path
import hashlib,re
def output_directory(root,kind,label):
 root=Path(root).resolve()
 if kind not in {'review','preview'} or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]*',label):raise ValueError('Unsafe render label or directory')
 p=(root/kind/label).resolve()
 if not p.is_relative_to(root/kind):raise ValueError('Render directory escapes task')
 p.mkdir(parents=True,exist_ok=False)
 return p
def guard(root,output,base,expected_hash):
 root=Path(root).resolve();output=Path(output).resolve();base=Path(base).resolve()
 if not output.is_relative_to(root) or output.is_relative_to(root/'inputs') or output==base:
  raise ValueError('Output must remain inside task directory, outside immutable inputs')
 if output.exists():raise FileExistsError('Refusing existing output: '+str(output))
 if not base.is_file():raise ValueError('Missing base')
 if expected_hash and hashlib.sha256(base.read_bytes()).hexdigest()!=expected_hash:raise ValueError('Base hash mismatch')
 return output
