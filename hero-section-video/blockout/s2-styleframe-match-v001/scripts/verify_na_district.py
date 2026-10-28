"""Reopen candidate; check actual support/clearances and protected original data."""
import bpy,math,json,hashlib,sys
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;s.frame_set(156);candidate=Path(bpy.data.filepath)
version=candidate.stem.rsplit('-',1)[-1];build=json.loads((R/f'review/na-district-build-{version}.json').read_text());allowed=set(build['hidden_original_objects'])
def capture():
 data={}
 for o in bpy.data.objects:
  if o.get('na_district_owner'):continue
  row={'parent':o.parent.name if o.parent else None,'matrix':list(map(list,o.matrix_basis)),'hide':None if o.name in allowed else o.hide_render,'materials':[m.name if m else None for m in o.data.materials]if hasattr(o.data,'materials')else []}
  if o.type=='MESH':row['vertices']=[list(v.co)for v in o.data.vertices];row['polygons']=[list(p.vertices)for p in o.data.polygons]
  elif o.type=='CURVE':row['curves']=[[[*p.co]for p in sp.points]for sp in o.data.splines];row['bevel']=o.data.bevel_depth
  elif o.type=='CAMERA':row['lens']=o.data.lens;row['shift']=[o.data.shift_x,o.data.shift_y]
  data[o.name]=hashlib.sha256(json.dumps(row,sort_keys=True).encode()).hexdigest()
 actions={a.name:[[fc.data_path,fc.array_index,[[list(k.co),list(k.handle_left),list(k.handle_right),k.interpolation]for k in fc.keyframe_points]]for l in a.layers for st in l.strips for bag in st.channelbags for fc in bag.fcurves]for a in bpy.data.actions}
 return data,actions
after,aa=capture();D=s.objects['SF_CN_LAYOUT'];DM=D.matrix_world;DI=DM.inverted();land=s.objects['SF_FRONT_LAND'];LI=land.matrix_world.inverted();down=(LI.to_3x3()@DM.to_3x3()@Vector((0,0,-1))).normalized()
def supported(x,y):return land.ray_cast(LI@(DM@Vector((x,y,5))),down)[0]
def overlap(a,b):
 for poly in (a,b):
  for j,p in enumerate(poly):
   e=poly[(j+1)%4]-p;axis=Vector((-e.y,e.x)).normalized();aa=[p.dot(axis)for p in a];bb=[p.dot(axis)for p in b]
   if max(aa)<min(bb) or max(bb)<min(aa):return False
 return True
roots=[o for o in s.objects if o.get('na_district_owner')and 'footprint'in o];polys={o.name:[Vector(tuple(o['footprint'][j:j+2]))for j in range(0,8,2)]for o in roots}
unsupported=[n for n,p in polys.items()if not all(supported(q.x,q.y)for q in p+[(p[j]+p[(j+1)%4])/2 for j in range(4)])]
overlaps=[(a,b)for i,a in enumerate(polys)for b in list(polys)[i+1:]if overlap(polys[a],polys[b])]
wheel_errors=[]
for o in s.objects:
 if o.name.startswith('NA_TRUCK_WHEEL'):
  p=DI@o.matrix_world.translation
  if not supported(p.x,p.y)or abs(p.z-.17-1.25)>.005:wheel_errors.append(o.name)
houses=[o for o in roots if o.get('role')=='village_house'];halls=[o for o in roots if o.get('role')=='harbor_hall']
# Density and extension guard: enough individual houses, including the NA-side bend.
na_houses=[o.name for o in houses if o.location.x>3 and o.location.y>7]
checks={'at_least_24_low_houses':len(houses)>=24,'two_detailed_harbor_halls':len(halls)==2,'village_extends_towards_NA':len(na_houses)>=5,'grounded_roof_footprints':not unsupported,'nonoverlapping_buildings':not overlaps,'truck_wheel_contact':not wheel_errors,'old_proxy_roofs_hidden':all(s.objects[n].hide_render for n in allowed)}
bpy.ops.wm.open_mainfile(filepath=str(R/'review/layout-proposal-v014.blend'));bpy.context.scene.frame_set(156);before,ba=capture()
changed=[k for k in before.keys()|after.keys()if before.get(k)!=after.get(k)]
checks['original_objects_preserved']=not changed;checks['animation_actions_unchanged']=aa==ba
result={'candidate':str(candidate),'sha256':hashlib.sha256(candidate.read_bytes()).hexdigest(),'checks':checks,'houses':len(houses),'halls':len(halls),'NA_bend_houses':na_houses,'unsupported':unsupported,'overlaps':overlaps,'wheel_errors':wheel_errors,'changed_originals':changed,'original_objects_checked':len(before),'actions_checked':len(ba),'scope':'Static NA district. Support and footprint tests are not continuous animation collision certification.'}
(R/f'review/na-district-verified-{version}.json').write_text(json.dumps(result,indent=2));print(json.dumps(result));assert all(checks.values())
