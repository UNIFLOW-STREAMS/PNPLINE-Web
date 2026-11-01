import bpy,sys,json,hashlib,importlib.util
from pathlib import Path
import numpy as np
import PyOpenColorIO as ocio

R=Path(__file__).resolve().parents[1]
SOURCE=Path('F:/pnpline-landing/hero-section-video/lookdev/hero-lighting-daylight-v002/pnpline-hero-lighting-daylight-v002.blend')
OUT=R/'pnpline-hero-background-gradient-v001.blend'
S=bpy.context.scene
FRAMES=[110,200,332,820,930]

def sha(p):
    with open(p,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def helpers():
    # Reuse scene fingerprinting and identical fixed-seed render settings.
    p=Path(__file__).parent/'lighting_helpers.py'
    spec=importlib.util.spec_from_file_location('lighting_helpers',p);m=importlib.util.module_from_spec(spec)
    old=sys.argv[:];sys.argv=['helpers','--','helper_only'];spec.loader.exec_module(m);sys.argv=old
    m.ROOT=R;return m

H=helpers()
def invariant():
    lights=H.light_record()
    world=[(n.name,n.bl_idname,[(i.identifier,H.clean(i.default_value)) for i in n.inputs if hasattr(i,'default_value')]) for n in S.world.node_tree.nodes]
    return {'scene':H.snapshot(),'lights':lights,'world':world}

def build():
    assert not S.compositing_node_group,'Existing compositor needs preservation'
    rec={'source':str(SOURCE),'sha256':sha(SOURCE),'invariant':invariant()}
    (R/'source.json').write_text(json.dumps(rec,indent=2))
    # Invert the exact viewing pipeline so the display-referred brief colours survive AgX + exposure.
    cfg=ocio.Config.CreateFromFile(str(Path(bpy.utils.system_resource('DATAFILES',path='colormanagement'))/'config.ocio'))
    linear=cfg.getColorSpace('scene_linear').getName()
    pipe=ocio.LegacyViewingPipeline()
    pipe.setDisplayViewTransform(ocio.DisplayViewTransform(src=linear,display='sRGB',view=S.view_settings.view_transform))
    pipe.setLooksOverride(S.view_settings.look);pipe.setLooksOverrideEnabled(True)
    scale=2**S.view_settings.exposure
    pipe.setLinearCC(ocio.MatrixTransform(matrix=[scale,0,0,0,0,scale,0,0,0,0,scale,0,0,0,0,1]))
    inverse=cfg.getProcessor(pipe.getProcessor(cfg).createGroupTransform(),ocio.TRANSFORM_DIR_INVERSE).getDefaultCPUProcessor()
    w,h=1920,1080
    top=np.array([223,234,243])/255;bottom=np.array([243,246,248])/255
    t=np.linspace(0,1,h);t=t*t*(3-2*t)
    display=bottom[None,:]*(1-t[:,None])+top[None,:]*t[:,None]
    rows=np.array([inverse.applyRGB([float(x) for x in rgb]) for rgb in display],dtype=np.float32)
    pixels=np.ones((h,w,4),dtype=np.float32);pixels[:,:,:3]=rows[:,None,:]
    im=bpy.data.images.new('BG | Screen gradient - DFEAF3 to F3F6F8',width=w,height=h,alpha=True,float_buffer=True)
    im.colorspace_settings.name=linear;im.pixels.foreach_set(pixels.ravel());im.update()
    im.filepath_raw=str(R/'background-gradient-linear.exr');im.file_format='OPEN_EXR';im.save();im.pack()
    group=bpy.data.node_groups.new('BG | Screen-space gradient composite','CompositorNodeTree')
    group.interface.new_socket(name='Image',in_out='OUTPUT',socket_type='NodeSocketColor')
    nodes=group.nodes;links=group.links
    render=nodes.new('CompositorNodeRLayers');render.label='Original lighting and materials';render.location=(-450,150)
    image=nodes.new('CompositorNodeImage');image.image=im;image.label='Packed scene-linear gradient';image.location=(-650,-180)
    resize=nodes.new('CompositorNodeScale');resize.inputs['Type'].default_value='Render Size';resize.inputs['Frame Type'].default_value='Stretch';resize.location=(-400,-160)
    over=nodes.new('CompositorNodeAlphaOver');over.inputs['Factor'].default_value=1;over.location=(-120,120)
    output=nodes.new('NodeGroupOutput');output.location=(120,120)
    links.new(image.outputs['Image'],resize.inputs['Image']);links.new(resize.outputs['Image'],over.inputs['Background'])
    links.new(render.outputs['Image'],over.inputs['Foreground']);links.new(over.outputs['Image'],output.inputs['Image'])
    S.compositing_node_group=group;S.render.film_transparent=True;S.render.use_compositing=True
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=='VIEW_3D':area.spaces.active.shading.use_compositor='CAMERA'
    S['background_variant']='screen-gradient-v001';S['background_source_sha256']=rec['sha256']
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT),compress=True)
    (R/'background-settings.json').write_text(json.dumps({'top_srgb':'#DFEAF3','bottom_srgb':'#F3F6F8','mapping':'Screen coordinates, smoothstep vertical, render-size scaling','environment':'unchanged from daylight-v002','packed_image':im.name,'packed':bool(im.packed_file),'view':S.view_settings.view_transform,'look':S.view_settings.look,'exposure':S.view_settings.exposure},indent=2))
    H.render('after',[110,332],960,32)

mode=sys.argv[sys.argv.index('--')+1]
if mode=='build':build()
elif mode=='render':H.render('after',FRAMES,960,32)
elif mode=='rest':H.render('after',[200,820,930],960,32)
elif mode=='verify':
    rec=json.loads((R/'source.json').read_text());now=invariant()
    check={'source_unchanged':sha(SOURCE)==rec['sha256'],'scene_lights_world_preserved':H.hashed(now)==H.hashed(rec['invariant']),
           'gradient_packed':bool(bpy.data.images['BG | Screen gradient - DFEAF3 to F3F6F8'].packed_file),
           'compositor_present':bool(S.compositing_node_group),'transparent_film':S.render.film_transparent}
    result={'checks':check,'passed':all(check.values()),'file':str(OUT),'sha256':sha(OUT)}
    (R/'verification.json').write_text(json.dumps(result,indent=2));print('VERIFIED',result,flush=True);assert result['passed']



