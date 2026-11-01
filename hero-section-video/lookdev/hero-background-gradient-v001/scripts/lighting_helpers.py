import bpy, sys, json, hashlib, time, math
from pathlib import Path
from mathutils import Vector, Matrix
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path('F:/pnpline-landing/hero-section-video/lookdev/hero-material-v001/pnpline-hero-material-v001.blend')
OUTPUT = ROOT / 'pnpline-hero-lighting-daylight-v002.blend'
FRAMES = [110, 332, 720, 820]
S = bpy.context.scene

def digest(path):
    with open(path, 'rb') as f: return hashlib.file_digest(f, 'sha256').hexdigest()

def clean(v):
    if isinstance(v, float): return round(v, 7)
    if isinstance(v, (str, int, bool)) or v is None: return v
    if isinstance(v, bpy.types.ID): return [v.bl_rna.identifier,v.name]
    try: return [clean(x) for x in v]
    except TypeError: return str(v)

def hashed(v): return hashlib.sha256(json.dumps(v, sort_keys=True, ensure_ascii=True).encode()).hexdigest()

def snapshot():
    opened = S.frame_current
    S.frame_set(0)
    objs = {}
    for o in S.objects:
        if o.type == 'LIGHT': continue
        objs[o.name] = [o.type, o.data.name if o.data else None, o.parent.name if o.parent else None,
            clean(o.matrix_basis), clean(o.matrix_parent_inverse), o.hide_render,
            [(x.name, x.link, x.material.name if x.material else None) for x in o.material_slots],
            [(c.name,c.type,c.influence,c.mute) for c in o.constraints],
            [(m.name,m.type,m.show_render) for m in o.modifiers]]
    meshes = {}
    for m in bpy.data.meshes:
        h = hashlib.sha256()
        for coll, attr, n, dtype in [(m.vertices,'co',3,np.float32),(m.loops,'vertex_index',1,np.int32),
                                    (m.polygons,'loop_total',1,np.int32),(m.polygons,'material_index',1,np.int32)]:
            a=np.empty(len(coll)*n,dtype=dtype); coll.foreach_get(attr,a); h.update(a.tobytes())
        meshes[m.name] = h.hexdigest()
    def tree(t):
        return {'nodes':[(n.name,n.bl_idname,[(i.identifier,clean(i.default_value)) for i in n.inputs if hasattr(i,'default_value')],
                        [(k,clean(getattr(n,k))) for k in ('operation','blend_type','distribution','node_tree') if hasattr(n,k)]) for n in t.nodes],
                'links':[(l.from_node.name,l.from_socket.identifier,l.to_node.name,l.to_socket.identifier) for l in t.links]}
    mats={m.name:tree(m.node_tree) if m.node_tree else clean(m.diffuse_color) for m in bpy.data.materials}
    acts={}
    for a in bpy.data.actions:
        curves=[]
        for layer in a.layers:
            for strip in layer.strips:
                for bag in strip.channelbags:
                    for fc in bag.fcurves:
                        curves.append([fc.data_path,fc.array_index,fc.extrapolation,
                            [(clean(k.co),clean(k.handle_left),clean(k.handle_right),k.interpolation,k.handle_left_type,k.handle_right_type) for k in fc.keyframe_points]])
        acts[a.name]=curves
    cams={c.name:[(k,clean(getattr(c,k))) for k in ('type','lens','sensor_width','sensor_height','sensor_fit','clip_start','clip_end','shift_x','shift_y','ortho_scale')]+ [('dof',c.dof.use_dof,c.dof.focus_distance,c.dof.aperture_fstop)] for c in bpy.data.cameras}
    scene={'camera':S.camera.name,'start':S.frame_start,'end':S.frame_end,'fps':S.render.fps,
           'markers':[(m.name,m.frame) for m in S.timeline_markers],
           'color':[S.view_settings.view_transform,S.view_settings.look,S.view_settings.exposure,S.view_settings.gamma]}
    result={k:{'count':len(v),'sha256':hashed(v)} for k,v in [('objects',objs),('meshes',meshes),('materials',mats),('actions',acts),('cameras',cams)]}
    result['scene']=scene
    S.frame_set(opened)
    return result

def light_record():
    return [{ 'name':o.name,'power':o.data.energy,'shape':getattr(o.data,'shape',None),
        'size':getattr(o.data,'size',None),'size_y':getattr(o.data,'size_y',None),
        'color':clean(o.data.color),'location':clean(o.matrix_world.translation),
        'parent':o.parent.name if o.parent else None} for o in S.objects if o.type=='LIGHT']

