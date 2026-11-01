import bpy,sys,math,json,numpy as np
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1]
B=R.parents[1]/'blockout'
sys.path[:0]=[str(R.parent/'us-warehouse-curvature-v001/scripts'),str(B/'curvature-rework-v001/scripts'),str(R.parent/'container-ship-v001/scripts')]
from surface_site import sphere,arc,basis
S=bpy.context.scene
U=S.objects['US_FRAME']
def flat(p):return arc(np.array(U.matrix_world.inverted()@Vector(p)))
def loc(o):return flat(o.matrix_world.translation).round(3).tolist()
o=S.objects['Figure Pack | surface anchor'];pt=np.array([55.36,31.52,1.86]);a=Matrix(basis(sphere,pt).tolist()).to_4x4();a.translation=Vector(sphere(pt))
o.matrix_parent_inverse=o.parent.matrix_world.inverted()@U.matrix_world@a@Matrix.Rotation(1.04,4,'Z')
bpy.context.view_layer.update()

import hashlib
p=R/'review/build.json';report=json.loads(p.read_text())
out=Path(bpy.data.filepath)
assert str(out)==report['output'] and hashlib.sha256(out.read_bytes()).hexdigest()==report['sha_result']
assert sum(1 for o in S.objects if o.name.startswith('Figure ') and 'Work shirt, vest and face' in o.name)==3
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
report['sha_result']=hashlib.sha256(out.read_bytes()).hexdigest()
report['packing_workstation_position']=[55.36,31.52,1.86]
p.write_text(json.dumps(report,indent=2))
