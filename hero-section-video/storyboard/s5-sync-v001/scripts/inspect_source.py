import bpy,sys,json,hashlib,math,runpy
import numpy as np
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];repo=R.parents[2];S2=repo/'hero-section-video/blockout/s5-integration-v001'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def describe(path):
 bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;objs=sorted(s.objects,key=lambda o:o.name)
 initial={'frame':s.frame_current,'range':[s.frame_start,s.frame_end],'fps':s.render.fps,'fps_base':s.render.fps_base,'camera':s.camera.name,'scene':s.name,'resolution':[s.render.resolution_x,s.render.resolution_y,s.render.resolution_percentage],'pixel_aspect':[s.render.pixel_aspect_x,s.render.pixel_aspect_y],'engine':s.render.engine,'markers':{m.name:m.frame for m in s.timeline_markers}}
 h=hashlib.sha256()
 for j in range(1392*4+1):
  s.frame_set(j//4,subframe=j%4/4);h.update(np.array([list(map(list,o.matrix_world)) for o in objs],dtype=np.float32).tobytes());h.update(np.array([s.camera.data.lens,s.camera.data.shift_x,s.camera.data.shift_y,s.camera.data.sensor_width,s.camera.data.sensor_height],dtype=np.float32).tobytes())
 geom=hashlib.sha256()
 for o in objs:
  geom.update(o.name.encode());geom.update(str((o.type,o.parent.name if o.parent else None,o.hide_render)).encode())
  if o.type=='MESH':
   geom.update(np.array([list(v.co) for v in o.data.vertices],dtype=np.float32).tobytes());geom.update(str([list(p.vertices) for p in o.data.polygons]).encode())
 return {'path':str(path),'sha256':sha(path),'saved_settings':initial,'evaluated_sha256':h.hexdigest(),'geometry_sha256':geom.hexdigest(),'objects':len(objs),'samples':5569,'step':.25}
old=describe(R/'inputs/committed-stage2.blend');new=describe(R/'master/source-current.blend')
comparison={'committed':old,'current':new,'motion_camera_equal':old['evaluated_sha256']==new['evaluated_sha256'],'geometry_equal':old['geometry_sha256']==new['geometry_sha256']}
(R/'review/source-comparison.json').write_text(json.dumps(comparison,indent=2),encoding='utf8');print('COMPARISON',json.dumps(comparison),flush=True)
s=bpy.context.scene;I=s.objects['US_FRAME'].matrix_world.inverted()
def pose(n,f):
 s.frame_set(int(f),subframe=f%1);m=I@s.objects[n].matrix_world;v=m.to_3x3()@Vector((1,0,0));return {'p':list(m.translation),'yaw':math.degrees(math.atan2(v.y,v.x)),'matrix':list(map(list,s.objects[n].matrix_world))}
probe=[]
for f in [648,660,672,696,720,724,728,732,736,740,752,762,766,780,800,809,810,811,842,848,849,870,890,900,912,924,948]:
 states={n:{str(d):pose(n,f+d) for d in [-1,0,1]} for n in ['A03_TRACTOR','A03_TRAILER','A01_CONTAINER','W01_NEW_PALLET','CAM_MASTER','CAM_LOOK_TARGET']}
 s.frame_set(f)
 probe.append({'frame':f,'objects':states,'door_z':[s.objects[n].rotation_euler.z for n in ['A01_DOOR_L','A01_DOOR_R']],'lens':s.camera.data.lens,'camera_type':s.camera.data.type,'freestyle_available':hasattr(s.render,'use_freestyle')})
(R/'review/state-probe.json').write_text(json.dumps(probe,indent=2),encoding='utf8')
sys.path.insert(0,str(repo/'hero-section-video/blockout/s5-dock-test-v001/scripts'))
deps={}
for name in ['master_regression.py','wheel_regression.py','integration.py']:
 p=S2/'tests'/name;deps[str(p)]=sha(p)
 print('REGRESSION_START',name,flush=True)
 exec(compile(p.read_text(encoding='utf8'),str(p),'exec'),{'__name__':'__main__','__file__':str(R/'tests'/name)})
deps[str(repo/'hero-section-video/blockout/s5-dock-test-v001/scripts/geometry.py')]=sha(repo/'hero-section-video/blockout/s5-dock-test-v001/scripts/geometry.py')
(R/'review/regression-dependencies.json').write_text(json.dumps(deps,indent=2),encoding='utf8')
assert comparison['motion_camera_equal'] and comparison['geometry_equal'],'Source has substantive changes; investigate'