def apply():
    bg=S.world.node_tree.nodes['Background']
    bg.inputs['Strength'].default_value=.12
    bg.inputs['Color'].default_value=(.82,.86,.90,1)
    for name,power,size,color in [('LD_CN_KEY',420000,45,(1,.96,.90)),('LD_CN_FILL',18000,115,(.90,.95,1)),
                                ('LD_US_KEY',520000,50,(1,.96,.90)),('LD_US_RIM',55000,80,(.90,.95,1))]:
        d=S.objects[name].data; d.energy=power; d.size=size; d.color=color
    for name,loc,target in [('LD_CN_KEY',(-200,-110,135),(-120,0,65)),('LD_US_KEY',(-10,-80,205),(80,28,125))]:
        o=S.objects[name];o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
    # Shape the cool reflection sources.
    for name in ('LD_CN_FILL','LD_US_RIM'):
        d=S.objects[name].data; d.shape='RECTANGLE'; d.size_y=d.size*.45
    for o in S.objects:
        if o.type!='LIGHT': continue
        if o.name.startswith('WH_INTERIOR_'):
            d=o.data;d.shape='RECTANGLE';d.size=4.5;d.size_y=1.2;d.energy=220;d.color=(1,.97,.92)
        elif o.name.startswith('WHE | Packing aisle light'):
            d=o.data;d.shape='RECTANGLE';d.size=4.5;d.size_y=1.2;d.energy=260;d.color=(.96,.98,1)
    # Follow the existing warehouse curvature, so the task lights stay below the roof.
    sys.path[:0]=['F:/pnpline-landing/hero-section-video/lookdev/us-warehouse-curvature-v001/scripts',
                 'F:/pnpline-landing/hero-section-video/blockout/curvature-rework-v001/scripts']
    from surface_site import sphere,basis
    col=bpy.data.collections.new('LD_DAYLIGHT_TASK_LIGHTS');S.collection.children.link(col)
    for label,pt,power in [('Pick',(50.0,32.7,7.5),450),('Pack',(56.0,32.7,7.5),550),('Dispatch',(64.0,30.3,7.5),320)]:
        p=np.array(pt);mat=Matrix(basis(sphere,p).tolist()).to_4x4();mat.translation=Vector(sphere(p))
        d=bpy.data.lights.new('LD_TASK_'+label,'AREA');d.shape='RECTANGLE';d.size=3.2;d.size_y=1.5;d.energy=power;d.color=(1,.98,.95)
        o=bpy.data.objects.new('LD_TASK_'+label,d);col.objects.link(o);o.parent=S.objects['US_FRAME'];o.matrix_basis=mat
    S['lighting_variant']='daylight-v002'
    S['lighting_source_sha256']=digest(SOURCE)
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT),compress=True)

def render(label,frames,width=960,samples=32):
    S.render.engine='CYCLES'
    pref=bpy.context.preferences.addons['cycles'].preferences;pref.compute_device_type='OPTIX';pref.get_devices()
    for d in pref.devices:d.use=d.type=='OPTIX'
    S.cycles.device='GPU';S.cycles.samples=samples;S.cycles.use_denoising=True;S.cycles.denoiser='OPENIMAGEDENOISE'
    S.cycles.seed=29;S.cycles.use_animated_seed=False;S.cycles.adaptive_min_samples=min(32,samples);S.cycles.adaptive_threshold=.02
    S.render.resolution_x=width;S.render.resolution_y=round(width*9/16);S.render.resolution_percentage=100
    S.render.use_border=False;S.render.use_persistent_data=True;S.render.image_settings.file_format='PNG'
    S.render.image_settings.color_mode='RGB';S.render.image_settings.color_depth='8';S.render.image_settings.compression=15
    dest=ROOT/'review'/label;dest.mkdir(parents=True,exist_ok=True);metrics=[]
    for f in frames:
        S.frame_set(f);S.render.filepath=str(dest/f'f{f:04d}.png');start=time.perf_counter()
        bpy.ops.render.render(write_still=True)
        rec={'frame':f,'seconds':round(time.perf_counter()-start,3),'width':width,'samples':samples,'file':S.render.filepath}
        metrics.append(rec);(dest/'metrics.json').write_text(json.dumps(metrics,indent=2))
        print('RENDER_COMPLETE',label,json.dumps(rec),flush=True)

mode=sys.argv[sys.argv.index('--')+1]
ROOT.mkdir(parents=True,exist_ok=True)
if mode=='build':
    record={'source':str(SOURCE),'sha256':digest(SOURCE),'preservation':snapshot(),'lights':light_record()}
    (ROOT/'source.json').write_text(json.dumps(record,indent=2))
    apply()
    (ROOT/'changes.json').write_text(json.dumps({'lights':light_record(),'world_strength':.12,'world_color':[.82,.86,.90]},indent=2))
    render('draft-after',[110,332,720,820],960,32)
elif mode=='before':render('before',FRAMES)
elif mode=='after':render('after',FRAMES)
elif mode=='verify':
    baseline=json.loads((ROOT/'source.json').read_text())
    current=snapshot();checks={k:hashed(baseline['preservation'][k])==hashed(current[k]) for k in current}
    checks['source_unchanged']=baseline['sha256']==digest(SOURCE)
    checks['world_strength']=abs(S.world.node_tree.nodes['Background'].inputs['Strength'].default_value-.12)<1e-6
    for name,power,size in [('LD_CN_KEY',420000,45),('LD_CN_FILL',18000,115),('LD_US_KEY',520000,50),('LD_US_RIM',55000,80)]:
        d=S.objects[name].data;checks[name]=abs(d.energy-power)<.1 and abs(d.size-size)<.001
    report={'checks':checks,'passed':all(checks.values()),'candidate_sha256':digest(OUTPUT),'candidate':str(OUTPUT),'snapshot':current,'added_lights':[o.name for o in S.objects if o.type=='LIGHT' and o.name.startswith('LD_TASK_')]}
    (ROOT/'verification.json').write_text(json.dumps(report,indent=2));print('VERIFICATION',json.dumps(report),flush=True)
    assert report['passed'],checks
elif mode=='baseline':
    record={'source':str(SOURCE),'sha256':digest(SOURCE),'preservation':snapshot(),'lights':light_record()}
    (ROOT/'source.json').write_text(json.dumps(record,indent=2))
    render('before',FRAMES)


