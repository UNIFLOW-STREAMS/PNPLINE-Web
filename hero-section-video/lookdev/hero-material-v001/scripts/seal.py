import bpy,json,hashlib,shutil
from pathlib import Path
R=Path(__file__).resolve().parents[1];file=Path(bpy.data.filepath)
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
archive=R/'inputs/render-source-unpacked.blend';archive.parent.mkdir(exist_ok=True)
render_sha=digest(file);shutil.copyfile(file,archive)
fonts=[]
for f in bpy.data.fonts:
 if f.filepath=='<builtin>':continue
 path=Path(bpy.path.abspath(f.filepath));original=path.read_bytes();f.pack();assert hashlib.sha256(f.packed_file.data).hexdigest()==hashlib.sha256(original).hexdigest()
 fonts.append(dict(name=f.name,original_path=str(path),sha256=hashlib.sha256(original).hexdigest(),packed_bytes=len(f.packed_file.data),origin='Font already referenced by the accepted source blend'))
bpy.ops.wm.save_as_mainfile(filepath=str(file))
(R/'review/packaging.json').write_text(json.dumps(dict(render_source_sha256=render_sha,render_source_archive=str(archive),packed_file_sha256=digest(file),changes='Only embed byte-identical existing Arial Bold font; no shader, geometry, lighting, camera or animation edit.',fonts=fonts),indent=2))
print('SEALED',digest(file),flush=True)
