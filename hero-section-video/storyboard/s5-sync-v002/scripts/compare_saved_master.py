"""Read-only comparison of the rendered snapshot and current S5 master."""
import bpy, json, hashlib, math
from pathlib import Path
from mathutils import Vector
B=Path(__file__).resolve().parents[1]
old=B.parent/'s5-sync-v001/master/source-current.blend'
current=B.parents[1]/'blockout/s5-integration-v001/master-s5-integration-v001.blend'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def inspect(path):
 bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene
 names=sorted(o.name for o in s.objects)
 scene={'frame_current':s.frame_current,'range':[s.frame_start,s.frame_end],'fps':[s.render.fps,s.render.fps_base],'camera':s.camera.name,'objects':len(names),'markers':{m.name:m.frame for m in s.timeline_markers}}
 geom=hashlib.sha256()
 for name in names:
  o=s.objects[name];geom.update(repr((o.name,o.type,o.parent.name if o.parent else None,o.hide_render)).encode())
  if o.type=='MESH':
   for v in o.data.vertices:geom.update(bytes(f'{v.co.x:.7f},{v.co.y:.7f},{v.co.z:.7f};','ascii'))
   for p in o.data.polygons:geom.update(bytes(str(tuple(p.vertices)),'ascii'))
 camera=[]; transforms=[]; lenses=[]
 for frame in range(624,949):
  s.frame_set(frame)
  camera.append(tuple(round(x,6) for row in s.camera.matrix_world for x in row))
  lenses.append((round(s.camera.data.lens,6),round(s.camera.data.shift_x,6),round(s.camera.data.shift_y,6)))
  transforms.append(tuple((name,tuple(round(x,5) for row in s.objects[name].matrix_world for x in row)) for name in names))
 return {'path':str(path),'sha256':sha(path),'scene':scene,'object_names':names,'geometry_sha256':geom.hexdigest(),'camera':camera,'lens':lenses,'transforms':transforms}
a=inspect(old);b=inspect(current)
result={'old_path':a['path'],'old_sha256':a['sha256'],'current_path':b['path'],'current_sha256':b['sha256'],'old_scene':a['scene'],'current_scene':b['scene'],'same_names':a['object_names']==b['object_names'],'same_geometry':a['geometry_sha256']==b['geometry_sha256'],'same_camera_all_325':a['camera']==b['camera'],'same_lens_all_325':a['lens']==b['lens'],'same_object_world_matrices_all_325':a['transforms']==b['transforms'],'differing_frames':[624+i for i,(x,y) in enumerate(zip(a['transforms'],b['transforms'])) if x!=y][:10]}
result['motion_camera_equivalent_for_preview']=all([result['same_names'],result['same_geometry'],result['same_camera_all_325'],result['same_lens_all_325'],result['same_object_world_matrices_all_325']])
(B/'review/current-master-comparison.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k not in ('old_scene','current_scene')},ensure_ascii=False),flush=True)
