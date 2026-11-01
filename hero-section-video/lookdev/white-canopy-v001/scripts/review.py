import bpy,sys
from pathlib import Path
from mathutils import Matrix,Vector
R=Path(__file__).resolve().parents[1]
s=bpy.context.scene
p=bpy.context.preferences.addons['cycles'].preferences
p.compute_device_type='OPTIX';p.get_devices()
for d in p.devices:d.use=d.type=='OPTIX'
s.render.engine='CYCLES';s.cycles.device='GPU' if any(d.use for d in p.devices) else 'CPU'
s.cycles.samples=40;s.cycles.use_denoising=True;s.cycles.adaptive_threshold=.03
s.render.resolution_x=1280;s.render.resolution_y=720;s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG'
native=s.camera
cam=bpy.data.objects.new('Proof camera',bpy.data.cameras.new('Proof camera'));s.collection.objects.link(cam)
def view(name,frame,unit,origin,target,width):
    s.frame_set(frame);s.camera=cam
    rot=(Vector(target)-Vector(origin)).to_track_quat('-Z','Y')
    cam.matrix_world=s.objects[unit].matrix_world@Matrix.Translation(Vector(origin))@rot.to_matrix().to_4x4()
    cam.data.type='ORTHO';cam.data.ortho_scale=width;cam.data.clip_end=1500
    s.render.filepath=str(R/'review'/(name+'.png'));bpy.ops.render.render(write_still=True)
if '--box' in sys.argv:
    s.frame_set(245)
    cargo=s.objects['A01_CONTAINER']
    center=cargo.matrix_world.inverted()@s.objects['A02_SHIP'].matrix_world.translation
    side=1 if center.y<0 else -1
    view('container-on-ship',245,'A01_CONTAINER',(2.8,side*12,4.0),(0,0,-.75),9.1)
    sys.exit(0)
view('waterfront',890,'DSP_TREE_042',(-5,-9,6),(0,0,1.40),13)
view('ship',245,'A02_SHIP',(3,25,8),(.2,0,1.9),19.9)
s.camera=native;s.frame_set(617);s.render.filepath=str(R/'review/warehouse-approach.png');bpy.ops.render.render(write_still=True)
