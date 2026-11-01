import bpy,sys
from pathlib import Path
from mathutils import Matrix,Vector
R=Path(__file__).resolve().parents[1];s=bpy.context.scene
src='after' if 'pnpline-container-ship' in bpy.data.filepath else 'before'
camera=s.camera;c=bpy.data.objects.new('Review only',bpy.data.cameras.new('Review only'))
s.collection.objects.link(c);p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='OPTIX';p.get_devices()
for device in p.devices:device.use=device.type=='OPTIX'
s.render.engine='CYCLES';s.cycles.device='GPU' if any(x.use for x in p.devices) else 'CPU'
s.cycles.samples=40;s.cycles.use_denoising=True;s.cycles.adaptive_threshold=.035
s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.image_settings.color_depth='8'
for view in sys.argv[sys.argv.index('--')+1:]:
    s.render.resolution_x=1440;s.render.resolution_y=810
    if view in ('sailing','berth','broadside'):
        origin,aim,scale,frame={'sailing':((9,24,12),(.45,0,1.85),20.2,245),'berth':((8,-20,12),(.2,0,2.),20.7,60),'broadside':((2,25,5.8),(.2,0,1.8),19.9,245)}[view]
        s.frame_set(frame);s.camera=c
        rot=(Vector(aim)-Vector(origin)).to_track_quat('-Z','Y')
        c.matrix_world=s.objects['A02_SHIP'].matrix_world@Matrix.Translation(Vector(origin))@rot.to_matrix().to_4x4()
        c.data.type='ORTHO';c.data.ortho_scale=scale;c.data.clip_end=1500
    else:
        s.camera=camera;s.frame_set(int(view))
    s.render.filepath=str(R/'review'/f'{src}-{view}.png')
    bpy.ops.render.render(write_still=True)
