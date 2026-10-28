import bpy,json,hashlib,ast
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];candidate=Path(bpy.data.filepath);version=candidate.stem.rsplit('-',1)[-1];s=bpy.context.scene;s.frame_set(156)
report=json.loads((R/f'review/crane-style-proposal-{version}.json').read_text());allowed=set(report['hidden_original_crane_visuals']);moved={p['name']for p in report['relocated_houses']+report['relocated_trees']}
t=ast.parse((R/'scripts/verify_na_district.py').read_text());func=next(n for n in t.body if isinstance(n,ast.FunctionDef)and n.name=='capture')
source=ast.unparse(func).replace("'na_district_owner'","'crane_revision_owner'")
source=source.replace("'matrix': list(map(list, o.matrix_basis))","'matrix': None if o.name in moved else list(map(list, o.matrix_basis))")
exec(source)
after,aa=capture();D=s.objects['SF_CN_LAYOUT'];DI=D.matrix_world.inverted();DM=D.matrix_world;land=s.objects['SF_FRONT_LAND'];LI=land.matrix_world.inverted();down=(LI.to_3x3()@DM.to_3x3()@Vector((0,0,-1))).normalized()
support_fail=[];leg_fail=[]
for o in s.objects:
 if o.name.startswith('CR_FOOT_'):
  pts=[DI@o.matrix_world@v.co for v in o.data.vertices]
  for p in pts:
   if abs(p.z-1.25)<.001 and not land.ray_cast(LI@(DM@(p+Vector((0,0,1)))),down)[0]:support_fail.append(o.name)
 if o.name.startswith('CR_LEG_'):
  pts=[DI@o.matrix_world@v.co for v in o.data.vertices]
  if abs(min(p.z for p in pts)-1.41)>.001 or abs(max(p.z for p in pts)-6.5)>.001:leg_fail.append(o.name)
bpy.ops.wm.open_mainfile(filepath=str(R/'review/layout-proposal-v017.blend'));bpy.context.scene.frame_set(156);before,ba=capture();changed=[k for k in before.keys()|after.keys()if before.get(k)!=after.get(k)]
checks={'four_grounded_feet':not support_fail,'vertical_legs_reach_horizontal_beam':not leg_fail,'no_pier_inside_houses':not report['support_building_overlaps'],'only_documented_original_changes':not changed,'all_48_animation_actions_unchanged':aa==ba}
result={'candidate':str(candidate),'sha256':hashlib.sha256(candidate.read_bytes()).hexdigest(),'static_checks':checks,'unexpected_changes':changed,'relocated_houses':report['relocated_houses'],'relocated_trees':report['relocated_trees'],'actions_checked':len(ba),'original_objects_checked':len(before),'animation_ready':False,'reason':'Original hoist is higher than reference-matched beam in initial lift and parked pose. This is a static review proposal.'}
(R/f'review/crane-verified-{version}.json').write_text(json.dumps(result,indent=2));print(json.dumps(result));assert all(checks.values())
