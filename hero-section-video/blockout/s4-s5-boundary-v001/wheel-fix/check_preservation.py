import bpy,sys,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'));from preservation import action,sha
allowed={'A03_TRACTOR','A03_TRAILER','TRACTOR_CAB'}
allowed.update(o.name for o in bpy.data.objects if o.name.startswith('A03') and '_WHEEL_' in o.name)
rootchildren={o.name for n in ['A03_TRACTOR','A03_TRAILER'] for o in bpy.data.objects[n].children_recursive}
def capture():
 s=bpy.data.scenes['PNPLINE_MASTER_v005'];bpy.context.window.scene=s
 objects=sorted(s.objects,key=lambda o:o.name);static={}
 for o in objects:
  if o.name not in allowed:static[o.name]=sha([action(o.animation_data),o.parent.name if o.parent else None,list(o.location),list(o.scale),[[list(v.co) for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons]] if o.type=='MESH' else None])
 frames=[];later=[]
 for f in range(1393):
  s.frame_set(f)
  frames.append(sha([[o.name,[list(r) for r in o.matrix_world]] for o in objects if o.name not in allowed|rootchildren]+[s.camera.data.lens]))
  if f>=620:later.append(sha([[n,[list(r) for r in bpy.data.objects[n].matrix_world]] for n in ['A03_TRACTOR','A03_TRAILER']]))
 return dict(names=[o.name for o in objects],static=static,protected=frames,later=later)
bpy.ops.wm.open_mainfile(filepath=str(R/'wheel-fix/before-wheel-fix.blend'));bpy.data.scenes['PNPLINE_MASTER_v005'].frame_set(596);before=capture()
bpy.ops.wm.open_mainfile(filepath=str(R/'master-s4-s5-boundary-v001.blend'));bpy.data.scenes['PNPLINE_MASTER_v005'].frame_set(596);after=capture()
result={k:before[k]==after[k] for k in before};print(result)
(R/'wheel-fix/preservation.json').write_text(json.dumps(result,indent=2))
assert all(result.values()),result
