import bpy,json,hashlib,time
from pathlib import Path
R=Path(__file__).resolve().parents[1];R.joinpath('review').mkdir(parents=True,exist_ok=True)
S=bpy.context.scene;old=R.parent/'white-cyan-study-v004';prev=json.loads((old/'study.json').read_text())
def sha(p):
 with open(p,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
assert sha(bpy.data.filepath)==prev['output_sha256']
def signature():
 return hashlib.sha256(repr([(o.name,o.parent.name if o.parent else None,tuple(tuple(row) for row in o.matrix_basis),o.data.name if o.data else None,o.hide_render) for o in S.objects]).encode()).hexdigest()
sig=signature();brand=bpy.data.materials['STUDY | landmark brand cyan'];changes=[];counts={}
allslots={(o.name,i):sl.material for o in S.objects for i,sl in enumerate(o.material_slots)}
roots=['PORT_COMPANION_CRANE_0','PORT_COMPANION_CRANE_1','CR_SLEW_JIB']
prefixes=('PORT_CRANE_CROSS','PORT_CRANE_BOOM','PORT_CRANE_PYLON','PORT_CRANE_STAY','PORT_CRANE_BACKSTAY','PORT_BOOM_TIE')
for rn in roots:
 count=0
 for o in S.objects[rn].children_recursive:
  if o.type not in {'MESH','CURVE'}:continue
  if rn!='CR_SLEW_JIB' and not o.name.startswith(prefixes):continue
  if any(k in o.name.lower() for k in ['glass','cable','bearing','hoist']):continue
  for i,sl in enumerate(o.material_slots):
   m=sl.material
   if not m or m.name in {'STUDY | glass','STUDY | rubber'}:continue
   sl.link='OBJECT';sl.material=brand;changes.append((rn,o.name,i,m.name,brand.name));count+=1
 counts[rn]=count
assert all(counts[rn]>0 for rn in roots)
keys={(n,i) for rn,n,i,a,b in changes}
assert all(S.objects[n].material_slots[i].material==m for (n,i),m in allslots.items() if (n,i) not in keys)
assert signature()==sig
out=R/'pnpline-white-cyan-study-v005.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out))
(R/'study.json').write_text(json.dumps(dict(source=prev['output'],source_sha256=prev['output_sha256'],output=str(out),output_sha256=sha(out),cranes=counts,changed_slots=changes,geometry_transform_signature=sig,scope='Three China port crane upper booms, pylons, stays and cross ties only; working crane upper machinery/cabin paint included. Lower legs, portal braces, bogies, cables and glazing unchanged. All non-target slots preserved.'),indent=2))
print('SAVED',out,counts,flush=True)
pref=bpy.context.preferences.addons['cycles'].preferences;pref.compute_device_type='OPTIX';pref.get_devices()
for d in pref.devices:d.use=d.type=='OPTIX'
S.render.engine='CYCLES';S.cycles.device='GPU';S.cycles.samples=40;S.cycles.use_denoising=True;S.render.use_persistent_data=True;S.render.resolution_percentage=100;S.render.resolution_x=1600;S.render.resolution_y=900;S.render.use_border=False;S.render.image_settings.file_format='PNG';S.render.image_settings.color_mode='RGB';S.render.image_settings.color_depth='8'
S.frame_set(132);S.render.filepath=str(R/'review/after-0132.png');t=time.time();bpy.ops.render.render(write_still=True)
(R/'review/render.json').write_text(json.dumps(dict(frame=132,camera=S.camera.name,seconds=time.time()-t),indent=2))
