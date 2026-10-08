"""Read-only saved-scene survey; never imports the destructive master builder."""
import argparse,bpy,json,sys,math
from pathlib import Path
from mathutils import Vector
p=argparse.ArgumentParser();p.add_argument('--output-dir',type=Path,required=True)
args=p.parse_args(sys.argv[sys.argv.index('--')+1:]);out=args.output_dir;out.mkdir(parents=True,exist_ok=True)
s=bpy.context.scene;u=bpy.data.objects['US_FRAME'].matrix_world.copy();inv=u.inverted()
def matrix(m):return [list(row) for row in m]
inventory=[]
for o in s.objects:
 inventory.append({'name':o.name,'type':o.type,'parent':o.parent.name if o.parent else None,'data':o.data.name if o.data else None,'action':o.animation_data.action.name if o.animation_data and o.animation_data.action else None,'nla':len(o.animation_data.nla_tracks) if o.animation_data else 0,'drivers':len(o.animation_data.drivers) if o.animation_data else 0,'constraints':[(c.name,c.type) for c in o.constraints],'collections':[c.name for c in o.users_collection],'properties':dict(o.items()),'hidden':[o.hide_render,o.hide_viewport,o.hide_get()]})
roots=['A03_TRAILER','A03_TRACTOR','A01_CONTAINER','A01_DOOR_L','A01_DOOR_R','TRAILER_HITCH','TRACTOR_HITCH','DOCK_TARGET','W01_NEW_PALLET','W01_REMAINING_CONTAINER_CARGO','CAM_MASTER','CAM_LOOK_TARGET']
motion=[]
for i in range(648*4,900*4+1):
 f=i/4;s.frame_set(int(f),subframe=f-int(f));row={'frame':f,'objects':{}}
 for n in roots:
  o=bpy.data.objects[n];m=inv@o.matrix_world;row['objects'][n]={'matrix':matrix(m),'p':list(m.translation),'forward':list((m.to_3x3()@Vector((1,0,0))).normalized()),'rotation_euler':list(o.rotation_euler)}
 motion.append(row)
s.frame_set(890)
meshes={}
for o in s.objects:
 if o.type=='MESH' and (o.name.startswith(('A01_','A03_','TRAILER_','TRACTOR_','WAREHOUSE_','DOCK_','E09_','RACK_')) or o.name=='US_PORT_GROUND'):
  pts=[inv@o.matrix_world@Vector(v) for v in o.bound_box];meshes[o.name]={'lo':[min(v[i] for v in pts) for i in range(3)],'hi':[max(v[i] for v in pts) for i in range(3)],'verts':len(o.data.vertices),'polygons':len(o.data.polygons)}
data={'file':bpy.data.filepath,'scene':s.name,'scenes':[q.name for q in bpy.data.scenes],'blender':bpy.app.version_string,'build_hash':bpy.app.build_hash.decode(),'fps':[s.render.fps,s.render.fps_base],'range':[s.frame_start,s.frame_end],'markers':{m.name:m.frame for m in s.timeline_markers},'camera':s.camera.name,'us_matrix':matrix(u),'objects':inventory,'motion':motion,'mesh_bounds_at_890':meshes,'metadata':dict(s.items())}
(out/'baseline-survey.json').write_text(json.dumps(data,indent=2,default=str),encoding='utf-8')
print('Scene',s.name,'objects',len(inventory),'frames',len(motion),'FPS',s.render.fps)
print('Animated',[(o['name'],o['action']) for o in inventory if o['action'] and o['name'] in roots])
print('References',[(o['name'],o['nla'],o['drivers'],o['constraints']) for o in inventory if o['nla'] or o['drivers'] or o['constraints']])
for f in [648,720,760,790,810,842,849,890,900]:
 row=next(r for r in motion if r['frame']==f)
 print(f,{n:{'p':[round(x,4) for x in row['objects'][n]['p']],'fwd':[round(x,3) for x in row['objects'][n]['forward']]} for n in ['A03_TRAILER','A03_TRACTOR','DOCK_TARGET']})
