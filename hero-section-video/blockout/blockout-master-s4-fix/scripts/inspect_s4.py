import bpy,json,sys
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent));from scene_evidence import capture,bounds
R=Path(__file__).resolve().parents[1];S=bpy.context.scene;C=S.camera;us=bpy.data.objects['US_FRAME'].matrix_world.copy()
data=capture();(R/'review/baseline-full.json').write_text(json.dumps(data,default=str))
old=json.loads((R.parent/'blockout-master-v005/review/states-after.json').read_text());changes={k:[f for f in range(457) if old['frames'][f][k]!=data['frames'][f][k]] for k in ['camera','target','lens','noncamera']}
samples=[]
for f in [455,456,457,476,495,510,520,531,532,540,555,580,599,615,631,632,637,642,647,648,649,668,680,696]:
 S.frame_set(f);samples.append({'frame':f,'camera_us':list(us.inverted()@C.matrix_world.translation),'target_us':list(us.inverted()@bpy.data.objects['CAM_LOOK_TARGET'].matrix_world.translation),'lens':C.data.lens,'ship_bounds':bounds('A02_SHIP'),'cargo_bounds':bounds('A01_CONTAINER'),'tractor_bounds':bounds('A03_TRACTOR'),'trailer_bounds':bounds('A03_TRAILER'),'cargo_us':list(us.inverted()@bpy.data.objects['A01_CONTAINER'].matrix_world.translation),'tractor_us':list(us.inverted()@bpy.data.objects['A03_TRACTOR'].matrix_world.translation)})
info={'file':bpy.data.filepath,'metadata':dict(S.items()),'scene':S.name,'range':[S.frame_start,S.frame_end],'fps':[S.render.fps,S.render.fps_base],'settings':{k:getattr(C.data,k) for k in ['type','sensor_width','sensor_height','sensor_fit','shift_x','shift_y','clip_start','clip_end']},'render':{'engine':S.render.engine,'size':[S.render.resolution_x,S.render.resolution_y],'percent':S.render.resolution_percentage,'pixel_aspect':[S.render.pixel_aspect_x,S.render.pixel_aspect_y]},'collections':[(c.name,c.hide_render) for c in bpy.data.collections],'prior_S2_S3_changes':changes,'samples':samples,'object_names':sorted(o.name for o in S.objects)}
(R/'review/baseline-inspection.json').write_text(json.dumps(info,indent=2,default=str));print(json.dumps({k:v for k,v in info.items() if k not in ['object_names','samples']},indent=2,default=str));print(json.dumps(samples))
