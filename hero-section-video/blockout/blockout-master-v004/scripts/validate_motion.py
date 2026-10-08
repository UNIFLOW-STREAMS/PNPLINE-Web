import bpy,json,math,sys
from pathlib import Path
from mathutils import Vector,Matrix
sys.path.insert(0,str(Path(__file__).resolve().parent))
from scene_evidence import capture,bounds
ROOT=Path(__file__).resolve().parents[1];S=bpy.context.scene;cam=S.camera
mode=sys.argv[sys.argv.index('--')+1]
data=capture();(ROOT/'review'/('states-'+mode+'.json')).write_text(json.dumps(data,default=str))
rows=[];hits=[];previous=None
meshes=[o for o in S.objects if o.type=='MESH' and o.name!='EARTH_CONTINUOUS_OCEAN' and not o.name.startswith('WAKE_')]
boxes={o.name:([min(v[i] for v in o.bound_box) for i in range(3)],[max(v[i] for v in o.bound_box) for i in range(3)]) for o in meshes}
for i in range(95*4,(254 if mode=='integrated' else 217)*4+1):
 f=i/4
 if mode=='candidate' and f>216:break
 S.frame_set(int(f),subframe=f-int(f));p=cam.matrix_world.translation.copy();q=cam.matrix_world.to_quaternion();t=bpy.data.objects['CAM_LOOK_TARGET'].matrix_world.translation.copy();ship=bpy.data.objects['A02_SHIP'].matrix_world.copy()
 local=ship.inverted()@p;up=ship.to_3x3()@Vector((0,0,1));forward=cam.matrix_world.to_3x3()@Vector((0,0,-1));right=cam.matrix_world.to_3x3()@Vector((1,0,0))
 row={'frame':f,'position':list(p),'quaternion':list(q),'target':list(t),'lens':cam.data.lens,'ship_local_camera':list(local),'globe_clearance':p.length-S['radius'],'elevation_deg':math.degrees(math.asin(-forward.dot(up.normalized()))),'right_up_dot':right.dot(up.normalized())}
 if previous:
  row.update(step_per_frame=(p-previous[0]).length*4,angle_deg_per_frame=math.degrees(q.rotation_difference(previous[1]).angle)*4,target_step_per_frame=(t-previous[2]).length*4)
 rows.append(row);previous=(p,q,t)
 for o in meshes:
  if o.hide_render:continue
  v=o.matrix_world.inverted()@p;lo,hi=boxes[o.name];scale=o.matrix_world.to_scale()
  margin=[.12/max(abs(scale[j]),1e-8) for j in range(3)]
  if all(lo[j]-margin[j]<v[j]<hi[j]+margin[j] for j in range(3)):hits.append({'frame':f,'object':o.name})
obs=[]
for f in [96,124,148,180,216]:
 S.frame_set(f);sm=bpy.data.objects['A02_SHIP'].matrix_world;local=sm.inverted()@cam.matrix_world.translation
 obs.append({'frame':f,'ship_bounds':bounds('A02_SHIP'),'hero_bounds':bounds('A01_CONTAINER'),'ship_local_camera':list(local),'distance':local.length,'lens':cam.data.lens,'stern_face_frontfacing':local.x<-7,'seaside_face_frontfacing':local.y<-2.6})
result={'mode':mode,'sample_interval_frames':.25,'samples':rows,'obb_hits':hits,'observations':obs,'clip':[cam.data.clip_start,cam.data.clip_end],'limits':'Camera point plus 0.12m against world-scale-corrected object OBBs; not exact mesh or swept-volume collision. Screen bounds include occluded vertices. Historical candidate excludes unjoined f216->217; integrated covers through f254.'}
(ROOT/'review'/('motion-'+mode+'.json')).write_text(json.dumps(result,indent=2))
print(mode,'hits',len(hits),'maxStep',max(r.get('step_per_frame',0) for r in rows),'maxAngle',max(r.get('angle_deg_per_frame',0) for r in rows))
assert not hits,hits[:10]
