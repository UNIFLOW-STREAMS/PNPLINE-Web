import bpy,sys,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R.parent/'s5-dock-test-v001/scripts'));from geometry import hull,overlap
s=bpy.context.scene;I=s.objects['US_FRAME'].matrix_world.inverted();maximum=(0,None);steer=(0,None);previous=None
for j in range(720*16,891*16):
 f=j/16;s.frame_set(j//16,subframe=j%16/16);m=I@s.objects['A03_TRAILER'].matrix_world;yaw=math.atan2(m[1][0],m[0][0])
 if previous is not None:
  d=abs(math.atan2(math.sin(yaw-previous),math.cos(yaw-previous)))*16*180/math.pi
  if d>maximum[0]:maximum=(d,f)
 previous=yaw
 for o in s.objects:
  if o.name.startswith('A03_TRACTOR_WHEEL_1.65') and abs(o.rotation_euler.z)*180/math.pi>steer[0]:steer=(abs(o.rotation_euler.z)*180/math.pi,(f,o.name))
print('BODY',maximum,'STEER',steer)
parts=[s.objects[n] for n in ['A01_SIDE_L','A01_SIDE_R','A01_DOOR_LEFT_LEAF','A01_DOOR_RIGHT_LEAF','TRAILER_CHASSIS']];walls=[s.objects[n] for n in ['DOCK_BRIDGE','WAREHOUSE_FLOOR']];results={}
for label in ['dock-before','dock-proposal']:
 if label=='dock-proposal':
  bridge=s.objects['DOCK_BRIDGE'];bridge.scale.y*=1.34/1.48;bridge.location.z=1.88
  for n in ['A01_DOOR_LEFT_LEAF','A01_DOOR_RIGHT_LEAF']:
   o=s.objects[n];o.scale.z*=1.43/1.5;o.location.z+=.035
 maxima={}
 for j in range(810*4,949*4):
  s.frame_set(j//4,subframe=j%4/4)
  for x in parts:
   for y in walls:
    key=x.name+'/'+y.name;maxima[key]=max(maxima.get(key,0),overlap(*hull(x),*hull(y)))
 results[label]=maxima;s.frame_set(890);U=s.objects['US_FRAME'].matrix_world
 if label=='dock-before':
  data=bpy.data.cameras.new('INSPECT_DOCK');cam=bpy.data.objects.new('INSPECT_DOCK',data);s.collection.objects.link(cam);data.lens=56;s.camera=cam
 p=Vector((38,26,3.9));t=Vector((35.95,29,1.94));cam.location=U@p;cam.rotation_mode='QUATERNION';cam.rotation_quaternion=U.to_quaternion()@(t-p).to_track_quat('-Z','Y')
 s.render.engine='BLENDER_WORKBENCH';s.render.resolution_x=960;s.render.resolution_y=640;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.filepath=str(R/'review'/f'{label}.png');bpy.ops.render.render(write_still=True)
(R/'review/dock-proposal.json').write_text(json.dumps(results,indent=2));print(json.dumps(results,indent=2))
