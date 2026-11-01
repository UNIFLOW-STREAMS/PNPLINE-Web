import sys, bpy
from pathlib import Path
from mathutils import Vector, Matrix
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R.parents[1]/'blockout/curvature-rework-v001/scripts'))
from mapping import rigid_at
s=bpy.context.scene
s.render.engine='CYCLES'
p=bpy.context.preferences.addons['cycles'].preferences
p.compute_device_type='OPTIX'; p.get_devices()
for d in p.devices:d.use=d.type=='OPTIX'
s.cycles.device='GPU' if any(d.use for d in p.devices) else 'CPU'
s.cycles.samples=24;s.cycles.use_denoising=True
s.render.resolution_percentage=100;s.render.resolution_x=1280;s.render.resolution_y=720
s.render.image_settings.file_format='PNG'
master=s.camera
cam=bpy.data.objects.new('Surface check',bpy.data.cameras.new('Surface check'))
s.collection.objects.link(cam)
which=sys.argv[sys.argv.index('--')+1:]
for arg in which:
    if arg in ('side','outlet','frontage'):
        s.frame_set(880)
        x,y,offset,scale={'side':(55,32,(16,-62,29),82),'outlet':(74,30,(21,-43,26),46),'frontage':(52,32,(7,-53,26),77)}[arg]
        anchor=Vector((x,y,.68))
        f=s.objects['US_FRAME'].matrix_world @ rigid_at(anchor,.68) @ Matrix.Translation(anchor)
        aim=f@Vector((0,0,2))
        cam.location=f@Vector(offset)
        cam.rotation_euler=(aim-cam.location).to_track_quat('-Z','Y').to_euler()
        if arg=='frontage':
            look=(Vector((0,0,6))-Vector(offset)).to_track_quat('-Z','Y')
            cam.matrix_world=f@Matrix.Translation(Vector(offset))@look.to_matrix().to_4x4()
        cam.data.type='ORTHO';cam.data.ortho_scale=scale;cam.data.clip_end=600;s.camera=cam
    else:
        s.camera=master;s.frame_set(int(arg))
    tag='before' if Path(bpy.data.filepath).stem=='before' else 'after'
    s.render.filepath=str(R/'review'/f'{tag}-{arg}.png')
    bpy.ops.render.render(write_still=True)
