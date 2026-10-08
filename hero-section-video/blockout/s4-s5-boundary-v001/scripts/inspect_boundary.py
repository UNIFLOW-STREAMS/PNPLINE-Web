import bpy,sys,json,math,argparse
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view
p=argparse.ArgumentParser();p.add_argument('--scene',required=True);p.add_argument('--output',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);s=bpy.data.scenes[a.scene];bpy.context.window.scene=s;U=bpy.data.objects['US_FRAME'].matrix_world.copy();I=U.inverted();rows=[]
names=['CAM_MASTER','CAM_LOOK_TARGET','A03_TRACTOR','A03_TRAILER','A01_CONTAINER','A01_DOOR_L','A01_DOOR_R','A02_SHIP','P02_SPREADER_FRAME','TRAILER_HITCH','TRACTOR_HITCH']
ground=[]
for name in ['US_QUAY','US_LAND_TERRACE','E07_INBOUND_ROAD']:
 o=bpy.data.objects[name];ground.append((name,BVHTree.FromPolygons([I@o.matrix_world@v.co for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons])))
for j in range(588*4,732*4+1):
 f=j/4;s.frame_set(math.floor(f),subframe=f%1);row=dict(frame=f,objects={})
 for name in names:
  o=bpy.data.objects[name];m=I@o.matrix_world;row['objects'][name]=dict(p=list(m.translation),matrix=[list(r) for r in m],quaternion=list(m.to_quaternion()),forward=list(m.to_3x3()@Vector((1,0,0))))
 row['lens']=s.camera.data.lens;row['bounds']={}
 for name in ['A03_TRACTOR','A01_CONTAINER','A02_SHIP','E08_WAREHOUSE','E07_INBOUND_ROAD']:
  o=bpy.data.objects[name];pts=[world_to_camera_view(s,s.camera,m.matrix_world@Vector(v)) for m in [o,*o.children_recursive] if m.type=='MESH' and not m.hide_render for v in m.bound_box];row['bounds'][name]=[min(p.x for p in pts),min(p.y for p in pts),max(p.x for p in pts),max(p.y for p in pts),min(p.z for p in pts)]
 row['support']=[]
 for o in s.objects:
  if '_WHEEL_' not in o.name or not o.name.startswith('A03'):continue
  center=(I@o.matrix_world).translation;bottom=min((I@o.matrix_world@v.co).z for v in o.data.vertices);hits=[(name,tree.ray_cast(center+Vector((0,0,3)),Vector((0,0,-1)),10)[0]) for name,tree in ground];hits=[(name,h.z) for name,h in hits if h is not None];g=max(hits,key=lambda x:x[1]);row['support'].append(dict(name=o.name,bottom=bottom,ground=g[0],gap=bottom-g[1]))
 rows.append(row)
out=dict(file=bpy.data.filepath,scene=s.name,blender=bpy.app.version_string,build=bpy.app.build_hash.decode(),fps=s.render.fps,range=[s.frame_start,s.frame_end],objects=len(s.objects),markers={m.name:m.frame for m in s.timeline_markers},matrix_US=[list(r) for r in U],rows=rows)
Path(a.output).write_text(json.dumps(out),encoding='utf8')
for row in rows:
 if row['frame'] in [600,608,620,632,648,649,660,672,696,720,732]:print(row['frame'],'CAM',row['objects']['CAM_MASTER']['p'],'TARGET',row['objects']['CAM_LOOK_TARGET']['p'],'lens',row['lens'],'vehicle',row['objects']['A03_TRAILER']['p'],'wheel gap',row['support'][0]['gap'])
