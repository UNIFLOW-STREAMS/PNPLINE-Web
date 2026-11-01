import bpy,json,hashlib,random,re,time,importlib.util
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1]; R.joinpath('review').mkdir(parents=True,exist_ok=True)
S=bpy.context.scene; source=R.parent/'white-cyan-study-v002'; previous=json.loads((source/'study.json').read_text())
def sha(p):
 with open(p,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
assert sha(bpy.data.filepath)==previous['output_sha256']
def sig():
 return hashlib.sha256(repr([(o.name,o.parent.name if o.parent else None,tuple(tuple(row) for row in o.matrix_basis),o.data.name if o.data else None,o.hide_render) for o in S.objects]).encode()).hexdigest()
before_sig=sig(); provenance={(n,i):m for n,i,m,role in json.loads((R.parent/'white-cyan-study-v001/study.json').read_text())['assignments']}
groups=[(['SF_SPHERE_TOWER','SF_OPEN_TOWER','SF_STEP_TOWER','SF_TALLEST_TOWER'],2),(['CNX_BJ_PALACE_ROOT','CNX_BJ_HEAVEN_ROOT','CNX_BJ_CCTV_ROOT','CNX_BJ_ZUN_ROOT','CNX_BJ_STADIUM_ROOT','CNX_BJ_GREAT_WALL_ROOT'],3),(['CNX_GZ_LINGNAN_ROOT','CNX_GZ_PAGODA_ROOT','CNX_GZ_CANTON_ROOT','CNX_GZ_IFC_ROOT','CNX_GZ_CTF_ROOT','CNX_GZ_FACETED_ROOT','CNX_GZ_SHELLS_ROOT'],4),(['USD_EMPIRE_ROOT','USD_ONEWTC_ROOT','UC_LIBERTY_BODY','UC_AR_CIVIC_GROUP'],2)]
rng=random.Random(20261102); selected=[n for pool,count in groups for n in rng.sample(pool,count)]
accent=bpy.data.materials['STUDY | cyan'].copy();accent.name='STUDY | landmark brand cyan';p=accent.node_tree.nodes.get('Principled BSDF');p.inputs['Roughness'].default_value=.42;p.inputs['Metallic'].default_value=.05
accent['random_seed']=20261102;accent['note']='Fixed selection per landmark; no animated shader random value.'
changed=[]; original_slots=[];counts={}
protected_names={'STUDY | glass','STUDY | architectural slate','STUDY | light industrial roof','WHE | Low iron observation glass','Pacific | painted swells and aerated wake','SF_water','SF_wave','CNX_water'}
protected={(o.name,i):sl.material for o in S.objects for i,sl in enumerate(o.material_slots) if sl.material and sl.material.name in protected_names}
for rootname in selected:
 root=S.objects[rootname];count=0
 for o in root.children_recursive:
  if o.type not in {'MESH','CURVE','FONT'}:continue
  name=o.name.lower()
  if any(k in name for k in ['paving','terrace','pedestal','plinth','island','garden','grass','lawn','plaza','tree','foundation','ground','stair','_step','flag','roof','dome','cornice','base_platform']):continue
  # Civic wings combine wall and roof faces in a single material slot.
  # Accent the separate column/drum pieces so its roof and grounds stay neutral.
  if rootname=='UC_AR_CIVIC_GROUP' and not any(k in name for k in ['column','drum','side_lintel']):continue
  for i,sl in enumerate(o.material_slots):
   mat=sl.material;old=provenance.get((o.name,i),'').lower()
   if not mat or mat.name not in {'STUDY | porcelain','STUDY | limestone','STUDY | metal'}:continue
   if any(k in old for k in ['glazed','ceramic','roof','tile','ridge','marble','paving','ochre']):continue
   original_slots.append((o,i,mat));sl.link='OBJECT';sl.material=accent;changed.append((rootname,o.name,i,mat.name,accent.name));count+=1
 counts[rootname]=count
assert all(S.objects[n].material_slots[i].material==m for (n,i),m in protected.items())
assert sig()==before_sig
out=R/'pnpline-white-cyan-study-v003.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out))
(R/'study.json').write_text(json.dumps(dict(source=previous['output'],source_sha256=previous['output_sha256'],output=str(out),output_sha256=sha(out),random_seed=20261102,selected_landmarks=selected,changed_slots=changed,landmark_slot_counts=counts,geometry_transform_signature=before_sig,protected_slots_unchanged=len(protected),note='Brand cyan on selected opaque landmark surfaces; glass, architectural roofs, industrial roof, water and observation glass preserved. Master and v002 preserved.'),indent=2))
print('SAVED',out,'landmarks',counts,flush=True)
pref=bpy.context.preferences.addons['cycles'].preferences;pref.compute_device_type='OPTIX';pref.get_devices()
for d in pref.devices:d.use=d.type=='OPTIX'
S.render.engine='CYCLES';S.cycles.device='GPU';S.cycles.samples=40;S.cycles.use_denoising=True;S.render.use_persistent_data=True;S.render.resolution_percentage=100;S.render.resolution_x=1600;S.render.resolution_y=900;S.render.use_border=False;S.render.image_settings.file_format='PNG';S.render.image_settings.color_mode='RGB';S.render.image_settings.color_depth='8'
active=S.camera;stats=[]
def render(key):
 S.render.filepath=str(R/'review'/f'{key}.png');t=time.time();bpy.ops.render.render(write_still=True);stats.append(dict(view=key,seconds=time.time()-t))
S.frame_set(132);render('after-0132')
spec=importlib.util.spec_from_file_location('framing',R.parents[1]/'blockout/cn-shanghai-density-v001/scripts/render_review.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
S.frame_set(57);S.render.resolution_y=1000
mod.diagnostic_camera(S,'skyline',dict(bounds=[[-15,8],[17,29],[-3,23]],direction=[.35,-1,.65],margin=1.06,description='Shanghai brand accents'),1.6);render('after-skyline')
S.frame_set(315);bpy.context.view_layer.update();frame=S.objects['US_FRAME'].matrix_world.copy();inv=frame.inverted();points=[]
for rn in groups[-1][0]:
 for o in S.objects[rn].children_recursive:
  if o.type=='MESH' and not o.hide_render:points.extend(inv@o.matrix_world@Vector(c) for c in o.bound_box)
center=Vector([(min(v[a] for v in points)+max(v[a] for v in points))/2 for a in range(3)])
back=Vector((.45,-1,1.25)).normalized();right=(-back).cross(Vector((0,0,1))).normalized();up=right.cross(-back).normalized()
xs=[(v-center).dot(right) for v in points];ys=[(v-center).dot(up) for v in points];center+=right*((max(xs)+min(xs))/2)+up*((max(ys)+min(ys))/2)
data=bpy.data.cameras.new('__REVIEW_US');cam=bpy.data.objects.new('__REVIEW_US',data);S.collection.objects.link(cam);rot=Matrix((right,up,back)).transposed().to_4x4();rot.translation=center+back*260;cam.matrix_world=frame@rot;data.type='ORTHO';data.ortho_scale=max(max(xs)-min(xs),(max(ys)-min(ys))*1.6)*1.10;data.clip_end=600;S.camera=cam;render('after-usa')
for o,i,m in original_slots:o.material_slots[i].material=m
render('before-usa')
(R/'review/render.json').write_text(json.dumps(stats,indent=2))
print('REVIEW COMPLETE',flush=True)
