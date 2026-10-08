import bpy,json,sys,math
from pathlib import Path
from mathutils import Vector,Matrix
sys.path.insert(0,str(Path(__file__).resolve().parent));from scene_evidence import bounds
ROOT=Path(__file__).resolve().parents[1];S=bpy.context.scene;c=S.camera
data={'file':bpy.data.filepath,'metadata':dict(S.items()),'scene':S.name,'fps':[S.render.fps,S.render.fps_base],'range':[S.frame_start,S.frame_end],'camera':c.name,'constraints':[x.type for x in c.constraints],'camera_settings':{k:getattr(c.data,k) for k in ['type','lens','sensor_width','sensor_height','sensor_fit','shift_x','shift_y','clip_start','clip_end']},'render':{'engine':S.render.engine,'size':[S.render.resolution_x,S.render.resolution_y],'percent':S.render.resolution_percentage,'aspect':[S.render.pixel_aspect_x,S.render.pixel_aspect_y]},'guides':[{'name':o.name,'type':o.type,'hide_render':o.hide_render,'collections':[x.name for x in o.users_collection]} for o in S.objects if any(k in o.name.upper() for k in ['GUIDE','PATH','ROUTE'])],'collections':[{ 'name':o.name,'hide_render':o.hide_render} for o in bpy.data.collections],'samples':[]}
for f in [215,216,217,252,270,280,300,325,330,350,370,375,398,420,447,455,456,457]:
 S.frame_set(f);ship=bpy.data.objects['A02_SHIP'].matrix_world;local=ship.inverted()@c.matrix_world.translation
 data['samples'].append({'frame':f,'position':list(c.matrix_world.translation),'quaternion':list(c.matrix_world.to_quaternion()),'target':list(bpy.data.objects['CAM_LOOK_TARGET'].matrix_world.translation),'local_camera':list(local),'distance':local.length,'ship_bounds':bounds('A02_SHIP'),'lens':c.data.lens})
old=json.loads((ROOT.parent/'blockout-master-v004/review/states-integrated.json').read_text())
changes=[]
for f in range(217):
 S.frame_set(f)
 if [list(r) for r in c.matrix_world]!=old['frames'][f]['camera']:changes.append(f)
data['S2_camera_differences_from_prior_delivery']=changes
(ROOT/'review/baseline-inspection.json').write_text(json.dumps(data,indent=2,default=str));print(json.dumps(data,indent=2,default=str))
