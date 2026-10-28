import bpy,json,sys,math,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];B=Path(bpy.data.filepath).parent;s=bpy.context.scene
sys.path.insert(0,str(R.parents[1]/'blockout/s5-dock-test-v001/scripts'));from geometry import hull,overlap,point_distance
body=[s.objects['A01_'+n] for n in ['FLOOR','ROOF','SIDE_L','SIDE_R','FRONT']]
deck=[o for o in s.objects if o.name.startswith('P03_') or o.name in ['SHIP_DECK','SHIP_BRIDGE']]
errors=[];max_overlap=0;max_spreader_gap=0;min_camera=1e9;camera_at=None
crane=[o for o in s.objects if o.type=='MESH' and o.name.startswith('P02_') and 'CABLE' not in o.name]
for j in range(216*4,624*4+1):
 f=j/4;s.frame_set(int(f),subframe=f%1)
 for a in body:
  for b in deck:
   d=overlap(*hull(a),*hull(b));max_overlap=max(max_overlap,d)
   if d>.01:errors.append({'frame':f,'pair':[a.name,b.name],'depth':d})
 if 532<=f<=624:
  c=s.objects['A01_CONTAINER'].matrix_world.translation;sp=s.objects['P02_SPREADER'].matrix_world.translation
  # Reference distance is constant while lifting; actual connection checked in US frame.
  local=s.objects['A01_CONTAINER'].matrix_world.inverted()@sp
  max_spreader_gap=max(max_spreader_gap,abs(local.x),abs(local.y))
 for o in crane+body+[s.objects['SHIP_HULL']]:
  d=point_distance(o,s.camera.matrix_world.translation)
  if d<min_camera:min_camera=d;camera_at=[f,o.name]
result={'pass':not errors and max_spreader_gap<.002 and min_camera>.12,'cargo_collision_errors':errors[:30],'cargo_collision_count':len(errors),'cargo_max_overlap_m':max_overlap,'spreader_xy_max_error_m':max_spreader_gap,'camera_clearance_m':min_camera,'camera_clearance_at':camera_at,'range':[216,624],'step':.25,'master_sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest()}
(B/'review/handoffs.json').write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(result),flush=True)
if not result['pass']:raise AssertionError('New handoff collision/support failed')
