import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];candidate=Path(bpy.data.filepath);version=candidate.stem.rsplit('-',1)[-1]
build=json.loads((R/f'review/c-district-build-{version}.json').read_text());hidden=set(build['hidden_original_objects'])
def capture():
 data={}
 for o in bpy.data.objects:
  if o.get('district_owner'):continue
  row={'parent':o.parent.name if o.parent else None,'matrix':list(map(list,o.matrix_basis)),'hide':None if o.name in hidden else o.hide_render}
  if o.type=='MESH':row['vertices']=[list(v.co)for v in o.data.vertices];row['polygons']=[list(p.vertices)for p in o.data.polygons]
  data[o.name]=hashlib.sha256(json.dumps(row,sort_keys=True).encode()).hexdigest()
 actions={a.name:[[fc.data_path,fc.array_index,[[list(k.co),list(k.handle_left),list(k.handle_right),k.interpolation]for k in fc.keyframe_points]]for l in a.layers for st in l.strips for bag in st.channelbags for fc in bag.fcurves]for a in bpy.data.actions}
 return data,actions
s=bpy.context.scene;s.frame_set(156);after,aa=capture();land=s.objects['SF_FRONT_LAND'];inv=land.matrix_world.inverted();D=s.objects['SF_CN_LAYOUT'];direction=(inv.to_3x3()@(D.matrix_world.to_3x3()@Vector((0,0,-1)))).normalized()
unsupported=[]
for o in s.objects:
 if o.name.startswith('DT_TRUCK_') and o.type=='EMPTY':
  for ch in o.children:
   if ch.name.startswith('DT_TRUCK_WHEEL'):
    p=ch.matrix_world.translation;local=inv@p;hit,q,_,_=land.ray_cast(local,direction)
    if not hit or abs((land.matrix_world@q-p).length-.16)>.03:unsupported.append(ch.name)
for o in s.objects:
 if o.name.startswith(('DT_GARDEN_PATH','DT_WATERFRONT_WALK')) and o.type=='MESH':
  for v in o.data.vertices:
   p=o.matrix_world@v.co;hit,*_=land.ray_cast(inv@p,direction)
   if not hit:unsupported.append(o.name);break
assert all(s.objects[n].hide_render for n in hidden)
bpy.ops.wm.open_mainfile(filepath=str(R/'review/layout-proposal-v011.blend'));bpy.context.scene.frame_set(156);before,ba=capture()
result={'candidate':str(candidate),'original_objects_checked':len(before),'changed_objects':[k for k in before.keys()|after.keys()if before.get(k)!=after.get(k)],'permitted_visibility_replacements':len(hidden),'all_actions_equal':aa==ba,'actions_checked':len(ba),'unsupported_vehicle_wheels_or_paths':unsupported,'known_limitations':'Existing global camera/whole-scene issues remain outside this district revision.'}
(R/f'review/c-district-scope-{version}.json').write_text(json.dumps(result,indent=2));print(json.dumps(result));assert not result['changed_objects'] and result['all_actions_equal'] and not unsupported
