"""Measure reopened camera trajectories, ship framing, and horizon continuity."""
import bpy, hashlib, json, math, statistics
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];cfg=json.loads((R/'config.json').read_text());result={}
for kind,path in [('before',(R/cfg['source']).resolve()),('after',R/cfg['output'])]:
 bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;cam=s.camera;ship=s.objects['A02_SHIP'];rows=[]
 # Hull and superstructure bound the visible ship, excluding water trails.
 geometry=[o for o in ship.children_recursive if o.type=='MESH' and ('HULL' in o.name or 'BRIDGE' in o.name or 'P03_' in o.name)]
 for tick in range(200*2,366*2+1):
  f=tick/2;s.frame_set(int(f),subframe=f%1);M=ship.matrix_world;eye=cam.matrix_world.translation;q=cam.matrix_world.to_quaternion()
  up=(M.to_quaternion()@Vector((0,0,1))).normalized();screen=world_to_camera_view(s,cam,M.translation)
  pts=[world_to_camera_view(s,cam,o.matrix_world@Vector(c)) for o in geometry for c in o.bound_box]
  rows.append({'frame':f,'eye':list(eye),'q':list(q),'ship':list(M.translation),'relative_eye':list(M.inverted()@eye),
   'screen':list(screen),'bounds':[min(p.x for p in pts),min(p.y for p in pts),max(p.x for p in pts),max(p.y for p in pts)],
   'roll':math.degrees(math.atan2(up.dot(q@Vector((1,0,0))),up.dot(q@Vector((0,1,0)))))})
 velocities=[];angular=[]
 for a,b in zip(rows,rows[1:]):
  velocities.append([(y-x)*2 for x,y in zip(a['eye'],b['eye'])])
  angular.append(4*math.degrees(math.acos(min(1,abs(sum(x*y for x,y in zip(a['q'],b['q'])))))))
 speed=[math.sqrt(sum(x*x for x in v)) for v in velocities]
 accel=[math.dist(a,b)*2 for a,b in zip(velocities,velocities[1:])]
 core=[r for r in rows if 235<=r['frame']<=330]
 near=[i for i,r in enumerate(rows[:-1]) if 270<=r['frame']<=310]
 result[kind]={'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'rows':rows,'metrics':{
  'core_speed_min':min(v for v,r in zip(speed,rows) if 235<=r['frame']<=330),
  'core_speed_max':max(v for v,r in zip(speed,rows) if 235<=r['frame']<=330),
  'old_wait_window_speed_min':min(speed[i] for i in near),
  'peak_acceleration':max(v for v,r in zip(accel,rows) if 210<=r['frame']<=350),
  'peak_angular_deg_per_frame':max(v for v,r in zip(angular,rows) if 210<=r['frame']<=350),
  'peak_roll_deg':max(abs(r['roll']) for r in core),
  'ship_outside_frames':sorted(set(int(r['frame']) for r in core if not (0<r['screen'][0]<1 and 0<r['screen'][1]<1))),
  'ship_bounds': [min(r['bounds'][0] for r in core),min(r['bounds'][1] for r in core),max(r['bounds'][2] for r in core),max(r['bounds'][3] for r in core)],
  'longitudinal_relative_range':[min(r['relative_eye'][0] for r in core),max(r['relative_eye'][0] for r in core)]}}
 print(kind,json.dumps(result[kind]['metrics'],indent=2),flush=True)
(R/'review/motion.json').write_text(json.dumps(result,indent=2))
