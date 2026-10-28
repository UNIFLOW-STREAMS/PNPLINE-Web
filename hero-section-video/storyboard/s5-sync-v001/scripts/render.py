import bpy,sys,json,uuid,datetime,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from contracts import digest,require
cfg=json.loads((R/'config.json').read_text(encoding='utf8'));sel=json.loads((R/'storyboard-selection.json').read_text(encoding='utf8'))
path=Path(bpy.data.filepath).resolve();source_sha=digest(path)
require(source_sha==sel['source_sha256'],'input does not match selection')
s=bpy.data.scenes[cfg['scene']];bpy.context.window.scene=s;require(s.camera.name==cfg['camera'],'wrong camera')
run=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid.uuid4().hex[:8]
out=R/'raw'/run;out.mkdir(exist_ok=False)
original={'resolution':[s.render.resolution_x,s.render.resolution_y,s.render.resolution_percentage],'pixel_aspect':[s.render.pixel_aspect_x,s.render.pixel_aspect_y],'engine':s.render.engine,'border':s.render.use_border,'crop':s.render.use_crop_to_border}
width=cfg['width'];height=round(width*s.render.resolution_y/s.render.resolution_x)
s.render.engine='BLENDER_WORKBENCH';s.render.resolution_x=width;s.render.resolution_y=height;s.render.resolution_percentage=100
s.render.use_border=False;s.render.use_crop_to_border=False;s.render.image_settings.file_format='PNG';s.render.film_transparent=False
s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.background_type='WORLD';s.world.color=(.18,.18,.18)
deps=[Path(__file__),R/'scripts/contracts.py',R/'config.json',R/'storyboard-selection.json',R/'inputs/source.json']
record={'schema':1,'run_id':run,'status':'rendering','started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source':{'path':str(path),'sha256':source_sha},'scene':s.name,'camera':s.camera.name,'blender':bpy.app.version_string,'blender_binary':bpy.app.binary_path,'git_head':json.loads((R/'inputs/source.json').read_text(encoding='utf8'))['git_head'],'fps':s.render.fps,'fps_base':s.render.fps_base,'preview_start':cfg['preview_start'],'frame_range':[s.frame_start,s.frame_end],'original_render':original,'render':{'engine':s.render.engine,'resolution':[width,height],'pixel_aspect':[s.render.pixel_aspect_x,s.render.pixel_aspect_y],'percentage':100,'border':False,'crop':False,'shading':'STUDIO MATERIAL shadows cavity','world_color':[.18,.18,.18]},'dependencies':{str(p):digest(p) for p in deps},'output_dir':str(out),'expected_frames':list(range(cfg['preview_start'],cfg['preview_end']+1)),'images':[]}
I=s.objects['US_FRAME'].matrix_world.inverted()
def matrix(o):return list(map(list,o.matrix_world))
def pose(n,f):
 s.frame_set(int(f),subframe=f%1);m=I@s.objects[n].matrix_world;v=m.to_3x3()@Vector((1,0,0));return {'p':list(m.translation),'yaw':math.degrees(math.atan2(v.y,v.x)),'world_matrix':matrix(s.objects[n])}
s.frame_set(900);cargo_ref=s.objects['A01_CONTAINER'].matrix_world.inverted()@s.objects['W01_NEW_PALLET'].matrix_world
def state(f):
 nearby={n:{str(d):pose(n,f+d) for d in [-1,0,1]} for n in ['A03_TRACTOR','A03_TRAILER','A01_CONTAINER','W01_NEW_PALLET','CAM_MASTER','CAM_LOOK_TARGET']}
 s.frame_set(f);t=nearby['A03_TRAILER'];vel=(Vector(t['1']['p'])-Vector(t['-1']['p']))/2;speed=vel.length;yaw=t['0']['yaw'];angle=math.radians(yaw)
 angles=[s.objects[n].rotation_euler.z for n in ['A01_DOOR_L','A01_DOOR_R']]
 rear=I@s.objects['A01_CONTAINER'].matrix_world@Vector((-1.6,0,0))
 floor=s.objects['WAREHOUSE_FLOOR'];dock_front=min((I@floor.matrix_world@Vector(c)).x for c in floor.bound_box)
 cargo=s.objects['A01_CONTAINER'].matrix_world.inverted()@s.objects['W01_NEW_PALLET'].matrix_world
 metrics={'speed':speed,'yaw':yaw,'yaw_change':((t['1']['yaw']-t['-1']['yaw']+180)%360-180)/2,'forward_dot':vel.normalized().dot(Vector((math.cos(angle),math.sin(angle),0))) if speed>.0001 else 0,'doors_closed':all(abs(a)<.001 for a in angles),'doors_open':all(abs(abs(a)-1.5*math.pi)<.001 for a in angles),'dock_gap':dock_front-rear.x,'cargo_relative_error':(cargo.translation-cargo_ref.translation).length}
 return {'neighbors':nearby,'metrics':metrics,'door_radians':angles,'dock_front_us_x':dock_front,'rear_us':list(rear),'dock_matrix':matrix(floor),'cargo_relative_matrix':list(map(list,cargo))}
rp=out/'render-record.json'
def save():rp.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf8')
save()
for f in record['expected_frames']:
 st=state(f) if f in {p['frame'] for p in sel['panels']}|{728,762,810} else None
 s.frame_set(f);p=out/f'{f:04d}.png';s.render.filepath=str(p);bpy.ops.render.render(write_still=True)
 camera={'world_matrix':matrix(s.camera),'lens_mm':s.camera.data.lens,'shift':[s.camera.data.shift_x,s.camera.data.shift_y],'sensor':[s.camera.data.sensor_width,s.camera.data.sensor_height],'type':s.camera.data.type,'clip':[s.camera.data.clip_start,s.camera.data.clip_end]}
 record['images'].append({'frame':f,'subframe':0,'source_sha256':source_sha,'scene':s.name,'camera':s.camera.name,'camera_state':camera,'path':str(p),'sha256':digest(p),'run_id':run,'state':st});save()
require(digest(path)==source_sha,'source changed during rendering')
record['status']='complete';record['completed_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save()
(R/'render-record.json').write_text(rp.read_text(encoding='utf8'),encoding='utf8')
print('COMPLETE',str(rp),flush=True)
