import bpy,json,hashlib,time
from pathlib import Path
R=Path(__file__).resolve().parents[1];R.joinpath('review').mkdir(parents=True,exist_ok=True)
S=bpy.context.scene;old=R.parent/'white-cyan-study-v003';prev=json.loads((old/'study.json').read_text())
def sha(p):
 with open(p,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
assert sha(bpy.data.filepath)==prev['output_sha256']
def signature():
 return hashlib.sha256(repr([(o.name,o.parent.name if o.parent else None,tuple(tuple(row) for row in o.matrix_basis),o.data.name if o.data else None,o.hide_render) for o in S.objects]).encode()).hexdigest()
sig=signature();brand=bpy.data.materials['STUDY | landmark brand cyan'];glass=bpy.data.materials['STUDY | glass'].copy();glass.name='STUDY | landmark cyan glazing';color=brand.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value[:];glass.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=color;glass.diffuse_color=color
changed=[]
for rootname in ['SF_TALLEST_TOWER','CNX_GZ_CANTON_ROOT']:
 root=S.objects[rootname]
 for o in root.children_recursive:
  if o.type not in {'MESH','CURVE'}:continue
  if any(k in o.name.lower() for k in ['paving','terrace','foundation','base_platform','pedestal']):continue
  for i,sl in enumerate(o.material_slots):
   m=sl.material
   if not m:continue
   if m.name=='STUDY | glass':new=glass
   elif m.name in {'STUDY | porcelain','STUDY | metal'}:new=brand
   elif m.name=='STUDY | roof' and not any(k in o.name.lower() for k in ['roof','tile']):new=brand
   else:continue
   changed.append((rootname,o.name,i,m.name,new.name));sl.link='OBJECT';sl.material=new
assert signature()==sig
assert any(x[0]=='SF_TALLEST_TOWER' for x in changed)
assert any(x[0]=='CNX_GZ_CANTON_ROOT' for x in changed)
out=R/'pnpline-white-cyan-study-v004.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out))
(R/'study.json').write_text(json.dumps(dict(source=prev['output'],source_sha256=prev['output_sha256'],output=str(out),output_sha256=sha(out),changed_slots=changed,geometry_transform_signature=sig,scope='Only Shanghai Tower and Canton Tower material slots. Cyan glass keeps v002 glass roughness, metallic and coat. All other material slots unchanged.'),indent=2))
print('SAVED',out,'slots',len(changed),flush=True)
pref=bpy.context.preferences.addons['cycles'].preferences;pref.compute_device_type='OPTIX';pref.get_devices()
for d in pref.devices:d.use=d.type=='OPTIX'
S.render.engine='CYCLES';S.cycles.device='GPU';S.cycles.samples=40;S.cycles.use_denoising=True;S.render.use_persistent_data=True;S.render.resolution_percentage=100;S.render.resolution_x=1600;S.render.resolution_y=900;S.render.use_border=False;S.render.image_settings.file_format='PNG';S.render.image_settings.color_mode='RGB';S.render.image_settings.color_depth='8'
S.frame_set(132);S.render.filepath=str(R/'review/after-0132.png');t=time.time();bpy.ops.render.render(write_still=True)
(R/'review/render.json').write_text(json.dumps(dict(frame=132,camera=S.camera.name,seconds=time.time()-t),indent=2))
