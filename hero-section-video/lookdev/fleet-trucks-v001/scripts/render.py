import bpy,sys,math
from mathutils import Matrix,Vector
from pathlib import Path
R=Path(__file__).resolve().parents[1];scene=bpy.context.scene
after='fleet-trucks-v001' in bpy.data.filepath
prefix='after' if after else 'before'
def setup(s,samples=48):
    s.render.engine='CYCLES'
    p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='OPTIX';p.get_devices()
    for d in p.devices:d.use=d.type=='OPTIX'
    s.cycles.device='GPU' if any(d.use for d in p.devices) else 'CPU'
    s.cycles.samples=samples;s.cycles.use_denoising=True;s.cycles.adaptive_threshold=.03
    s.render.resolution_x=1440;s.render.resolution_y=810;s.render.resolution_percentage=100
    s.render.image_settings.file_format='PNG';s.render.image_settings.color_depth='8'
def camera(s):
    c=bpy.data.objects.new('Fleet review lens',bpy.data.cameras.new('Fleet review lens'))
    s.collection.objects.link(c);return c
def point_cam(c,origin,aim,size,space):
    rot=(Vector(aim)-Vector(origin)).to_track_quat('-Z','Y')
    c.matrix_world=space@Matrix.Translation(Vector(origin))@rot.to_matrix().to_4x4()
    c.data.type='ORTHO';c.data.ortho_scale=size;c.data.clip_start=.01;c.data.clip_end=350
def render(s,name):
    s.render.filepath=str(R/'review'/f'{prefix}-{name}.png')
    bpy.ops.render.render(write_still=True,scene=s.name)
def studio(shot):
    scene.frame_set(475)
    raw=bpy.data.scenes.new('Fleet studio '+shot)
    setup(raw,64)
    for prop in ('view_transform','look','exposure','gamma'):
        setattr(raw.view_settings,prop,getattr(scene.view_settings,prop))
    sroot=scene.objects['A03_TRACTOR' if shot.startswith('tractor') else 'A04_PRIMARY']
    objects=[o for n in (('A03_TRACTOR','A03_TRAILER','A01_CONTAINER') if shot.startswith('tractor') else ('A04_PRIMARY',)) for o in scene.objects[n].children_recursive if o.type in ('MESH','FONT') and not o.hide_render]
    inv=sroot.matrix_world.inverted();dg=bpy.context.evaluated_depsgraph_get();lowest=5.
    for o in objects:
        e=o.evaluated_get(dg);me=bpy.data.meshes.new_from_object(e,depsgraph=dg)
        du=bpy.data.objects.new(o.name+' proof',me);raw.collection.objects.link(du);du.matrix_world=inv@e.matrix_world
        if 'WHEEL' in o.name:lowest=min(lowest,min((du.matrix_world@v.co).z for v in me.vertices))
    me=bpy.data.meshes.new('Studio floor');me.from_pydata([(-70,-70,lowest-.0005),(70,-70,lowest-.0005),(70,70,lowest-.0005),(-70,70,lowest-.0005)],[],[(0,1,2,3)])
    floor=bpy.data.objects.new('Studio floor',me);raw.collection.objects.link(floor)
    mat=bpy.data.materials.new('Studio gray');mat.diffuse_color=(.19,.24,.27,1);me.materials.append(mat)
    raw.world=bpy.data.worlds.new('Studio softbox environment');raw.world.use_nodes=True
    raw.world.node_tree.nodes['Background'].inputs[0].default_value=(.65,.75,.84,1)
    raw.world.node_tree.nodes['Background'].inputs[1].default_value=.54
    for loc,power,size,color in [((3.,4.,8.),610,6.,(1,.94,.85)),((-5.,-4.,6.),550,5.,(.82,.93,1)),((2,-6,3),180,4.,(.92,.96,1))]:
        ld=bpy.data.lights.new('Studio softbox','AREA');ld.energy=power;ld.shape='DISK';ld.size=size;ld.color=color
        li=bpy.data.objects.new('Studio softbox',ld);raw.collection.objects.link(li);li.location=loc
        li.rotation_euler=(Vector((-.7,0,1.45))-Vector(loc)).to_track_quat('-Z','Y').to_euler()
    target=(-.75,0,2.03) if shot.startswith('tractor') else (0,0,1.86)
    sg=-1 if shot=='tractor-right' else 1
    cam=camera(raw);raw.camera=cam
    point_cam(cam,(3.9,sg*9,4.55),target,7.68 if shot.startswith('tractor') else 5.70,Matrix.Identity(4))
    render(raw,shot)
setup(scene);native=scene.camera;cam=camera(scene)
for shot in sys.argv[sys.argv.index('--')+1:]:
    if shot.startswith(('tractor','dispatch-product')):
        studio(shot);continue
    if shot.isdigit():scene.camera=native;scene.frame_set(int(shot))
    elif shot=='yard':
        scene.frame_set(617);scene.camera=cam
        point_cam(cam,(34,2,42),(15.7,26,2.5),35,scene.objects['US_FRAME'].matrix_world)
    elif shot=='dispatch':
        scene.frame_set(870);scene.camera=cam
        unit=scene.objects['A04_PRIMARY'];rel=unit.matrix_world.inverted()@scene.objects['A05_SECONDARY'].matrix_world.translation
        aim=(rel.x*.45,rel.y*.5,1.82)
        point_cam(cam,Vector(aim)+Vector((8,3,9)),aim,10.7,unit.matrix_world)
    render(scene,shot)
